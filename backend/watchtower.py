#!/usr/bin/env python3
"""
WATCHTOWER v2.0 - DNSTwist-style CT Log Monitor
================================================
Part of Project SCAM-KILLER

Monitors Certificate Transparency logs in real-time and detects phishing
domains using dnstwist-style fuzzing algorithms.

Features:
- Real-time CT log monitoring via certstream
- DNSTwist-style domain permutation matching
- Live statistics and detection counter
- Export to JSON/CSV
- Integration with Hunter Bot for automated investigation

Usage:
    python watchtower.py                    # Monitor mode
    python watchtower.py --generate kbank   # Generate permutations only
    python watchtower.py --test             # Test with sample domains
"""

import certstream
import json
import re
import logging
import sys
import os
import csv
import argparse
from datetime import datetime
from typing import List, Set, Dict, Optional, Tuple, Generator
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import threading
import time

# Logging setup - ASCII only for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('WATCHTOWER')


# ============================================================================
# DNSTWIST-STYLE FUZZER ENGINE
# ============================================================================

class DomainFuzzer:
    """
    DNSTwist-inspired domain permutation generator.
    Generates all possible typosquatting variations of a target domain.
    """
    
    # QWERTY keyboard layout for typo simulation
    QWERTY = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4',
        '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6ygfr5',
        'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsz', 's': 'edxzaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft',
        'h': 'ujnbgy', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn',
        'n': 'bhjm', 'm': 'njk'
    }
    
    # ASCII homoglyphs (look-alike characters)
    HOMOGLYPHS = {
        '0': ['o'],
        '1': ['l', 'i'],
        '3': ['8'],
        '6': ['9'],
        '8': ['3'],
        '9': ['6'],
        'a': ['4', '@'],
        'b': ['d', '6'],
        'c': ['e', '('],
        'd': ['b', 'cl'],
        'e': ['3', 'c'],
        'g': ['q', '9'],
        'h': ['n'],
        'i': ['1', 'l', '!'],
        'k': ['lc'],
        'l': ['1', 'i', '|'],
        'm': ['n', 'nn', 'rn'],
        'n': ['m', 'r'],
        'o': ['0'],
        'q': ['g'],
        'r': ['n'],
        's': ['5', '$'],
        't': ['7', '+'],
        'u': ['v'],
        'v': ['u'],
        'w': ['vv'],
        'rn': ['m'],
        'cl': ['d'],
    }
    
    # Common phishing additions
    ADDITIONS = [
        'secure', 'login', 'signin', 'verify', 'update', 'confirm',
        'account', 'online', 'mobile', 'app', 'auth', 'portal',
        'service', 'support', 'help', 'official', 'real', 'true',
        'thailand', 'thai', 'th', 'bkk'
    ]
    
    def __init__(self, domain: str):
        """Initialize with a target domain (without TLD)."""
        self.domain = domain.lower().strip()
        self.permutations: Set[Tuple[str, str]] = set()  # (domain, fuzzer_type)
    
    def _bitsquatting(self) -> Generator[str, None, None]:
        """Generate bitsquatting variations (single bit flips)."""
        masks = [1, 2, 4, 8, 16, 32, 64, 128]
        chars = set('abcdefghijklmnopqrstuvwxyz0123456789-')
        for i, c in enumerate(self.domain):
            for mask in masks:
                b = chr(ord(c) ^ mask)
                if b in chars:
                    yield self.domain[:i] + b + self.domain[i+1:]
    
    def _homoglyph(self) -> Generator[str, None, None]:
        """Generate homoglyph variations (look-alike characters)."""
        for i, c in enumerate(self.domain):
            for g in self.HOMOGLYPHS.get(c, []):
                yield self.domain[:i] + g + self.domain[i+1:]
        # Two-character homoglyphs
        for i in range(len(self.domain) - 1):
            pair = self.domain[i:i+2]
            for g in self.HOMOGLYPHS.get(pair, []):
                yield self.domain[:i] + g + self.domain[i+2:]
    
    def _hyphenation(self) -> Generator[str, None, None]:
        """Generate hyphenated variations."""
        for i in range(1, len(self.domain)):
            yield self.domain[:i] + '-' + self.domain[i:]
    
    def _insertion(self) -> Generator[str, None, None]:
        """Generate insertion variations (extra characters)."""
        for i in range(len(self.domain)):
            c = self.domain[i]
            for ins in self.QWERTY.get(c, ''):
                yield self.domain[:i] + ins + self.domain[i:]
                yield self.domain[:i+1] + ins + self.domain[i+1:]
    
    def _omission(self) -> Generator[str, None, None]:
        """Generate omission variations (missing characters)."""
        for i in range(len(self.domain)):
            yield self.domain[:i] + self.domain[i+1:]
    
    def _repetition(self) -> Generator[str, None, None]:
        """Generate repetition variations (doubled characters)."""
        for i, c in enumerate(self.domain):
            yield self.domain[:i] + c + self.domain[i:]
    
    def _replacement(self) -> Generator[str, None, None]:
        """Generate replacement variations (adjacent key typos)."""
        for i, c in enumerate(self.domain):
            for r in self.QWERTY.get(c, ''):
                yield self.domain[:i] + r + self.domain[i+1:]
    
    def _transposition(self) -> Generator[str, None, None]:
        """Generate transposition variations (swapped characters)."""
        for i in range(len(self.domain) - 1):
            yield self.domain[:i] + self.domain[i+1] + self.domain[i] + self.domain[i+2:]
    
    def _vowel_swap(self) -> Generator[str, None, None]:
        """Generate vowel swap variations."""
        vowels = 'aeiou'
        for i, c in enumerate(self.domain):
            if c in vowels:
                for v in vowels:
                    if v != c:
                        yield self.domain[:i] + v + self.domain[i+1:]
    
    def _addition(self) -> Generator[str, None, None]:
        """Generate addition variations (common phishing prefixes/suffixes)."""
        for word in self.ADDITIONS:
            yield word + self.domain
            yield self.domain + word
            yield word + '-' + self.domain
            yield self.domain + '-' + word
    
    def _subdomain_simulation(self) -> Generator[str, None, None]:
        """Generate subdomain-style variations."""
        for i in range(1, len(self.domain)):
            if self.domain[i] not in '-.' and self.domain[i-1] not in '-.':
                yield self.domain[:i] + '.' + self.domain[i:]
    
    def generate_all(self) -> Set[Tuple[str, str]]:
        """Generate all permutations and return as set of (domain, type) tuples."""
        fuzzers = [
            ('bitsquatting', self._bitsquatting),
            ('homoglyph', self._homoglyph),
            ('hyphenation', self._hyphenation),
            ('insertion', self._insertion),
            ('omission', self._omission),
            ('repetition', self._repetition),
            ('replacement', self._replacement),
            ('transposition', self._transposition),
            ('vowel-swap', self._vowel_swap),
            ('addition', self._addition),
        ]
        
        self.permutations = set()
        for name, func in fuzzers:
            for domain in func():
                if domain and domain != self.domain:
                    self.permutations.add((domain, name))
        
        return self.permutations
    
    def count(self) -> int:
        return len(self.permutations)


