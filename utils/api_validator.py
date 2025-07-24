#!/usr/bin/env python3
"""
API Key Validator for Vibe Scout
Validates and tests API keys for external services
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class APIKeyValidator:
    """Validates API keys and provides status information"""
    
    def __init__(self):
        self.api_keys = {}
        self.validation_results = {}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load all API keys from environment"""
        self.api_keys = {
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
            'SENDGRID_API_KEY': os.getenv('SENDGRID_API_KEY'),
            'FROM_EMAIL': os.getenv('FROM_EMAIL'),
            'FROM_NAME': os.getenv('FROM_NAME'),
            'RAILWAY_API_KEY': os.getenv('RAILWAY_API_KEY')
        }
    
    def validate_all(self) -> Dict[str, bool]:
        """Validate all API keys"""
        results = {}
        
        # Validate Groq API Key
        results['groq'] = self._validate_groq_key()
        
        # Validate SendGrid API Key
        results['sendgrid'] = self._validate_sendgrid_key()
        
        # Validate Email Configuration
        results['email_config'] = self._validate_email_config()
        
        # Validate Railway API Key
        results['railway'] = self._validate_railway_key()
        
        self.validation_results = results
        return results
    
    def _validate_groq_key(self) -> bool:
        """Validate Groq API key format"""
        groq_key = self.api_keys.get('GROQ_API_KEY')
        
        if not groq_key:
            logger.warning("GROQ_API_KEY not found in environment")
            return False
        
        if not groq_key.startswith('gsk_'):
            logger.warning("GROQ_API_KEY format appears invalid (should start with 'gsk_')")
            return False
        
        if len(groq_key) < 20:
            logger.warning("GROQ_API_KEY appears too short")
            return False
        
        logger.info("GROQ_API_KEY format appears valid")
        return True
    
    def _validate_sendgrid_key(self) -> bool:
        """Validate SendGrid API key format"""
        sendgrid_key = self.api_keys.get('SENDGRID_API_KEY')
        
        if not sendgrid_key:
            logger.warning("SENDGRID_API_KEY not found in environment")
            return False
        
        if not sendgrid_key.startswith('SG.'):
            logger.warning("SENDGRID_API_KEY format appears invalid (should start with 'SG.')")
            return False
        
        if len(sendgrid_key) < 50:
            logger.warning("SENDGRID_API_KEY appears too short")
            return False
        
        logger.info("SENDGRID_API_KEY format appears valid")
        return True
    
    def _validate_email_config(self) -> bool:
        """Validate email configuration"""
        from_email = self.api_keys.get('FROM_EMAIL')
        from_name = self.api_keys.get('FROM_NAME')
        
        if not from_email:
            logger.warning("FROM_EMAIL not found in environment")
            return False
        
        if '@' not in from_email:
            logger.warning("FROM_EMAIL format appears invalid")
            return False
        
        if not from_name:
            logger.warning("FROM_NAME not found in environment")
            return False
        
        logger.info("Email configuration appears valid")
        return True
    
    def _validate_railway_key(self) -> bool:
        """Validate Railway API key format"""
        railway_key = self.api_keys.get('RAILWAY_API_KEY')
        
        if not railway_key:
            logger.warning("RAILWAY_API_KEY not found in environment")
            return False
        
        if len(railway_key) < 20:
            logger.warning("RAILWAY_API_KEY appears too short")
            return False
        
        logger.info("RAILWAY_API_KEY format appears valid")
        return True
    
    def test_groq_connection(self) -> bool:
        """Test Groq API connection"""
        try:
            import groq
            
            if not self.api_keys.get('GROQ_API_KEY'):
                logger.error("Cannot test Groq connection: API key not found")
                return False
            
            client = groq.Groq(api_key=self.api_keys['GROQ_API_KEY'])
            
            # Simple test call
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama3-8b-8192",
                max_tokens=10
            )
            
            logger.info("Groq API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Groq API connection test failed: {e}")
            return False
    
    def test_sendgrid_connection(self) -> bool:
        """Test SendGrid API connection"""
        try:
            from sendgrid import SendGridAPIClient
            
            if not self.api_keys.get('SENDGRID_API_KEY'):
                logger.error("Cannot test SendGrid connection: API key not found")
                return False
            
            sg = SendGridAPIClient(api_key=self.api_keys['SENDGRID_API_KEY'])
            
            # Test API key validity by getting account info
            response = sg.client.user.account.get()
            
            if response.status_code == 200:
                logger.info("SendGrid API connection test successful")
                return True
            else:
                logger.error(f"SendGrid API test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid API connection test failed: {e}")
            return False
    
    def get_status_report(self) -> Dict:
        """Get comprehensive status report"""
        validation_results = self.validate_all()
        
        report = {
            'validation_results': validation_results,
            'missing_keys': [],
            'invalid_keys': [],
            'working_services': [],
            'broken_services': []
        }
        
        # Check for missing keys
        for key_name, key_value in self.api_keys.items():
            if not key_value:
                report['missing_keys'].append(key_name)
        
        # Categorize services
        if validation_results.get('groq'):
            if self.test_groq_connection():
                report['working_services'].append('Groq')
            else:
                report['broken_services'].append('Groq')
        else:
            report['broken_services'].append('Groq')
        
        if validation_results.get('sendgrid'):
            if self.test_sendgrid_connection():
                report['working_services'].append('SendGrid')
            else:
                report['broken_services'].append('SendGrid')
        else:
            report['broken_services'].append('SendGrid')
        
        return report
    
    def print_status_report(self):
        """Print a formatted status report"""
        report = self.get_status_report()
        
        print("\n" + "="*60)
        print("🔑 API KEY VALIDATION REPORT")
        print("="*60)
        
        # Validation Results
        print("\n📋 VALIDATION RESULTS:")
        for service, is_valid in report['validation_results'].items():
            status = "✅ VALID" if is_valid else "❌ INVALID"
            print(f"  {service.upper()}: {status}")
        
        # Missing Keys
        if report['missing_keys']:
            print(f"\n❌ MISSING API KEYS:")
            for key in report['missing_keys']:
                print(f"  - {key}")
        
        # Working Services
        if report['working_services']:
            print(f"\n✅ WORKING SERVICES:")
            for service in report['working_services']:
                print(f"  - {service}")
        
        # Broken Services
        if report['broken_services']:
            print(f"\n❌ BROKEN SERVICES:")
            for service in report['broken_services']:
                print(f"  - {service}")
        
        print("\n" + "="*60)

def main():
    """Main function for testing"""
    validator = APIKeyValidator()
    validator.print_status_report()

if __name__ == "__main__":
    main() 