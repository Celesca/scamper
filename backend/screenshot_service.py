#!/usr/bin/env python3
"""
SCREENSHOT SERVICE - Headless Browser Screenshot Capture
=========================================================
Uses Playwright to capture screenshots of suspicious domains.
"""

import asyncio
import logging
import base64
from typing import Optional, Dict, List
from datetime import datetime
import os

logger = logging.getLogger('SCREENSHOT')

# Try to import playwright
try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    logger.warning("Playwright not installed. Screenshot service will be limited.")


class ScreenshotService:
    """Service for capturing website screenshots using headless browser."""
    
    SCREENSHOT_DIR = "screenshots"
    TIMEOUT = 30000  # 30 seconds
    
    def __init__(self):
        self.browser = None
        self._ensure_screenshot_dir()
    
    def _ensure_screenshot_dir(self):
        """Create screenshot directory if it doesn't exist."""
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR)
    
    async def capture_screenshot(self, url: str, full_page: bool = False) -> Optional[bytes]:
        """
        Capture a screenshot of the given URL.
        
        Args:
            url: The URL to screenshot
            full_page: Whether to capture the full page or just viewport
            
        Returns:
            Screenshot bytes or None if failed
        """
        if not HAS_PLAYWRIGHT:
            logger.warning("Playwright not available, returning None")
            return None
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        screenshot = None
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                try:
                    await page.goto(url, timeout=self.TIMEOUT, wait_until='networkidle')
                    await asyncio.sleep(2)  # Wait for any animations
                    
                    screenshot = await page.screenshot(full_page=full_page)
                    
                except PlaywrightTimeout:
                    logger.warning(f"Timeout loading {url}")
                except Exception as e:
                    logger.error(f"Error loading {url}: {e}")
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Browser error for {url}: {e}")
        
        return screenshot
    
    async def save_screenshot(self, url: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture and save a screenshot to disk.
        
        Returns:
            Path to saved file or None if failed
        """
        screenshot = await self.capture_screenshot(url)
        if not screenshot:
            return None
        
        if not filename:
            # Generate filename from URL
            safe_url = url.replace('://', '_').replace('/', '_').replace('.', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_url}_{timestamp}.png"
        
        filepath = os.path.join(self.SCREENSHOT_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(screenshot)
        
        return filepath
    
    async def extract_page_content(self, url: str) -> Optional[Dict]:
        """
        Extract page content and metadata.
        
        Returns:
            Dictionary with page title, text, form fields, etc.
        """
        if not HAS_PLAYWRIGHT:
            return None
        
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        result = {
            'url': url,
            'title': '',
            'text': '',
            'forms': [],
            'has_password_field': False,
            'has_login_form': False,
            'external_links': [],
            'images': [],
            'error': None
        }
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    await page.goto(url, timeout=self.TIMEOUT, wait_until='domcontentloaded')
                    
                    # Get title
                    result['title'] = await page.title()
                    
                    # Get visible text
                    result['text'] = await page.inner_text('body')
                    
                    # Check for password fields
                    password_fields = await page.query_selector_all('input[type="password"]')
                    result['has_password_field'] = len(password_fields) > 0
                    
                    # Get forms
                    forms = await page.query_selector_all('form')
                    for form in forms:
                        form_data = {
                            'action': await form.get_attribute('action') or '',
                            'method': await form.get_attribute('method') or 'get',
                            'inputs': []
                        }
                        
                        inputs = await form.query_selector_all('input')
                        for inp in inputs:
                            input_type = await inp.get_attribute('type') or 'text'
                            input_name = await inp.get_attribute('name') or ''
                            form_data['inputs'].append({
                                'type': input_type,
                                'name': input_name
                            })
                            
                            if input_type == 'password':
                                result['has_login_form'] = True
                        
                        result['forms'].append(form_data)
                    
                except Exception as e:
                    result['error'] = str(e)
                
                await browser.close()
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def detect_form_fields(self, url: str) -> List[Dict]:
        """
        Detect form fields on a page for the poisoning bot.
        
        Returns:
            List of form field information
        """
        content = await self.extract_page_content(url)
        if not content or content.get('error'):
            return []
        
        fields = []
        for form in content.get('forms', []):
            for inp in form.get('inputs', []):
                fields.append({
                    'form_action': form['action'],
                    'form_method': form['method'],
                    'input_type': inp['type'],
                    'input_name': inp['name']
                })
        
        return fields


# Singleton instance
_screenshot_service = None

def get_screenshot_service() -> ScreenshotService:
    """Get the screenshot service singleton."""
    global _screenshot_service
    if _screenshot_service is None:
        _screenshot_service = ScreenshotService()
    return _screenshot_service


# ============================================================================
# API ROUTES (to be registered with Flask)
# ============================================================================

def create_screenshot_routes(bp):
    """Create screenshot routes for a Flask blueprint."""
    from flask import request, jsonify
    
    @bp.route('/screenshot', methods=['POST'])
    def capture_screenshot():
        """Capture a screenshot of a URL."""
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        service = get_screenshot_service()
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            screenshot = loop.run_until_complete(service.capture_screenshot(url))
        finally:
            loop.close()
        
        if screenshot:
            return jsonify({
                'url': url,
                'screenshot': base64.b64encode(screenshot).decode('utf-8'),
                'format': 'png'
            })
        else:
            return jsonify({'error': 'Failed to capture screenshot'}), 500
    
    @bp.route('/extract-content', methods=['POST'])
    def extract_content():
        """Extract page content and metadata."""
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        service = get_screenshot_service()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            content = loop.run_until_complete(service.extract_page_content(url))
        finally:
            loop.close()
        
        if content:
            return jsonify(content)
        else:
            return jsonify({'error': 'Failed to extract content'}), 500
