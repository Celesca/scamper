#!/usr/bin/env python3
"""
POISONING BOT - Active Defense System
======================================
Pollutes phishing databases with fake credentials.
DEMO MODE: Logs actions without actually submitting.
"""

import logging
import random
import string
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger('POISONING_BOT')

# Try to import faker for realistic fake data
try:
    from faker import Faker
    fake = Faker(['th_TH', 'en_US'])
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False
    logger.warning("Faker not installed. Using basic fake data generation.")


@dataclass
class FakeCredential:
    """A fake credential to inject into phishing forms."""
    username: str
    email: str
    password: str
    phone: str
    id_card: str  # Thai national ID format
    credit_card: str
    created_at: str


class FakeDataGenerator:
    """Generate realistic-looking fake data for poisoning attacks."""
    
    THAI_FIRST_NAMES = [
        'สมชาย', 'สมหญิง', 'วิชัย', 'วิภา', 'ประเสริฐ', 'ประภา',
        'สุชาติ', 'สุภาพร', 'ธนกร', 'ธนพร', 'พิชัย', 'พิมพ์', 'อรุณ', 'อรุณี'
    ]
    
    THAI_LAST_NAMES = [
        'สุขสวัสดิ์', 'จันทร์เพ็ญ', 'พรหมมา', 'ศรีสุข', 'วงศ์สกุล',
        'เจริญรุ่ง', 'มีโชค', 'รักษาศีล', 'ประเสริฐ', 'เกษมศานต์'
    ]
    
    EMAIL_DOMAINS = [
        'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
        'mail.com', 'protonmail.com', 'icloud.com'
    ]
    
    PHONE_PREFIXES = ['08', '09', '06']
    
    def __init__(self):
        self.generated_count = 0
    
    def _random_string(self, length: int, include_numbers: bool = True) -> str:
        """Generate a random string."""
        chars = string.ascii_lowercase
        if include_numbers:
            chars += string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _generate_thai_name(self) -> tuple:
        """Generate a Thai name."""
        if HAS_FAKER:
            return fake.first_name(), fake.last_name()
        return random.choice(self.THAI_FIRST_NAMES), random.choice(self.THAI_LAST_NAMES)
    
    def _generate_email(self, name: str) -> str:
        """Generate an email address."""
        if HAS_FAKER:
            return fake.email()
        username = name.lower().replace(' ', '.') + str(random.randint(1, 999))
        domain = random.choice(self.EMAIL_DOMAINS)
        return f"{username}@{domain}"
    
    def _generate_password(self) -> str:
        """Generate a realistic-looking password."""
        patterns = [
            lambda: f"{self._random_string(6)}@{random.randint(1, 99)}",
            lambda: f"{random.choice(['love', 'pass', 'pwd', 'hello'])}{random.randint(1000, 9999)}",
            lambda: self._random_string(8, include_numbers=True),
            lambda: f"{self._random_string(4)}_{random.randint(100, 999)}",
        ]
        return random.choice(patterns)()
    
    def _generate_thai_phone(self) -> str:
        """Generate a Thai phone number."""
        if HAS_FAKER:
            return fake.phone_number()
        prefix = random.choice(self.PHONE_PREFIXES)
        return f"{prefix}{random.randint(10000000, 99999999)}"
    
    def _generate_thai_id(self) -> str:
        """Generate a fake Thai National ID (13 digits)."""
        # Format: X-XXXX-XXXXX-XX-X
        return f"{random.randint(1, 8)}{random.randint(1000, 9999)}{random.randint(10000, 99999)}{random.randint(10, 99)}{random.randint(0, 9)}"
    
    def _generate_credit_card(self) -> str:
        """Generate a fake credit card number (passes Luhn check but invalid)."""
        # Generate a fake card that looks real but isn't
        prefix = random.choice(['4', '5', '3'])  # Visa, Mastercard, Amex-ish
        base = prefix + ''.join(str(random.randint(0, 9)) for _ in range(14))
        # Add random check digit (won't pass Luhn, but looks real)
        return base + str(random.randint(0, 9))
    
    def generate_credential(self) -> FakeCredential:
        """Generate a single fake credential."""
        first_name, last_name = self._generate_thai_name()
        full_name = f"{first_name} {last_name}"
        
        credential = FakeCredential(
            username=self._random_string(8),
            email=self._generate_email(full_name),
            password=self._generate_password(),
            phone=self._generate_thai_phone(),
            id_card=self._generate_thai_id(),
            credit_card=self._generate_credit_card(),
            created_at=datetime.now().isoformat()
        )
        
        self.generated_count += 1
        return credential
    
    def generate_batch(self, count: int = 100) -> List[FakeCredential]:
        """Generate a batch of fake credentials."""
        return [self.generate_credential() for _ in range(count)]


