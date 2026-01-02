#!/usr/bin/env python3
"""
SCANNER API - Domain Vulnerability Scanner
==========================================
REST API for on-demand domain scanning with DNSTwist-style fuzzing.
"""

from flask import Blueprint, request, jsonify
from typing import List, Dict, Optional
import logging
import time
import socket
import concurrent.futures
from dataclasses import dataclass, asdict
from datetime import datetime

# Try to import dnstwist, fall back to custom implementation
try:
    import dnstwist
    HAS_DNSTWIST = True
except ImportError:
    HAS_DNSTWIST = False

logger = logging.getLogger('SCANNER')

# Create Blueprint
scanner_bp = Blueprint('scanner', __name__, url_prefix='/api/scanner')


# ============================================================================
# DOMAIN FUZZER (Fallback if dnstwist not available)
# ============================================================================

class SimpleFuzzer:
    """Simplified domain fuzzer for demo purposes."""
    
    COMMON_TLDS = ['.com', '.net', '.org', '.xyz', '.io', '.co', '.app', '.site', '.online', '.info']
    
    def __init__(self, domain: str):
        self.domain = domain
        parts = domain.split('.')
        self.name = parts[0] if parts else domain
        self.tld = '.' + '.'.join(parts[1:]) if len(parts) > 1 else '.com'
    
    def generate(self) -> List[Dict]:
        """Generate domain permutations."""
        results = []
        
        # Original
        results.append({'domain': self.domain, 'fuzzer': 'original'})
        
        # Homoglyphs
        homoglyphs = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 'l': '1'}
        for char, replacement in homoglyphs.items():
            if char in self.name:
                fuzzy = self.name.replace(char, replacement, 1)
                results.append({'domain': f"{fuzzy}{self.tld}", 'fuzzer': 'homoglyph'})
        
        # Typos - omission
        for i in range(len(self.name)):
            fuzzy = self.name[:i] + self.name[i+1:]
            if fuzzy:
                results.append({'domain': f"{fuzzy}{self.tld}", 'fuzzer': 'omission'})
        
        # Typos - repetition
        for i in range(len(self.name)):
            fuzzy = self.name[:i] + self.name[i] + self.name[i:]
            results.append({'domain': f"{fuzzy}{self.tld}", 'fuzzer': 'repetition'})
        
        # Addition
        additions = ['-secure', '-login', '-official', '-thailand', '-verify', 'secure-', 'login-', 'official-']
        for add in additions:
            if add.startswith('-'):
                results.append({'domain': f"{self.name}{add}{self.tld}", 'fuzzer': 'addition'})
            else:
                results.append({'domain': f"{add}{self.name}{self.tld}", 'fuzzer': 'addition'})
        
        # TLD swap
        for tld in self.COMMON_TLDS:
            if tld != self.tld:
                results.append({'domain': f"{self.name}{tld}", 'fuzzer': 'tld-swap'})
        
        # Hyphenation
        if '-' not in self.name and len(self.name) > 3:
            results.append({'domain': f"{self.name[:len(self.name)//2]}-{self.name[len(self.name)//2:]}{self.tld}", 'fuzzer': 'hyphenation'})
        
        # Remove duplicates
        seen = set()
        unique = []
        for r in results:
            if r['domain'] not in seen:
                seen.add(r['domain'])
                unique.append(r)
        
        return unique


# ============================================================================
# DNS RESOLVER
# ============================================================================

def resolve_domain(domain: str, timeout: float = 2.0) -> Dict:
    """Resolve a domain and return DNS records."""
    result = {
        'domain': domain,
        'dns_a': [],
        'dns_mx': [],
        'is_registered': False
    }
    
    try:
        # A records
        socket.setdefaulttimeout(timeout)
        ips = socket.gethostbyname_ex(domain)[2]
        result['dns_a'] = ips
        result['is_registered'] = True
    except (socket.gaierror, socket.timeout):
        pass
    except Exception:
        pass
    
    return result


# ============================================================================
# RISK SCORER
# ============================================================================