# ============================================================================
# TARGET CONFIGURATION
# ============================================================================

@dataclass
class TargetConfig:
    """Configuration for target brands to monitor."""
    
    # Thai Banks - Primary Targets
    thai_banks: List[str] = field(default_factory=lambda: [
        'kbank', 'kasikorn', 'kasikornbank',
        'scb', 'scbeasy', 'siamcommercial',
        'krungthai', 'ktb', 'krungthaibank',
        'bangkokbank', 'bbl',
        'krungsri', 'bay',
        'ttb', 'tmbbank',
        'gsb',
        'uob', 'cimb', 'lhbank',
    ])
    
    # Government & Financial Services
    thai_gov: List[str] = field(default_factory=lambda: [
        'paotang', 'thaichana', 'เราชนะ',
        'promptpay', 'baac',
    ])
    
    # E-wallets & Payment
    thai_ewallet: List[str] = field(default_factory=lambda: [
        'truemoney', 'truewallet',
        'linepay', 'rabbitlinepay',
        'shopeepay', 'airpay', 'bluepay',
    ])
    
    # Legitimate domains to whitelist
    whitelist: List[str] = field(default_factory=lambda: [
        'kasikornbank.com', 'kbank.com', 'kasikorn.com',
        'scb.co.th', 'scbeasy.com',
        'krungthai.com', 'ktb.co.th',
        'bangkokbank.com', 'bbl.co.th',
        'krungsri.com', 'bay.co.th',
        'ttbbank.com', 'gsb.or.th',
        'truemoney.com', 'truewallet.com',
        'line.me', 'linepay.line.me',
        'shopee.co.th', 'lazada.co.th',
        'google.com', 'microsoft.com', 'apple.com',
    ])
    
    # Suspicious TLDs
    suspicious_tlds: List[str] = field(default_factory=lambda: [
        '.xyz', '.top', '.club', '.online', '.site', '.info',
        '.work', '.click', '.link', '.buzz', '.live', '.store',
        '.space', '.fun', '.icu', '.pw', '.cc', '.tk', '.ml',
        '.ga', '.cf', '.gq', '.cam', '.rest', '.monster'
    ])
    
    def get_all_targets(self) -> List[str]:
        """Get all target brands."""
        return self.thai_banks + self.thai_gov + self.thai_ewallet