class PoisoningBot:
    """
    Active defense bot that pollutes phishing databases.
    
    WARNING: This is for educational/demonstration purposes only.
    In production, use DEMO_MODE=True to log actions without submitting.
    """
    
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.generator = FakeDataGenerator()
        self.actions_log: List[Dict] = []
    
    def _log_action(self, action: str, details: Dict):
        """Log an action for tracking."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'demo_mode': self.demo_mode,
            **details
        }
        self.actions_log.append(entry)
        logger.info(f"[{'DEMO' if self.demo_mode else 'LIVE'}] {action}: {details}")
    
    async def _submit_form(self, url: str, form_data: Dict) -> bool:
        """
        Submit form data to the target URL.
        In demo mode, this just logs the action.
        """
        self._log_action('SUBMIT_FORM', {
            'url': url,
            'fields': list(form_data.keys())
        })
        
        if self.demo_mode:
            return True
        
        # In non-demo mode, would use aiohttp to submit
        # This is intentionally not implemented for safety
        logger.warning("Non-demo mode is not implemented for safety reasons")
        return False
    
    async def poison_site(self, url: str, credentials_count: int = 100) -> Dict:
        """
        Poison a phishing site with fake credentials.
        
        Args:
            url: The phishing site URL
            credentials_count: Number of fake credentials to generate
            
        Returns:
            Report of poisoning operation
        """
        self._log_action('START_POISONING', {
            'url': url,
            'target_count': credentials_count
        })
        
        # Try to extract form fields
        from screenshot_service import get_screenshot_service
        service = get_screenshot_service()
        
        try:
            fields = await service.detect_form_fields(url)
        except Exception as e:
            logger.error(f"Failed to detect form fields: {e}")
            fields = []
        
        # Generate fake credentials
        credentials = self.generator.generate_batch(credentials_count)
        
        submitted = 0
        failed = 0
        
        for cred in credentials:
            cred_dict = asdict(cred)
            
            # Map credential fields to detected form fields
            form_data = {}
            for field in fields:
                name = field.get('input_name', '').lower()
                if 'user' in name or 'login' in name:
                    form_data[field['input_name']] = cred_dict['username']
                elif 'email' in name or 'mail' in name:
                    form_data[field['input_name']] = cred_dict['email']
                elif 'pass' in name or 'pwd' in name:
                    form_data[field['input_name']] = cred_dict['password']
                elif 'phone' in name or 'tel' in name:
                    form_data[field['input_name']] = cred_dict['phone']
                elif 'card' in name or 'credit' in name:
                    form_data[field['input_name']] = cred_dict['credit_card']
            
            # If no fields detected, use common field names
            if not form_data:
                form_data = {
                    'username': cred_dict['username'],
                    'email': cred_dict['email'],
                    'password': cred_dict['password']
                }
            
            success = await self._submit_form(url, form_data)
            if success:
                submitted += 1
            else:
                failed += 1
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        report = {
            'url': url,
            'demo_mode': self.demo_mode,
            'credentials_generated': len(credentials),
            'form_fields_detected': len(fields),
            'submissions_attempted': submitted,
            'submissions_failed': failed,
            'completed_at': datetime.now().isoformat()
        }
        
        self._log_action('COMPLETE_POISONING', report)
        
        return report
    
    def get_sample_credentials(self, count: int = 10) -> List[Dict]:
        """Get sample fake credentials for display."""
        credentials = self.generator.generate_batch(count)
        return [asdict(c) for c in credentials]
    
    def get_action_log(self) -> List[Dict]:
        """Get the action log."""
        return self.actions_log


# Singleton instance (always in demo mode for safety)
_poisoning_bot = None

def get_poisoning_bot(demo_mode: bool = True) -> PoisoningBot:
    """Get the poisoning bot singleton."""
    global _poisoning_bot
    if _poisoning_bot is None or _poisoning_bot.demo_mode != demo_mode:
        _poisoning_bot = PoisoningBot(demo_mode=demo_mode)
    return _poisoning_bot


# ============================================================================
# API ROUTES
# ============================================================================

def create_poisoning_routes(bp):
    """Create poisoning bot routes for a Flask blueprint."""
    from flask import request, jsonify
    
    @bp.route('/poison', methods=['POST'])
    def poison_site():
        """Start a poisoning operation (demo mode only)."""
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        count = data.get('count', 100)
        
        # Always use demo mode for safety
        bot = get_poisoning_bot(demo_mode=True)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            report = loop.run_until_complete(bot.poison_site(url, count))
        finally:
            loop.close()
        
        return jsonify(report)
    
    @bp.route('/sample-credentials', methods=['GET'])
    def get_sample_credentials():
        """Get sample fake credentials for display."""
        count = request.args.get('count', 10, type=int)
        bot = get_poisoning_bot()
        samples = bot.get_sample_credentials(min(count, 100))
        return jsonify({'credentials': samples})
    
    @bp.route('/action-log', methods=['GET'])
    def get_action_log():
        """Get the poisoning action log."""
        bot = get_poisoning_bot()
        return jsonify({'log': bot.get_action_log()})
