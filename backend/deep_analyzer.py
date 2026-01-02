#!/usr/bin/env python3
"""
DEEP DOMAIN ANALYZER - 3-Layer Analysis System
===============================================
Comprehensive phishing domain analysis using:
- Layer 1 (Bouncer): Fast local checks
- Layer 2 (Detective): DOM analysis, screenshots, favicon
- Layer 3 (Judge): AI-powered verdict
"""

import asyncio
import base64
import hashlib
import logging
import re
import ssl
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
import socket
import json

logger = logging.getLogger('DEEP_ANALYZER')

# Try to import Playwright
HAS_PLAYWRIGHT = False
PLAYWRIGHT_WORKING = False

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
    # We'll test if it actually works on first use
    PLAYWRIGHT_WORKING = True
except ImportError:
    logger.warning("Playwright not installed. Deep analysis will be limited.")

def _check_playwright_works():
    """Test if Playwright can actually launch a browser."""
    global PLAYWRIGHT_WORKING
    if not HAS_PLAYWRIGHT:
        return False
    # We assume it works until proven otherwise
    return PLAYWRIGHT_WORKING

def _mark_playwright_broken():
    """Mark Playwright as not working (browser crashed)."""
    global PLAYWRIGHT_WORKING
    PLAYWRIGHT_WORKING = False
    logger.error("Playwright browser crashed. Disabling browser-based analysis.")


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DOMAnalysis:
    """Analysis of a webpage's DOM structure."""
    has_login_form: bool = False
    has_password_field: bool = False
    form_count: int = 0
    form_actions: List[str] = field(default_factory=list)
    input_fields: List[Dict] = field(default_factory=list)
    suspicious_elements: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    scripts_count: int = 0
    meta_title: str = ""
    meta_description: str = ""
    page_text: str = ""
    thai_keywords_found: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Layer1Result:
    """Layer 1 (Bouncer) analysis result."""
    score: int = 0
    factors: List[str] = field(default_factory=list)
    fuzzer_type: str = ""
    is_registered: bool = False
    dns_a: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass 
class Layer2Result:
    """Layer 2 (Detective) analysis result."""
    score: int = 0
    factors: List[str] = field(default_factory=list)
    screenshot_b64: Optional[str] = None
    favicon_url: Optional[str] = None
    favicon_b64: Optional[str] = None
    dom_analysis: Optional[DOMAnalysis] = None
    page_accessible: bool = False
    redirect_chain: List[str] = field(default_factory=list)
    ssl_info: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        result = asdict(self)
        if self.dom_analysis:
            result['dom_analysis'] = self.dom_analysis.to_dict()
        return result


@dataclass
class Layer3Result:
    """Layer 3 (Judge) analysis result."""
    score: int = 0
    verdict: str = "unknown"  # "safe", "suspicious", "phishing", "unknown"
    confidence: float = 0.0
    reasoning: str = ""
    recommendation: str = "monitor"  # "safe", "monitor", "investigate", "takedown"
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DeepAnalysisResult:
    """Complete 3-layer analysis result."""
    domain: str
    target_domain: str
    analysis_time: str
    
    # Layer results
    layer1: Layer1Result = field(default_factory=Layer1Result)
    layer2: Layer2Result = field(default_factory=Layer2Result)
    layer3: Layer3Result = field(default_factory=Layer3Result)
    
    # Final scores
    final_score: int = 0
    recommendation: str = "monitor"
    
    def to_dict(self) -> dict:
        return {
            'domain': self.domain,
            'target_domain': self.target_domain,
            'analysis_time': self.analysis_time,
            'layer1': self.layer1.to_dict(),
            'layer2': self.layer2.to_dict(),
            'layer3': self.layer3.to_dict(),
            'final_score': self.final_score,
            'recommendation': self.recommendation
        }


# ============================================================================
# THAI PHISHING KEYWORDS
# ============================================================================