# ============================================================================
# PERMUTATION DATABASE
# ============================================================================

class PermutationDatabase:
    """
    Pre-computed database of all target domain permutations.
    Used for O(1) lookup when checking incoming domains.
    """
    
    def __init__(self, config: TargetConfig):
        self.config = config
        self.permutations: Dict[str, Tuple[str, str]] = {}  # domain -> (target, fuzzer_type)
        self.targets_generated: Set[str] = set()
        self._build_database()
    
    def _build_database(self):
        """Build the permutation database for all targets."""
        logger.info("Building permutation database...")
        
        for target in self.config.get_all_targets():
            fuzzer = DomainFuzzer(target)
            perms = fuzzer.generate_all()
            
            for domain, fuzzer_type in perms:
                # Store mapping: permutation -> (original target, fuzzer type)
                if domain not in self.permutations:
                    self.permutations[domain] = (target, fuzzer_type)
            
            self.targets_generated.add(target)
        
        logger.info("Database built: %d permutations for %d targets", 
                   len(self.permutations), len(self.targets_generated))
    
    def lookup(self, domain: str) -> Optional[Tuple[str, str]]:
        """
        Look up a domain in the database.
        Returns (target, fuzzer_type) if found, None otherwise.
        """
        # Extract the domain name without TLD and subdomains
        parts = domain.lower().split('.')
        
        # Check various parts of the domain
        for i, part in enumerate(parts):
            if part in self.permutations:
                return self.permutations[part]
            
            # Check combined parts (e.g., kbank-secure)
            if i < len(parts) - 1:
                combined = part + parts[i + 1]
                if combined in self.permutations:
                    return self.permutations[combined]
        
        # Also check if the full domain (minus TLD) is in the database
        if len(parts) >= 2:
            domain_without_tld = '.'.join(parts[:-1])
            for perm in self.permutations:
                if perm in domain_without_tld:
                    return self.permutations[perm]
        
        return None
    
    def contains_target_keyword(self, domain: str) -> Optional[str]:
        """Check if domain contains any target keyword directly."""
        domain_lower = domain.lower()
        for target in self.config.get_all_targets():
            if target in domain_lower:
                return target
        return None


# ============================================================================
# DETECTION RESULT
# ============================================================================

@dataclass
class Detection:
    """Represents a detected suspicious domain."""
    domain: str
    target: str
    fuzzer_type: str
    risk_score: int
    risk_factors: List[str]
    detection_time: str
    certificate_issuer: str = ""
    all_domains: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# LIVE STATISTICS
# ============================================================================

