#!/usr/bin/env python3
"""
SCAM-HUNTER v1.0 - AI-Powered Phishing Domain Scanner
======================================================
Hackathon Project: AI Fraud Detection for Thai Banks

This tool proactively hunts for phishing domains targeting Thai financial
institutions using dnstwist's powerful domain permutation engine.

Features:
1. DNSTwist Integration - Generate all possible typosquatting variations
2. Live DNS Resolution - Check if domains are actually registered
3. Web Content Analysis - Fetch and analyze suspicious sites
4. AI Risk Scoring - Smart scoring based on multiple factors
5. Beautiful Reports - Export to HTML, JSON, CSV
6. Takedown Support - Auto-generate reports for ThaiCERT

Usage:
    python scam_hunter.py kbank.com              # Scan single domain
    python scam_hunter.py --all                  # Scan all Thai banks
    python scam_hunter.py kbank.com --report     # Generate HTML report
    python scam_hunter.py kbank.com --live       # Only show live threats

Author: SCAM-KILLER Team
"""

import subprocess
import json
import csv
import sys
import os
import re
import socket
import ssl
import urllib.request
import urllib.error
import threading
import time
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import hashlib

# ============================================================================
# CONFIGURATION
# ============================================================================

# Thai Bank Targets - Primary Monitoring List
THAI_TARGETS = {
    'kbank.com': {'name': 'Kasikornbank', 'alias': ['kasikorn', 'kbank']},
    'kasikornbank.com': {'name': 'Kasikornbank', 'alias': ['kasikorn']},
    'scb.co.th': {'name': 'Siam Commercial Bank', 'alias': ['scb', 'scbeasy']},
    'krungthai.com': {'name': 'Krungthai Bank', 'alias': ['ktb', 'krungthai']},
    'bangkokbank.com': {'name': 'Bangkok Bank', 'alias': ['bbl']},
    'krungsri.com': {'name': 'Bank of Ayudhya', 'alias': ['krungsri', 'bay']},
    'ttbbank.com': {'name': 'TMBThanachart Bank', 'alias': ['ttb', 'tmb']},
    'gsb.or.th': {'name': 'Government Savings Bank', 'alias': ['gsb']},
    'truemoney.com': {'name': 'TrueMoney', 'alias': ['truewallet']},
    'linepay.line.me': {'name': 'LINE Pay', 'alias': ['linepay', 'rabbit']},
}

# Suspicious TLDs that scammers often use
SUSPICIOUS_TLDS = [
    '.xyz', '.top', '.club', '.online', '.site', '.info', '.work', 
    '.click', '.link', '.buzz', '.live', '.store', '.space', '.fun', 
    '.icu', '.pw', '.cc', '.tk', '.ml', '.ga', '.cf', '.gq', 
    '.cam', '.rest', '.monster', '.sbs', '.cfd'
]

# Phishing keywords commonly found in scam domains
PHISHING_KEYWORDS = [
    'secure', 'login', 'signin', 'verify', 'update', 'confirm',
    'account', 'auth', 'portal', 'service', 'support', 'official',
    'reward', 'prize', 'bonus', 'claim', 'alert', 'urgent', 'locked'
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DomainThreat:
    """Represents a detected phishing domain threat."""
    domain: str
    fuzzer: str
    dns_a: List[str] = field(default_factory=list)
    dns_mx: List[str] = field(default_factory=list)
    dns_ns: List[str] = field(default_factory=list)
    http_status: Optional[int] = None
    https_enabled: bool = False
    ssl_issuer: str = ""
    page_title: str = ""
    page_content_hash: str = ""
    similar_content: bool = False
    risk_score: int = 0
    risk_factors: List[str] = field(default_factory=list)
    is_live: bool = False
    screenshot_path: str = ""
    scan_time: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScanReport:
    """Complete scan report for a target domain."""
    target_domain: str
    target_name: str
    scan_start: str
    scan_end: str
    total_permutations: int
    registered_domains: int
    live_threats: int
    high_risk_count: int
    threats: List[DomainThreat] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            'threats': [t.to_dict() for t in self.threats]
        }


# ============================================================================
# DNSTWIST WRAPPER
# ============================================================================