THAI_PHISHING_KEYWORDS = [
    # Authentication
    'ยืนยันตัวตน', 'ยืนยัน', 'xác nhận', 'เข้าสู่ระบบ', 'ล็อกอิน', 'login',
    # OTP/Security
    'otp', 'รหัส', 'รหัสผ่าน', 'password', 'pin', 'รหัสลับ',
    # Account
    'บัญชี', 'account', 'ระงับ', 'suspend', 'block', 'ปิดบัญชี',
    # Bank
    'ธนาคาร', 'bank', 'โอนเงิน', 'transfer', 'เงิน', 'money',
    # Urgency
    'ด่วน', 'urgent', 'ทันที', 'immediately', 'ภายใน 24', 'within 24',
    # Thai banks
    'kbank', 'kasikorn', 'scb', 'กสิกร', 'ไทยพาณิชย์', 'กรุงไทย', 'กรุงเทพ',
    # Rewards/Scam
    'รางวัล', 'prize', 'ได้รับ', 'receive', 'คลิก', 'click', 'ลิงก์', 'link'
]

SUSPICIOUS_FORM_ACTIONS = [
    'google.com/forms', 'forms.gle', 'bit.ly', 'tinyurl', 
    'script.google.com', 'webhook', 'discord.com/api'
]


# ============================================================================
# DEEP ANALYZER CLASS
# ============================================================================