def calculate_risk(domain_info: Dict, target_domain: str) -> Dict:
    """Calculate risk score for a domain."""
    score = 0
    factors = []
    
    domain = domain_info.get('domain', '')
    is_registered = domain_info.get('is_registered', False)
    fuzzer = domain_info.get('fuzzer', '')
    
    # Base scoring
    if is_registered:
        score += 30
        factors.append("Domain is registered")
    
    # Fuzzer-based scoring
    if fuzzer == 'homoglyph':
        score += 25
        factors.append("Uses lookalike characters")
    elif fuzzer == 'addition':
        score += 20
        factors.append("Uses deceptive addition pattern")
    elif fuzzer == 'typosquatting':
        score += 20
        factors.append("Typosquatting attempt")
    elif fuzzer == 'tld-swap':
        score += 15
        factors.append("Different TLD")
    
    # Suspicious TLDs
    suspicious_tlds = ['.xyz', '.top', '.loan', '.click', '.icu', '.site', '.online', '.pw', '.tk']
    if any(domain.endswith(tld) for tld in suspicious_tlds):
        score += 15
        factors.append("Uses suspicious TLD")
    
    # Phishing keywords
    phishing_keywords = ['secure', 'login', 'verify', 'update', 'account', 'official', 'bank']
    for keyword in phishing_keywords:
        if keyword in domain.lower() and keyword not in target_domain.lower():
            score += 10
            factors.append(f"Contains phishing keyword: {keyword}")
            break
    
    return {
        **domain_info,
        'risk_score': min(score, 100),
        'risk_factors': factors
    }


# ============================================================================
# API ROUTES
# ============================================================================

@scanner_bp.route('/scan', methods=['POST'])
def scan_domain():
    """Scan a domain for potential phishing threats."""
    data = request.json
    if not data or 'domain' not in data:
        return jsonify({'error': 'Domain is required'}), 400
    
    target_domain = data['domain'].strip().lower()
    if not target_domain:
        return jsonify({'error': 'Invalid domain'}), 400
    
    # Remove protocol if present
    if '://' in target_domain:
        target_domain = target_domain.split('://')[1]
    target_domain = target_domain.split('/')[0]
    
    start_time = time.time()
    
    # Generate permutations
    fuzzer = SimpleFuzzer(target_domain)
    permutations = fuzzer.generate()
    
    # Resolve domains in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(resolve_domain, p['domain']): p for p in permutations}
        
        for future in concurrent.futures.as_completed(futures, timeout=30):
            perm = futures[future]
            try:
                dns_result = future.result()
                result = {**dns_result, 'fuzzer': perm['fuzzer']}
                result = calculate_risk(result, target_domain)
                results.append(result)
            except Exception as e:
                logger.error(f"Error resolving {perm['domain']}: {e}")
                results.append({
                    'domain': perm['domain'],
                    'fuzzer': perm['fuzzer'],
                    'dns_a': [],
                    'dns_mx': [],
                    'is_registered': False,
                    'risk_score': 0,
                    'risk_factors': []
                })
    
    # Sort by risk score
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    
    scan_time = time.time() - start_time
    registered = [r for r in results if r['is_registered']]
    high_risk = [r for r in results if r['risk_score'] >= 70]
    
    return jsonify({
        'target': target_domain,
        'total_permutations': len(results),
        'registered_count': len(registered),
        'high_risk_count': len(high_risk),
        'results': results,
        'scan_time': round(scan_time, 2)
    })


@scanner_bp.route('/permutations', methods=['POST'])
def get_permutations():
    """Get domain permutations without DNS resolution."""
    data = request.json
    if not data or 'domain' not in data:
        return jsonify({'error': 'Domain is required'}), 400
    
    target_domain = data['domain'].strip().lower()
    fuzzer = SimpleFuzzer(target_domain)
    permutations = fuzzer.generate()
    
    return jsonify({
        'target': target_domain,
        'count': len(permutations),
        'permutations': permutations
    })


@scanner_bp.route('/quick-check', methods=['POST'])
def quick_check():
    """Quick check if a domain is potentially suspicious."""
    data = request.json
    if not data or 'domain' not in data:
        return jsonify({'error': 'Domain is required'}), 400
    
    domain = data['domain'].strip().lower()
    
    # Check against Thai targets
    thai_targets = ['kbank', 'scb', 'kasikorn', 'bangkok', 'krungsri', 'ttb', 'gsb', 'lazada', 'shopee', 'line']
    
    is_suspicious = False
    matched_target = None
    
    for target in thai_targets:
        if target in domain:
            # Check if it's not the legitimate domain
            legit_domains = [
                f'{target}.com', f'{target}.co.th', f'{target}.th',
                f'www.{target}.com', f'www.{target}.co.th'
            ]
            if domain not in legit_domains:
                is_suspicious = True
                matched_target = target
                break
    
    return jsonify({
        'domain': domain,
        'is_suspicious': is_suspicious,
        'matched_target': matched_target
    })