class DNSTwistScanner:
    """Wrapper for dnstwist domain permutation scanning."""
    
    def __init__(self, threads: int = 50):
        self.threads = threads
        self._check_dnstwist()
    
    def _check_dnstwist(self):
        """Verify dnstwist is installed."""
        try:
            result = subprocess.run(
                ['dnstwist', '--help'],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                raise RuntimeError("dnstwist not working properly")
        except FileNotFoundError:
            # Try python -m dnstwist
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'dnstwist', '--help'],
                    capture_output=True, text=True
                )
            except:
                raise RuntimeError("dnstwist not installed. Run: pip install dnstwist")
    
    def generate_permutations(self, domain: str) -> List[Dict]:
        """Generate domain permutations using dnstwist (without resolution)."""
        print(f"[*] Generating permutations for: {domain}")
        
        try:
            # Use python -m dnstwist for better compatibility
            result = subprocess.run(
                [sys.executable, '-m', 'dnstwist', '--format', 'json', domain],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                domains = json.loads(result.stdout)
                print(f"[+] Generated {len(domains)} permutations")
                return domains
            else:
                print(f"[-] Error: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("[-] Timeout generating permutations")
            return []
        except json.JSONDecodeError:
            print("[-] Failed to parse dnstwist output")
            return []
    
    def scan_with_resolution(self, domain: str, registered_only: bool = False) -> List[Dict]:
        """Full scan with DNS resolution using dnstwist."""
        print(f"[*] Scanning {domain} with DNS resolution...")
        print(f"[*] This may take a few minutes...")
        
        try:
            cmd = [
                sys.executable, '-m', 'dnstwist',
                '--format', 'json',
                '--threads', str(self.threads),
                '--registered' if registered_only else '',
                domain
            ]
            # Remove empty strings from command
            cmd = [c for c in cmd if c]
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0 and result.stdout:
                domains = json.loads(result.stdout)
                registered = [d for d in domains if d.get('dns_a') or d.get('dns_ns')]
                print(f"[+] Found {len(registered)} registered domains out of {len(domains)} permutations")
                return domains
            else:
                print(f"[-] Error: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("[-] Timeout during scan")
            return []
        except json.JSONDecodeError as e:
            print(f"[-] Failed to parse output: {e}")
            return []


# ============================================================================
# WEB CONTENT ANALYZER
# ============================================================================

class WebAnalyzer:
    """Analyzes web content for phishing indicators."""
    
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    TIMEOUT = 10
    
    def __init__(self):
        self.original_hashes = {}  # Store hashes of legitimate sites
    
    def fetch_page(self, domain: str) -> Tuple[int, str, str]:
        """
        Fetch a web page and return (status_code, content, title).
        Tries HTTPS first, then HTTP.
        """
        for protocol in ['https', 'http']:
            url = f"{protocol}://{domain}"
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': self.USER_AGENT}
                )
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, timeout=self.TIMEOUT, context=ctx) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    status = response.status
                    
                    # Extract title
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else ""
                    
                    return status, content, title
                    
            except Exception:
                continue
        
        return 0, "", ""
    
    def get_content_hash(self, content: str) -> str:
        """Generate a fuzzy hash of page content."""
        # Remove whitespace and scripts for comparison
        clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r'\s+', ' ', clean)
        return hashlib.md5(clean.encode()).hexdigest()[:16]
    
    def check_ssl(self, domain: str) -> Tuple[bool, str]:
        """Check SSL certificate and return (has_ssl, issuer)."""
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    return True, issuer.get('organizationName', 'Unknown')
        except:
            return False, ""
    
    def analyze_content(self, content: str) -> List[str]:
        """Analyze page content for phishing indicators."""
        indicators = []
        content_lower = content.lower()
        
        # Thai bank names in content
        thai_terms = ['kbank', 'kasikorn', 'scb', 'krungthai', 'bangkok bank']
        for term in thai_terms:
            if term in content_lower:
                indicators.append(f"Contains Thai bank reference: {term}")
        
        # Login form detection
        if '<form' in content_lower and ('password' in content_lower or 'login' in content_lower):
            indicators.append("Contains login/password form")
        
        # Credit card input detection
        if 'card' in content_lower and ('number' in content_lower or 'cvv' in content_lower):
            indicators.append("Contains credit card input fields")
        
        # OTP/PIN input detection
        if 'otp' in content_lower or 'pin' in content_lower:
            indicators.append("Contains OTP/PIN input")
        
        # Thai language detection
        thai_chars = re.findall(r'[\u0E00-\u0E7F]+', content)
        if thai_chars:
            indicators.append("Contains Thai language text")
        
        return indicators