class DeepDomainAnalyzer:
    """
    3-Layer Deep Analysis System for phishing detection.
    """
    
    def __init__(self):
        self.timeout = 15000  # 15 seconds
    
    async def analyze(
        self, 
        domain: str, 
        target_domain: str,
        include_screenshot: bool = True,
        include_dom: bool = True
    ) -> DeepAnalysisResult:
        """
        Run full 3-layer analysis on a domain.
        
        Args:
            domain: The suspicious domain to analyze
            target_domain: The legitimate domain being impersonated
            include_screenshot: Whether to capture screenshots
            include_dom: Whether to analyze DOM
        """
        result = DeepAnalysisResult(
            domain=domain,
            target_domain=target_domain,
            analysis_time=datetime.now().isoformat()
        )
        
        # Layer 1: Bouncer (fast, always runs)
        result.layer1 = self._layer1_bouncer(domain, target_domain)
        
        # Layer 2: Detective (DOM, screenshot - only if registered)
        if result.layer1.is_registered and (include_screenshot or include_dom):
            result.layer2 = await self._layer2_detective(
                domain, 
                include_screenshot=include_screenshot,
                include_dom=include_dom
            )
        
        # Layer 3: Judge (combine all evidence)
        result.layer3 = self._layer3_judge(result.layer1, result.layer2)
        
        # Calculate final score
        result.final_score = self._calculate_final_score(
            result.layer1, result.layer2, result.layer3
        )
        result.recommendation = self._get_recommendation(result.final_score)
        
        return result
    
    def _layer1_bouncer(self, domain: str, target: str) -> Layer1Result:
        """
        Layer 1: Fast local checks.
        - Domain fuzzing type detection
        - DNS resolution
        - TLD analysis
        - Keyword detection
        """
        result = Layer1Result()
        domain_lower = domain.lower()
        target_lower = target.lower()
        
        # DNS Resolution
        try:
            socket.setdefaulttimeout(2.0)
            ips = socket.gethostbyname_ex(domain)[2]
            result.dns_a = ips
            result.is_registered = True
            result.score += 20
            result.factors.append("Domain is registered and resolves")
        except (socket.gaierror, socket.timeout):
            result.is_registered = False
        
        # Fuzzer type detection
        target_name = target_lower.split('.')[0]
        domain_name = domain_lower.split('.')[0]
        
        # Homoglyph detection
        homoglyphs = {'0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '@': 'a'}
        normalized = domain_name
        for h, char in homoglyphs.items():
            normalized = normalized.replace(h, char)
        if normalized != domain_name and target_name in normalized:
            result.fuzzer_type = 'homoglyph'
            result.score += 30
            result.factors.append("Uses lookalike characters (homoglyph)")
        
        # Addition detection
        additions = ['secure', 'login', 'official', 'verify', 'update', 'account', 'thailand', 'th']
        for add in additions:
            if add in domain_name and add not in target_name:
                result.fuzzer_type = 'addition'
                result.score += 25
                result.factors.append(f"Uses deceptive addition: '{add}'")
                break
        
        # Contains target keyword
        if target_name in domain_name and domain_name != target_name:
            if not result.fuzzer_type:
                result.fuzzer_type = 'keyword-match'
            result.score += 20
            result.factors.append(f"Contains target brand: '{target_name}'")
        
        # Suspicious TLD
        suspicious_tlds = ['.xyz', '.top', '.club', '.online', '.site', '.info', 
                          '.click', '.link', '.buzz', '.pw', '.tk', '.ml']
        for tld in suspicious_tlds:
            if domain_lower.endswith(tld):
                result.score += 20
                result.factors.append(f"Suspicious TLD: {tld}")
                break
        
        # Multiple hyphens
        if domain_name.count('-') >= 2:
            result.score += 10
            result.factors.append("Multiple hyphens in domain")
        
        # Very long domain
        if len(domain_name) > 25:
            result.score += 10
            result.factors.append("Unusually long domain name")
        
        return result
    
    async def _layer2_detective(
        self, 
        domain: str,
        include_screenshot: bool = True,
        include_dom: bool = True
    ) -> Layer2Result:
        """
        Layer 2: Deep inspection.
        - Page screenshot
        - DOM analysis
        - Favicon extraction
        - Form detection
        """
        result = Layer2Result()
        
        # Check if Playwright is available and working
        if not HAS_PLAYWRIGHT or not _check_playwright_works():
            result.factors.append("Browser analysis not available - using limited analysis")
            # Do basic HTTP check instead
            return await self._layer2_fallback(domain, result)
        
        url = f"https://{domain}"
        browser = None
        
        try:
            async with async_playwright() as p:
                try:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-dev-shm-usage']
                    )
                except Exception as launch_err:
                    # Browser launch failed - mark Playwright as broken
                    _mark_playwright_broken()
                    result.factors.append(f"Browser launch failed: {str(launch_err)[:50]}")
                    return await self._layer2_fallback(domain, result)
                
                try:
                    context = await browser.new_context(
                        viewport={'width': 1280, 'height': 800},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    )
                    page = await context.new_page()
                    
                    # Track redirects
                    result.redirect_chain = [url]
                    
                    try:
                        response = await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')
                        result.page_accessible = True
                        
                        # Check for redirects
                        final_url = page.url
                        if final_url != url:
                            result.redirect_chain.append(final_url)
                            result.factors.append(f"Redirects to: {final_url}")
                        
                        # Wait for page to settle
                        await asyncio.sleep(1)
                        
                        # Screenshot
                        if include_screenshot:
                            try:
                                screenshot = await page.screenshot(full_page=False)
                                result.screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
                            except Exception as e:
                                logger.warning(f"Screenshot failed: {e}")
                        
                        # DOM Analysis
                        if include_dom:
                            result.dom_analysis = await self._analyze_dom(page)
                            
                            # Score based on DOM findings
                            if result.dom_analysis:
                                if result.dom_analysis.has_login_form:
                                    result.score += 25
                                    result.factors.append("Contains login form")
                                
                                if result.dom_analysis.has_password_field:
                                    result.score += 20
                                    result.factors.append("Has password input field")
                                
                                if result.dom_analysis.thai_keywords_found:
                                    result.score += 15
                                    keywords = ', '.join(result.dom_analysis.thai_keywords_found[:5])
                                    result.factors.append(f"Thai phishing keywords: {keywords}")
                                
                                # Check form actions
                                for action in result.dom_analysis.form_actions:
                                    for suspicious in SUSPICIOUS_FORM_ACTIONS:
                                        if suspicious in action.lower():
                                            result.score += 20
                                            result.factors.append(f"Suspicious form target: {action}")
                                            break
                        
                        # Favicon extraction
                        try:
                            favicon_url = await page.evaluate('''
                                () => {
                                    const link = document.querySelector('link[rel*="icon"]');
                                    return link ? link.href : null;
                                }
                            ''')
                            if favicon_url:
                                result.favicon_url = favicon_url
                        except:
                            pass
                            
                    except PlaywrightTimeout:
                        result.factors.append("Page load timeout")
                    except Exception as e:
                        result.factors.append(f"Page load error: {str(e)[:50]}")
                    
                finally:
                    if browser:
                        try:
                            await browser.close()
                        except:
                            pass
                            
        except BrokenPipeError:
            _mark_playwright_broken()
            logger.error("Playwright EPIPE error - browser crashed")
            result.factors.append("Browser crashed - using fallback analysis")
            return await self._layer2_fallback(domain, result)
        except Exception as e:
            error_str = str(e)
            if 'EPIPE' in error_str or 'broken pipe' in error_str.lower():
                _mark_playwright_broken()
                logger.error("Playwright pipe broken - browser crashed")
                result.factors.append("Browser crashed - using fallback analysis")
                return await self._layer2_fallback(domain, result)
            else:
                logger.error(f"Layer 2 analysis failed: {e}")
                result.factors.append(f"Analysis error: {str(e)[:50]}")
        
        return result
    
    async def _layer2_fallback(self, domain: str, result: Layer2Result) -> Layer2Result:
        """
        Fallback Layer 2 analysis using basic HTTP requests.
        Used when Playwright is not available or crashes.
        """
        url = f"https://{domain}"
        
        try:
            # Create SSL context that doesn't verify (for testing suspicious sites)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                result.page_accessible = True
                html = response.read().decode('utf-8', errors='ignore')[:50000]
                
                # Basic HTML analysis
                html_lower = html.lower()
                
                # Check for forms
                form_count = html_lower.count('<form')
                if form_count > 0:
                    result.score += 15
                    result.factors.append(f"Contains {form_count} form(s)")
                
                # Check for password fields
                if 'type="password"' in html_lower or "type='password'" in html_lower:
                    result.score += 20
                    result.factors.append("Has password input field")
                
                # Check for Thai phishing keywords
                keywords_found = []
                for keyword in THAI_PHISHING_KEYWORDS:
                    if keyword.lower() in html_lower:
                        keywords_found.append(keyword)
                
                if keywords_found:
                    result.score += 15
                    result.factors.append(f"Thai keywords: {', '.join(keywords_found[:5])}")
                
                # Create basic DOM analysis
                result.dom_analysis = DOMAnalysis(
                    has_login_form=form_count > 0 and ('password' in html_lower or 'login' in html_lower),
                    has_password_field='password' in html_lower,
                    form_count=form_count,
                    thai_keywords_found=keywords_found[:10]
                )
                
        except urllib.error.HTTPError as e:
            result.factors.append(f"HTTP error: {e.code}")
        except urllib.error.URLError as e:
            result.factors.append(f"URL error: {str(e.reason)[:30]}")
        except Exception as e:
            result.factors.append(f"Fallback analysis error: {str(e)[:30]}")
        
        return result
    
    async def _analyze_dom(self, page) -> DOMAnalysis:
        """Extract and analyze DOM elements."""
        analysis = DOMAnalysis()
        
        try:
            # Get page title
            analysis.meta_title = await page.title()
            
            # Get meta description
            try:
                analysis.meta_description = await page.evaluate('''
                    () => {
                        const meta = document.querySelector('meta[name="description"]');
                        return meta ? meta.content : '';
                    }
                ''')
            except:
                pass
            
            # Count forms
            forms = await page.query_selector_all('form')
            analysis.form_count = len(forms)
            
            # Analyze each form
            for form in forms:
                try:
                    action = await form.get_attribute('action') or ''
                    if action:
                        analysis.form_actions.append(action)
                    
                    # Check inputs in form
                    inputs = await form.query_selector_all('input')
                    for inp in inputs:
                        input_type = await inp.get_attribute('type') or 'text'
                        input_name = await inp.get_attribute('name') or ''
                        input_placeholder = await inp.get_attribute('placeholder') or ''
                        
                        analysis.input_fields.append({
                            'type': input_type,
                            'name': input_name,
                            'placeholder': input_placeholder
                        })
                        
                        if input_type == 'password':
                            analysis.has_password_field = True
                            analysis.has_login_form = True
                        
                        # Check for credential fields
                        credential_patterns = ['email', 'user', 'login', 'phone', 'mobile', 'id', 'card']
                        field_text = f"{input_name} {input_placeholder}".lower()
                        if any(p in field_text for p in credential_patterns):
                            if input_type in ['text', 'email', 'tel']:
                                analysis.has_login_form = True
                except:
                    continue
            
            # Get visible text
            try:
                analysis.page_text = await page.inner_text('body')
                analysis.page_text = analysis.page_text[:5000]  # Limit size
            except:
                pass
            
            # Check for Thai phishing keywords
            page_lower = analysis.page_text.lower() if analysis.page_text else ''
            for keyword in THAI_PHISHING_KEYWORDS:
                if keyword.lower() in page_lower:
                    analysis.thai_keywords_found.append(keyword)
            
            # Deduplicate keywords
            analysis.thai_keywords_found = list(set(analysis.thai_keywords_found))[:10]
            
            # Count scripts
            scripts = await page.query_selector_all('script')
            analysis.scripts_count = len(scripts)
            
            # Get external links
            try:
                links = await page.evaluate('''
                    () => {
                        const links = document.querySelectorAll('a[href^="http"]');
                        return Array.from(links).map(a => a.href).slice(0, 20);
                    }
                ''')
                analysis.external_links = links or []
            except:
                pass
                
        except Exception as e:
            logger.error(f"DOM analysis error: {e}")
        
        return analysis
    
    def _layer3_judge(self, l1: Layer1Result, l2: Layer2Result) -> Layer3Result:
        """
        Layer 3: AI Judge - Combine all evidence for final verdict.
        In production, this could call an LLM for reasoning.
        """
        result = Layer3Result()
        
        # Combine scores
        total_score = l1.score + l2.score
        
        # Analyze patterns
        high_risk_indicators = 0
        reasoning_parts = []
        
        # Check Layer 1 indicators
        if l1.is_registered:
            reasoning_parts.append("Domain is actively registered")
            high_risk_indicators += 1
        
        if 'homoglyph' in (l1.fuzzer_type or ''):
            reasoning_parts.append("Uses lookalike characters to deceive users")
            high_risk_indicators += 2
        
        if any('TLD' in f for f in l1.factors):
            reasoning_parts.append("Uses suspicious top-level domain")
            high_risk_indicators += 1
        
        # Check Layer 2 indicators
        if l2.page_accessible:
            if l2.dom_analysis:
                if l2.dom_analysis.has_login_form:
                    reasoning_parts.append("Page contains credential-harvesting form")
                    high_risk_indicators += 2
                
                if l2.dom_analysis.thai_keywords_found:
                    reasoning_parts.append("Contains Thai phishing language patterns")
                    high_risk_indicators += 2
                
                if l2.dom_analysis.has_password_field:
                    reasoning_parts.append("Requests password input")
                    high_risk_indicators += 2
        
        # Determine verdict
        if high_risk_indicators >= 4:
            result.verdict = "phishing"
            result.recommendation = "takedown"
            result.confidence = min(0.95, 0.6 + (high_risk_indicators * 0.08))
        elif high_risk_indicators >= 2:
            result.verdict = "suspicious"
            result.recommendation = "investigate"
            result.confidence = min(0.85, 0.5 + (high_risk_indicators * 0.1))
        elif high_risk_indicators >= 1:
            result.verdict = "suspicious"
            result.recommendation = "monitor"
            result.confidence = 0.5
        else:
            result.verdict = "unknown"
            result.recommendation = "monitor"
            result.confidence = 0.3
        
        # Calculate Layer 3 score contribution
        result.score = high_risk_indicators * 10
        
        # Build reasoning
        if reasoning_parts:
            result.reasoning = "Analysis indicates: " + "; ".join(reasoning_parts) + "."
        else:
            result.reasoning = "Insufficient evidence for conclusive determination."
        
        return result
    
    def _calculate_final_score(
        self, 
        l1: Layer1Result, 
        l2: Layer2Result, 
        l3: Layer3Result
    ) -> int:
        """Calculate final combined score (0-100)."""
        # Weighted combination
        score = (l1.score * 0.3) + (l2.score * 0.4) + (l3.score * 0.3)
        return min(100, int(score))
    
    def _get_recommendation(self, score: int) -> str:
        """Get recommendation based on final score."""
        if score >= 80:
            return "takedown"
        elif score >= 60:
            return "investigate"
        elif score >= 40:
            return "monitor"
        else:
            return "safe"