class LiveStats:
    """Real-time statistics with live display."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.certs_processed = 0
        self.domains_checked = 0
        self.detections = 0
        self.high_risk = 0
        self.detections_by_target: Dict[str, int] = defaultdict(int)
        self.detections_by_fuzzer: Dict[str, int] = defaultdict(int)
        self.recent_detections: List[Detection] = []
        self._lock = threading.Lock()
        self._last_print = time.time()
    
    def record_cert(self):
        with self._lock:
            self.certs_processed += 1
    
    def record_domain(self):
        with self._lock:
            self.domains_checked += 1
    
    def record_detection(self, detection: Detection):
        with self._lock:
            self.detections += 1
            if detection.risk_score >= 70:
                self.high_risk += 1
            self.detections_by_target[detection.target] += 1
            self.detections_by_fuzzer[detection.fuzzer_type] += 1
            self.recent_detections.append(detection)
            if len(self.recent_detections) > 100:
                self.recent_detections.pop(0)
    
    def print_live(self, force: bool = False):
        """Print live statistics (throttled to once per second)."""
        now = time.time()
        if not force and now - self._last_print < 1.0:
            return
        self._last_print = now
        
        runtime = (datetime.now() - self.start_time).total_seconds()
        rate = self.certs_processed / max(runtime, 1)
        
        # Clear line and print stats
        status = (f"\r[LIVE] Certs: {self.certs_processed:,} | "
                  f"Domains: {self.domains_checked:,} | "
                  f"Rate: {rate:.0f}/s | "
                  f"DETECTIONS: {self.detections} | "
                  f"HIGH-RISK: {self.high_risk}")
        
        print(status, end='', flush=True)
    
    def print_summary(self):
        """Print final summary."""
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        print("\n")
        print("=" * 70)
        print("WATCHTOWER SESSION SUMMARY")
        print("=" * 70)
        print(f"Runtime: {runtime:.1f} seconds ({runtime/60:.1f} minutes)")
        print(f"Certificates Processed: {self.certs_processed:,}")
        print(f"Domains Checked: {self.domains_checked:,}")
        print(f"Processing Rate: {self.certs_processed/max(runtime,1):.1f} certs/second")
        print("-" * 70)
        print(f"TOTAL DETECTIONS: {self.detections}")
        print(f"HIGH RISK (>=70): {self.high_risk}")
        
        if self.detections_by_target:
            print("\nDetections by Target Brand:")
            for target, count in sorted(self.detections_by_target.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {target}: {count}")
        
        if self.detections_by_fuzzer:
            print("\nDetections by Fuzzer Type:")
            for fuzzer, count in sorted(self.detections_by_fuzzer.items(),
                                        key=lambda x: x[1], reverse=True):
                print(f"  {fuzzer}: {count}")
        
        print("=" * 70)


# ============================================================================
# MAIN WATCHTOWER CLASS
# ============================================================================

class Watchtower:
    """
    Main Watchtower monitoring system.
    Watches CT logs and detects phishing domains using DNSTwist algorithms.
    """
    
    CERTSTREAM_URL = 'wss://certstream.calidog.io/'
    
    def __init__(self, config: Optional[TargetConfig] = None, 
                 output_file: Optional[str] = None):
        self.config = config or TargetConfig()
        self.db = PermutationDatabase(self.config)
        self.stats = LiveStats()
        self.output_file = output_file
        self.detections: List[Detection] = []
        self.is_running = False
        self._output_lock = threading.Lock()
        
        if self.output_file:
            self._init_output_file()
    
    def _init_output_file(self):
        """Initialize output file with headers."""
        if self.output_file.endswith('.csv'):
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'domain', 'target', 'fuzzer_type', 
                                'risk_score', 'risk_factors', 'issuer'])
    
    def _save_detection(self, detection: Detection):
        """Save detection to output file."""
        if not self.output_file:
            return
        
        with self._output_lock:
            if self.output_file.endswith('.csv'):
                with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        detection.detection_time,
                        detection.domain,
                        detection.target,
                        detection.fuzzer_type,
                        detection.risk_score,
                        '; '.join(detection.risk_factors),
                        detection.certificate_issuer
                    ])
            else:  # JSON
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(detection.to_dict()) + '\n')
    
    def _is_whitelisted(self, domain: str) -> bool:
        """Check if domain is whitelisted."""
        domain_lower = domain.lower()
        for safe in self.config.whitelist:
            if domain_lower == safe or domain_lower.endswith('.' + safe):
                return True
        return False
    
    def _calculate_risk(self, domain: str, target: str, fuzzer_type: str) -> Tuple[int, List[str]]:
        """Calculate risk score and factors for a domain."""
        score = 0
        factors = []
        domain_lower = domain.lower()
        
        # Base score from detection type
        if fuzzer_type in ['homoglyph', 'bitsquatting']:
            score += 40
            factors.append(f"High-risk fuzzer: {fuzzer_type}")
        elif fuzzer_type in ['addition', 'hyphenation']:
            score += 30
            factors.append(f"Medium-risk fuzzer: {fuzzer_type}")
        else:
            score += 25
            factors.append(f"Typosquatting: {fuzzer_type}")
        
        # TLD analysis
        for tld in self.config.suspicious_tlds:
            if domain_lower.endswith(tld):
                score += 25
                factors.append(f"Suspicious TLD: {tld}")
                break
        
        # Multiple hyphens
        if domain_lower.count('-') >= 2:
            score += 15
            factors.append("Multiple hyphens in domain")
        
        # Long domain
        if len(domain_lower) > 30:
            score += 10
            factors.append("Unusually long domain")
        
        # Security keywords
        security_words = ['secure', 'verify', 'login', 'update', 'confirm', 'auth']
        for word in security_words:
            if word in domain_lower:
                score += 15
                factors.append(f"Security keyword: {word}")
                break
        
        # Contains numbers
        if re.search(r'\d', domain_lower):
            score += 5
            factors.append("Contains numbers")
        
        return min(score, 100), factors
    
    def _analyze_domain(self, domain: str, cert_data: dict) -> Optional[Detection]:
        """Analyze a domain for phishing indicators."""
        if self._is_whitelisted(domain):
            return None
        
        # First, check exact keyword match
        target = self.db.contains_target_keyword(domain)
        if target:
            # Direct keyword match - high confidence
            score, factors = self._calculate_risk(domain, target, "keyword-match")
            factors.insert(0, f"Contains target keyword: {target}")
            score = min(score + 20, 100)
        else:
            # Check fuzzer database
            result = self.db.lookup(domain)
            if not result:
                return None
            target, fuzzer_type = result
            score, factors = self._calculate_risk(domain, target, fuzzer_type)
        
        # Extract certificate info
        issuer = ""
        try:
            issuer = cert_data.get('leaf_cert', {}).get('issuer', {}).get('O', '')
        except:
            pass
        
        return Detection(
            domain=domain,
            target=target,
            fuzzer_type=fuzzer_type if 'fuzzer_type' in dir() else 'keyword-match',
            risk_score=score,
            risk_factors=factors,
            detection_time=datetime.now().isoformat(),
            certificate_issuer=issuer,
            all_domains=cert_data.get('leaf_cert', {}).get('all_domains', [])
        )
    
    def _certstream_callback(self, message: dict, context):
        """Callback for certstream events."""
        if message.get('message_type') == 'heartbeat':
            return
        
        if message.get('message_type') != 'certificate_update':
            return
        
        self.stats.record_cert()
        
        try:
            cert_data = message.get('data', {})
            leaf_cert = cert_data.get('leaf_cert', {})
            all_domains = leaf_cert.get('all_domains', [])
            
            for domain in all_domains:
                self.stats.record_domain()
                
                # Skip wildcards
                if domain.startswith('*.'):
                    domain = domain[2:]
                
                # Analyze
                detection = self._analyze_domain(domain, cert_data)
                
                if detection:
                    self.stats.record_detection(detection)
                    self.detections.append(detection)
                    self._save_detection(detection)
                    self._print_detection(detection)
            
            # Update live stats display
            self.stats.print_live()
            
        except Exception as e:
            logger.error("Error processing cert: %s", str(e))
    
    def _print_detection(self, detection: Detection):
        """Print a detection alert."""
        # Clear the live stats line first
        print("\r" + " " * 80 + "\r", end='')
        
        severity = "!!CRITICAL!!" if detection.risk_score >= 70 else "!WARNING!"
        
        print(f"\n{'='*70}")
        print(f"{severity} PHISHING DETECTED {severity}")
        print(f"{'='*70}")
        print(f"Domain:     {detection.domain}")
        print(f"Target:     {detection.target}")
        print(f"Type:       {detection.fuzzer_type}")
        print(f"Risk Score: {detection.risk_score}/100")
        print(f"Time:       {detection.detection_time}")
        if detection.certificate_issuer:
            print(f"Issuer:     {detection.certificate_issuer}")
        print(f"Factors:")
        for factor in detection.risk_factors:
            print(f"  - {factor}")
        print(f"{'='*70}\n")
    
    def start(self):
        """Start monitoring CT logs."""
        print("""