# ============================================================================
# RISK SCORING ENGINE
# ============================================================================

class RiskScorer:
    """AI-style risk scoring engine."""
    
    @staticmethod
    def calculate_risk(threat: DomainThreat, original_domain: str) -> Tuple[int, List[str]]:
        """Calculate risk score and factors for a threat."""
        score = 0
        factors = []
        domain_lower = threat.domain.lower()
        
        # 1. DNS Registration (domain is live)
        if threat.dns_a:
            score += 30
            factors.append(f"Domain resolves to: {', '.join(threat.dns_a[:2])}")
        
        # 2. Web server active
        if threat.http_status:
            if threat.http_status == 200:
                score += 25
                factors.append("Web server responding (HTTP 200)")
            elif threat.http_status in [301, 302]:
                score += 15
                factors.append("Web server redirecting")
        
        # 3. HTTPS enabled (trying to look legitimate)
        if threat.https_enabled:
            score += 10
            factors.append(f"SSL Certificate: {threat.ssl_issuer}")
        
        # 4. Suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if domain_lower.endswith(tld):
                score += 20
                factors.append(f"Suspicious TLD: {tld}")
                break
        
        # 5. Fuzzer type analysis
        high_risk_fuzzers = ['homoglyph', 'bitsquatting', 'cyrillic']
        medium_risk_fuzzers = ['addition', 'hyphenation', 'subdomain']
        
        if threat.fuzzer in high_risk_fuzzers:
            score += 15
            factors.append(f"High-risk typosquat: {threat.fuzzer}")
        elif threat.fuzzer in medium_risk_fuzzers:
            score += 10
            factors.append(f"Typosquat technique: {threat.fuzzer}")
        
        # 6. Phishing keywords in domain
        for keyword in PHISHING_KEYWORDS:
            if keyword in domain_lower:
                score += 10
                factors.append(f"Phishing keyword: {keyword}")
                break
        
        # 7. Page title analysis
        if threat.page_title:
            title_lower = threat.page_title.lower()
            if any(bank in title_lower for bank in ['kbank', 'kasikorn', 'scb', 'krungthai']):
                score += 20
                factors.append(f"Bank name in title: {threat.page_title[:50]}")
        
        # 8. Similar content to original
        if threat.similar_content:
            score += 25
            factors.append("Content similar to legitimate site")
        
        return min(score, 100), factors


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generate beautiful HTML and other reports."""
    
    @staticmethod
    def generate_html(report: ScanReport, output_path: str):
        """Generate a beautiful HTML report."""
        
        # Sort threats by risk score
        sorted_threats = sorted(report.threats, key=lambda x: x.risk_score, reverse=True)
        
        # Generate threat rows
        threat_rows = ""
        for t in sorted_threats:
            if not t.is_live:
                continue
            
            risk_class = "critical" if t.risk_score >= 70 else "warning" if t.risk_score >= 40 else "low"
            factors_html = "<br>".join(f"• {f}" for f in t.risk_factors)
            
            threat_rows += f"""
            <tr class="{risk_class}">
                <td class="domain">{t.domain}</td>
                <td>{t.fuzzer}</td>
                <td>{', '.join(t.dns_a[:2]) if t.dns_a else 'N/A'}</td>
                <td>{'Yes' if t.https_enabled else 'No'}</td>
                <td class="score">{t.risk_score}</td>
                <td class="factors">{factors_html}</td>
            </tr>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCAM-HUNTER Report: {report.target_domain}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            margin-bottom: 30px;
        }}
        h1 {{ 
            font-size: 2.5em; 
            background: linear-gradient(90deg, #ff6b6b, #feca57);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .subtitle {{ color: #888; font-size: 1.1em; }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{ color: #888; }}
        .stat-card.danger .stat-value {{ color: #ff6b6b; }}
        .stat-card.warning .stat-value {{ color: #feca57; }}
        .stat-card.info .stat-value {{ color: #54a0ff; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(255,255,255,0.03);
            border-radius: 15px;
            overflow: hidden;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        th {{
            background: rgba(255,255,255,0.1);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}
        
        tr.critical {{ border-left: 4px solid #ff6b6b; }}
        tr.warning {{ border-left: 4px solid #feca57; }}
        tr.low {{ border-left: 4px solid #54a0ff; }}
        
        .domain {{ font-family: monospace; font-size: 1.1em; }}
        .score {{ 
            font-weight: bold; 
            font-size: 1.2em;
        }}
        tr.critical .score {{ color: #ff6b6b; }}
        tr.warning .score {{ color: #feca57; }}
        tr.low .score {{ color: #54a0ff; }}
        
        .factors {{ font-size: 0.85em; color: #aaa; }}
        
        footer {{
            text-align: center;
            padding: 40px;
            color: #666;
            margin-top: 30px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        .badge-danger {{ background: rgba(255,107,107,0.2); color: #ff6b6b; }}
        .badge-warning {{ background: rgba(254,202,87,0.2); color: #feca57; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SCAM-HUNTER Report</h1>
            <p class="subtitle">AI-Powered Phishing Domain Detection for {report.target_name}</p>
            <p style="margin-top: 15px; color: #666;">
                Target: <strong>{report.target_domain}</strong> | 
                Scan Time: {report.scan_start}
            </p>
        </header>
        
        <div class="stats">
            <div class="stat-card info">
                <div class="stat-value">{report.total_permutations:,}</div>
                <div class="stat-label">Total Permutations</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-value">{report.registered_domains}</div>
                <div class="stat-label">Registered Domains</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-value">{report.live_threats}</div>
                <div class="stat-label">Live Threats</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-value">{report.high_risk_count}</div>
                <div class="stat-label">High Risk (70+)</div>
            </div>
        </div>
        
        <h2 style="margin-bottom: 20px;">
            Detected Threats 
            <span class="badge badge-danger">{report.live_threats} Active</span>
        </h2>
        
        <table>
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>Type</th>
                    <th>IP Address</th>
                    <th>HTTPS</th>
                    <th>Risk</th>
                    <th>Factors</th>
                </tr>
            </thead>
            <tbody>
                {threat_rows if threat_rows else '<tr><td colspan="6" style="text-align:center;padding:40px;color:#666;">No live threats detected</td></tr>'}
            </tbody>
        </table>
        
        <footer>
            <p>Generated by SCAM-HUNTER v1.0 | Project SCAM-KILLER</p>
            <p>AI Fraud Detection Hackathon 2024</p>
        </footer>
    </div>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"[+] HTML report saved: {output_path}")
    
    @staticmethod
    def generate_json(report: ScanReport, output_path: str):
        """Generate JSON report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"[+] JSON report saved: {output_path}")
    
    @staticmethod
    def generate_csv(report: ScanReport, output_path: str):
        """Generate CSV report."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'domain', 'fuzzer', 'dns_a', 'https', 'risk_score', 
                'is_live', 'page_title', 'risk_factors'
            ])
            for t in report.threats:
                if t.is_live:
                    writer.writerow([
                        t.domain,
                        t.fuzzer,
                        ';'.join(t.dns_a),
                        t.https_enabled,
                        t.risk_score,
                        t.is_live,
                        t.page_title[:50],
                        ';'.join(t.risk_factors)
                    ])
        print(f"[+] CSV report saved: {output_path}")
    
    @staticmethod
    def generate_thaicert_report(report: ScanReport) -> str:
        """Generate report format for ThaiCERT submission."""
        lines = [
            "=" * 70,
            "PHISHING DOMAIN REPORT - ThaiCERT Submission",
            "=" * 70,
            f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Target Brand: {report.target_name} ({report.target_domain})",
            f"Total Threats Detected: {report.live_threats}",
            "",
            "HIGH RISK DOMAINS REQUIRING IMMEDIATE ACTION:",
            "-" * 70,
        ]
        
        for t in sorted(report.threats, key=lambda x: x.risk_score, reverse=True):
            if t.is_live and t.risk_score >= 50:
                lines.extend([
                    f"\nDomain: {t.domain}",
                    f"Risk Score: {t.risk_score}/100",
                    f"IP Address: {', '.join(t.dns_a) if t.dns_a else 'Unknown'}",
                    f"Detection Type: {t.fuzzer}",
                    "Risk Factors:",
                    *[f"  - {f}" for f in t.risk_factors],
                ])
        
        lines.extend([
            "",
            "=" * 70,
            "This report was auto-generated by SCAM-HUNTER v1.0",
            "For questions: report@thaicert.or.th",
        ])
        
        return "\n".join(lines)


# ============================================================================
# MAIN SCANNER
# ============================================================================

class ScamHunter:
    """Main SCAM-HUNTER scanner class."""
    
    def __init__(self, threads: int = 50):
        self.dnstwist = DNSTwistScanner(threads=threads)
        self.web = WebAnalyzer()
        self.threads = threads
    
    def scan_domain(self, domain: str, live_only: bool = False, 
                    quick: bool = False) -> ScanReport:
        """
        Scan a domain for phishing threats.
        
        Args:
            domain: Target domain to scan (e.g., kbank.com)
            live_only: Only include domains with active DNS
            quick: Skip web content analysis for speed
        """
        target_info = THAI_TARGETS.get(domain, {'name': domain, 'alias': []})
        target_name = target_info['name']
        
        print("\n" + "=" * 70)
        print("SCAM-HUNTER v1.0 - AI-Powered Phishing Domain Scanner")
        print("=" * 70)
        print(f"Target: {target_name} ({domain})")
        print(f"Mode: {'Quick' if quick else 'Full'} | Live Only: {live_only}")
        print("=" * 70 + "\n")
        
        scan_start = datetime.now().isoformat()
        
        # Step 1: Generate permutations and resolve DNS
        print("[STEP 1/3] Scanning with dnstwist (DNS resolution)...")
        raw_results = self.dnstwist.scan_with_resolution(domain, registered_only=live_only)
        
        if not raw_results:
            print("[-] No results from dnstwist")
            return ScanReport(
                target_domain=domain,
                target_name=target_name,
                scan_start=scan_start,
                scan_end=datetime.now().isoformat(),
                total_permutations=0,
                registered_domains=0,
                live_threats=0,
                high_risk_count=0
            )
        
        # Step 2: Filter and enrich results
        print("\n[STEP 2/3] Analyzing detected domains...")
        threats = []
        registered_count = 0
        
        for item in raw_results:
            # Skip original domain
            if item.get('fuzzer') == '*original':
                continue
            
            domain_name = item.get('domain', '')
            dns_a = item.get('dns_a', [])
            dns_mx = item.get('dns_mx', [])
            dns_ns = item.get('dns_ns', [])
            
            # Check if registered
            is_registered = bool(dns_a or dns_ns)
            if is_registered:
                registered_count += 1
            
            if live_only and not is_registered:
                continue
            
            threat = DomainThreat(
                domain=domain_name,
                fuzzer=item.get('fuzzer', 'unknown'),
                dns_a=dns_a if isinstance(dns_a, list) else [dns_a] if dns_a else [],
                dns_mx=dns_mx if isinstance(dns_mx, list) else [dns_mx] if dns_mx else [],
                dns_ns=dns_ns if isinstance(dns_ns, list) else [dns_ns] if dns_ns else [],
                is_live=is_registered
            )
            
            threats.append(threat)
        
        # Step 3: Web content analysis (if not quick mode)
        if not quick and threats:
            print(f"\n[STEP 3/3] Analyzing web content for {len([t for t in threats if t.is_live])} live domains...")
            
            live_threats = [t for t in threats if t.is_live]
            with ThreadPoolExecutor(max_workers=min(10, len(live_threats))) as executor:
                def analyze_threat(t):
                    if t.dns_a:
                        # Check SSL
                        t.https_enabled, t.ssl_issuer = self.web.check_ssl(t.domain)
                        
                        # Fetch page
                        status, content, title = self.web.fetch_page(t.domain)
                        t.http_status = status
                        t.page_title = title
                        
                        if content:
                            t.page_content_hash = self.web.get_content_hash(content)
                    
                    # Calculate risk score
                    t.risk_score, t.risk_factors = RiskScorer.calculate_risk(t, domain)
                    return t
                
                futures = {executor.submit(analyze_threat, t): t for t in live_threats}
                for i, future in enumerate(as_completed(futures)):
                    print(f"\r  Analyzed {i+1}/{len(live_threats)} domains", end='', flush=True)
            print()
        else:
            # Quick mode - just calculate basic risk
            for t in threats:
                t.risk_score, t.risk_factors = RiskScorer.calculate_risk(t, domain)
        
        # Build report
        live_count = len([t for t in threats if t.is_live])
        high_risk = len([t for t in threats if t.risk_score >= 70])
        
        report = ScanReport(
            target_domain=domain,
            target_name=target_name,
            scan_start=scan_start,
            scan_end=datetime.now().isoformat(),
            total_permutations=len(raw_results),
            registered_domains=registered_count,
            live_threats=live_count,
            high_risk_count=high_risk,
            threats=threats
        )
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _print_summary(self, report: ScanReport):
        """Print scan summary to console."""
        print("\n" + "=" * 70)
        print("SCAN COMPLETE - SUMMARY")
        print("=" * 70)
        print(f"Target: {report.target_name}")
        print(f"Total Permutations Checked: {report.total_permutations:,}")
        print(f"Registered Domains Found: {report.registered_domains}")
        print(f"Live Web Servers: {report.live_threats}")
        print(f"HIGH RISK (70+): {report.high_risk_count}")
        print("=" * 70)
        
        # Show top threats
        top_threats = sorted(
            [t for t in report.threats if t.is_live],
            key=lambda x: x.risk_score, reverse=True
        )[:10]
        
        if top_threats:
            print("\nTOP THREATS:")
            print("-" * 70)
            for t in top_threats:
                risk_indicator = "!!!" if t.risk_score >= 70 else "! " if t.risk_score >= 40 else "  "
                print(f"{risk_indicator} [{t.risk_score:3d}] {t.domain}")
                for factor in t.risk_factors[:3]:
                    print(f"        -> {factor}")
            print("-" * 70)
    
    def scan_all_thai_banks(self) -> List[ScanReport]:
        """Scan all configured Thai bank domains."""
        reports = []
        for domain in THAI_TARGETS.keys():
            try:
                report = self.scan_domain(domain, live_only=True, quick=True)
                reports.append(report)
            except Exception as e:
                print(f"[-] Error scanning {domain}: {e}")
        return reports


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='SCAM-HUNTER - AI-Powered Phishing Domain Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scam_hunter.py kbank.com              # Scan kbank.com
  python scam_hunter.py kbank.com --live       # Only show live threats
  python scam_hunter.py kbank.com --report     # Generate HTML report
  python scam_hunter.py kbank.com --quick      # Quick scan (no web analysis)
  python scam_hunter.py --all                  # Scan all Thai banks
  python scam_hunter.py --list                 # List monitored banks
        """
    )
    
    parser.add_argument('domain', nargs='?', help='Target domain to scan')
    parser.add_argument('--all', action='store_true', help='Scan all Thai banks')
    parser.add_argument('--list', action='store_true', help='List monitored banks')
    parser.add_argument('--live', action='store_true', help='Only show live/registered domains')
    parser.add_argument('--quick', action='store_true', help='Quick scan without web analysis')
    parser.add_argument('--report', action='store_true', help='Generate HTML report')
    parser.add_argument('--json', action='store_true', help='Generate JSON report')
    parser.add_argument('--csv', action='store_true', help='Generate CSV report')
    parser.add_argument('--threads', type=int, default=50, help='Number of threads')
    parser.add_argument('-o', '--output', help='Output directory for reports')
    
    args = parser.parse_args()
    
    if args.list:
        print("\nMonitored Thai Financial Institutions:")
        print("-" * 50)
        for domain, info in THAI_TARGETS.items():
            print(f"  {domain:25} - {info['name']}")
        return
    
    if not args.domain and not args.all:
        parser.print_help()
        return
    
    hunter = ScamHunter(threads=args.threads)
    output_dir = args.output or '.'
    
    if args.all:
        reports = hunter.scan_all_thai_banks()
        if args.report:
            for r in reports:
                output_path = os.path.join(output_dir, f"report_{r.target_domain.replace('.', '_')}.html")
                ReportGenerator.generate_html(r, output_path)
    else:
        report = hunter.scan_domain(args.domain, live_only=args.live, quick=args.quick)
        
        if args.report:
            output_path = os.path.join(output_dir, f"report_{args.domain.replace('.', '_')}.html")
            ReportGenerator.generate_html(report, output_path)
        
        if args.json:
            output_path = os.path.join(output_dir, f"report_{args.domain.replace('.', '_')}.json")
            ReportGenerator.generate_json(report, output_path)
        
        if args.csv:
            output_path = os.path.join(output_dir, f"report_{args.domain.replace('.', '_')}.csv")
            ReportGenerator.generate_csv(report, output_path)
        
        # Print ThaiCERT report if high risk threats found
        if report.high_risk_count > 0:
            print("\n" + ReportGenerator.generate_thaicert_report(report))


if __name__ == '__main__':
    main()