# ============================================================================
# TAKEDOWN REPORT GENERATOR
# ============================================================================

class TakedownReportGenerator:
    """Generate evidence packages for takedown requests."""
    
    @staticmethod
    def generate_report(analysis: DeepAnalysisResult) -> Dict:
        """Generate a takedown report from analysis results."""
        return {
            'report_id': hashlib.md5(
                f"{analysis.domain}{analysis.analysis_time}".encode()
            ).hexdigest()[:12],
            'generated_at': datetime.now().isoformat(),
            'target_domain': analysis.target_domain,
            'malicious_domain': analysis.domain,
            'risk_score': analysis.final_score,
            'recommendation': analysis.recommendation,
            'verdict': analysis.layer3.verdict,
            'confidence': analysis.layer3.confidence,
            
            'evidence': {
                'dns_records': analysis.layer1.dns_a,
                'risk_factors': (
                    analysis.layer1.factors + 
                    analysis.layer2.factors
                ),
                'has_login_form': (
                    analysis.layer2.dom_analysis.has_login_form 
                    if analysis.layer2.dom_analysis else False
                ),
                'has_password_field': (
                    analysis.layer2.dom_analysis.has_password_field
                    if analysis.layer2.dom_analysis else False
                ),
                'screenshot_available': bool(analysis.layer2.screenshot_b64),
                'thai_keywords': (
                    analysis.layer2.dom_analysis.thai_keywords_found
                    if analysis.layer2.dom_analysis else []
                )
            },
            
            'analysis_summary': analysis.layer3.reasoning,
            
            'recommended_actions': _get_recommended_actions(analysis)
        }


def _get_recommended_actions(analysis: DeepAnalysisResult) -> List[str]:
    """Get list of recommended actions based on analysis."""
    actions = []
    
    if analysis.recommendation == 'takedown':
        actions.extend([
            "Report to domain registrar for takedown",
            "Submit to Google Safe Browsing",
            "Notify brand security team",
            "Report to Thai CERT"
        ])
    elif analysis.recommendation == 'investigate':
        actions.extend([
            "Monitor domain for changes",
            "Contact registrar for ownership info",
            "Add to internal blocklist"
        ])
    else:
        actions.append("Add to monitoring watchlist")
    
    return actions


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_analyzer_instance: Optional[DeepDomainAnalyzer] = None

def get_deep_analyzer() -> DeepDomainAnalyzer:
    """Get singleton analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = DeepDomainAnalyzer()
    return _analyzer_instance