+======================================================================+
|                                                                      |
|   WATCHTOWER v2.0 - DNSTwist-style CT Log Monitor                    |
|   Part of Project SCAM-KILLER                                        |
|                                                                      |
|   Hunting phishing domains before they strike...                     |
|                                                                      |
+======================================================================+
        """)
        
        logger.info("Starting Watchtower...")
        logger.info("Targets: %d brands, %d permutations loaded",
                   len(self.db.targets_generated), len(self.db.permutations))
        logger.info("Connecting to: %s", self.CERTSTREAM_URL)
        if self.output_file:
            logger.info("Output file: %s", self.output_file)
        logger.info("Press Ctrl+C to stop\n")
        
        self.is_running = True
        
        try:
            certstream.listen_for_events(
                self._certstream_callback,
                url=self.CERTSTREAM_URL
            )
        except KeyboardInterrupt:
            logger.info("\nStopping Watchtower...")
        except Exception as e:
            logger.error("Certstream error: %s", str(e))
        finally:
            self.stop()
    
    def stop(self):
        """Stop monitoring and print summary."""
        self.is_running = False
        self.stats.print_summary()
        
        if self.detections:
            print(f"\n[RESULTS] {len(self.detections)} detections saved")
            if self.output_file:
                print(f"[OUTPUT] Saved to: {self.output_file}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_permutations(domain: str) -> None:
    """Generate and print all permutations for a domain."""
    print(f"\nGenerating permutations for: {domain}")
    print("=" * 60)
    
    fuzzer = DomainFuzzer(domain)
    perms = fuzzer.generate_all()
    
    # Group by fuzzer type
    by_type = defaultdict(list)
    for perm, ftype in perms:
        by_type[ftype].append(perm)
    
    total = 0
    for ftype, domains in sorted(by_type.items()):
        print(f"\n[{ftype.upper()}] ({len(domains)} variations)")
        for d in sorted(domains)[:10]:  # Show first 10
            print(f"  {d}")
        if len(domains) > 10:
            print(f"  ... and {len(domains) - 10} more")
        total += len(domains)
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {total} permutations generated")


def run_test_mode() -> None:
    """Run test mode with sample domains."""
    print("\nRunning test mode with sample domains...")
    print("=" * 60)
    
    config = TargetConfig()
    db = PermutationDatabase(config)
    
    # Test domains
    test_domains = [
        # Should detect (typosquatting)
        'kbank-secure.xyz',
        'kasikornbank-login.com',
        'scb-verify.top',
        'krunqthai.com',  # homoglyph: g -> q
        'kbamk.com',      # transposition
        'kbannk.com',     # repetition
        'kban.com',       # omission
        'truem0ney.com',  # homoglyph: o -> 0
        'secure-kbank.club',
        # Should NOT detect (legitimate or unrelated)
        'kbank.com',
        'kasikornbank.com',
        'randomdomain.com',
        'google.com',
    ]
    
    detections = 0
    for domain in test_domains:
        target = db.contains_target_keyword(domain)
        result = db.lookup(domain)
        
        is_whitelist = any(domain == w or domain.endswith('.' + w) 
                          for w in config.whitelist)
        
        if is_whitelist:
            status = "[WHITELIST]"
        elif target or result:
            status = "[DETECTED]"
            detections += 1
            if result:
                print(f"\n{status} {domain}")
                print(f"  Target: {result[0]}, Type: {result[1]}")
            else:
                print(f"\n{status} {domain}")
                print(f"  Contains keyword: {target}")
        else:
            status = "[CLEAN]"
            print(f"\n{status} {domain}")
    
    print(f"\n{'='*60}")
    print(f"Test complete: {detections}/{len(test_domains)} detected")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='WATCHTOWER - CT Log Monitor for Phishing Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python watchtower.py                        # Start monitoring
  python watchtower.py -o detections.csv      # Save to CSV
  python watchtower.py --generate kbank       # Show permutations
  python watchtower.py --test                 # Run test mode
        """
    )
    
    parser.add_argument('-o', '--output', 
                       help='Output file for detections (CSV or JSON)')
    parser.add_argument('--generate', metavar='DOMAIN',
                       help='Generate permutations for a domain')
    parser.add_argument('--test', action='store_true',
                       help='Run test mode with sample domains')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_permutations(args.generate)
    elif args.test:
        run_test_mode()
    else:
        watchtower = Watchtower(output_file=args.output)
        watchtower.start()


if __name__ == '__main__':
    main()
