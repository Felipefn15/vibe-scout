#!/usr/bin/env python3
"""
Test System Fixes - Vibe Scout
Tests all the fixes implemented based on log analysis
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_validator import APIKeyValidator
from utils.rate_limiter import RateLimiter
from config.lead_filters import LeadFilters
from scraper.collect import LeadCollector
from analysis.site_seo import SiteSEOAnalyzer
from analysis.social import SocialMediaAnalyzer
from llm.generate_email import EmailGenerator
from email_sender.sendgrid_sender import SendGridSender

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemFixTester:
    """Test all system fixes"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
    
    def test_rate_limiter(self) -> bool:
        """Test Rate Limiter fix"""
        logger.info("🔧 Testing Rate Limiter fix...")
        
        try:
            # Test basic rate limiter
            limiter = RateLimiter(max_requests=5, time_window=10)
            
            # Test wait method (the fix)
            limiter.wait()
            logger.info("✅ Rate Limiter wait method works")
            
            # Test wait_if_needed method
            limiter.wait_if_needed()
            logger.info("✅ Rate Limiter wait_if_needed method works")
            
            # Test exponential backoff
            delay = limiter.exponential_backoff(1)
            logger.info(f"✅ Rate Limiter exponential backoff works: {delay:.2f}s")
            
            self.test_results['rate_limiter'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Rate Limiter test failed: {e}")
            self.test_results['rate_limiter'] = False
            return False
    
    def test_lead_filters(self) -> bool:
        """Test improved lead filters"""
        logger.info("🔧 Testing improved lead filters...")
        
        try:
            # Test invalid lead detection
            invalid_leads = [
                "As melhores empresas do setor de Jurídico – Rio de Janeiro - Glassdoor",
                "Como consultar a OAB de um advogado? Passo a passo - Estácio",
                "Os 10 maiores escritórios de advocacia de São Paulo",
                "Advogado: Estado do RJ - Salário",
                "Padarias em Belo Horizonte para se deliciar de pães e..."
            ]
            
            valid_leads = [
                "Garcia Advogados",
                "Basilio Advogados",
                "Padaria Vianney",
                "Restaurante São Paulo"
            ]
            
            # Load filters
            filters = LeadFilters()
            
            # Test invalid leads
            invalid_count = 0
            for lead in invalid_leads:
                if not filters.is_valid_business(lead):
                    invalid_count += 1
                    logger.info(f"✅ Correctly filtered invalid lead: {lead[:50]}...")
                else:
                    logger.warning(f"❌ Failed to filter invalid lead: {lead[:50]}...")
            
            # Test valid leads
            valid_count = 0
            for lead in valid_leads:
                if filters.is_valid_business(lead):
                    valid_count += 1
                    logger.info(f"✅ Correctly accepted valid lead: {lead}")
                else:
                    logger.warning(f"❌ Incorrectly filtered valid lead: {lead}")
            
            success_rate = (invalid_count / len(invalid_leads)) * 100
            logger.info(f"✅ Lead filter test: {invalid_count}/{len(invalid_leads)} invalid leads filtered ({success_rate:.1f}%)")
            
            self.test_results['lead_filters'] = success_rate >= 80
            return success_rate >= 80
            
        except Exception as e:
            logger.error(f"❌ Lead filters test failed: {e}")
            self.test_results['lead_filters'] = False
            return False
    
    def test_api_keys(self) -> bool:
        """Test API key validation"""
        logger.info("🔧 Testing API key validation...")
        
        try:
            validator = APIKeyValidator()
            validation_results = validator.validate_all()
            
            # Check if at least some keys are valid
            valid_keys = sum(validation_results.values())
            total_keys = len(validation_results)
            
            logger.info(f"✅ API key validation: {valid_keys}/{total_keys} keys valid")
            
            # Print detailed report
            validator.print_status_report()
            
            self.test_results['api_keys'] = valid_keys > 0
            return valid_keys > 0
            
        except Exception as e:
            logger.error(f"❌ API key validation test failed: {e}")
            self.test_results['api_keys'] = False
            return False
    
    def test_analysis_modules(self) -> bool:
        """Test analysis modules for missing methods"""
        logger.info("🔧 Testing analysis modules...")
        
        try:
            # Test SiteSEOAnalyzer
            site_analyzer = SiteSEOAnalyzer()
            
            # Check if analyze_website method exists
            if hasattr(site_analyzer, 'analyze_website'):
                logger.info("✅ SiteSEOAnalyzer.analyze_website method exists")
            else:
                logger.error("❌ SiteSEOAnalyzer.analyze_website method missing")
                return False
            
            # Test SocialMediaAnalyzer
            social_analyzer = SocialMediaAnalyzer()
            
            # Check if analyze_social_media_for_leads method exists
            if hasattr(social_analyzer, 'analyze_social_media_for_leads'):
                logger.info("✅ SocialMediaAnalyzer.analyze_social_media_for_leads method exists")
            else:
                logger.error("❌ SocialMediaAnalyzer.analyze_social_media_for_leads method missing")
                return False
            
            self.test_results['analysis_modules'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Analysis modules test failed: {e}")
            self.test_results['analysis_modules'] = False
            return False
    
    def test_email_generation(self) -> bool:
        """Test email generation"""
        logger.info("🔧 Testing email generation...")
        
        try:
            email_gen = EmailGenerator()
            
            # Test generate_email method (alias)
            if hasattr(email_gen, 'generate_email'):
                logger.info("✅ EmailGenerator.generate_email method exists")
            else:
                logger.error("❌ EmailGenerator.generate_email method missing")
                return False
            
            # Test generate_personalized_email method
            if hasattr(email_gen, 'generate_personalized_email'):
                logger.info("✅ EmailGenerator.generate_personalized_email method exists")
            else:
                logger.error("❌ EmailGenerator.generate_personalized_email method missing")
                return False
            
            self.test_results['email_generation'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Email generation test failed: {e}")
            self.test_results['email_generation'] = False
            return False
    
    def test_sendgrid_sender(self) -> bool:
        """Test SendGrid sender"""
        logger.info("🔧 Testing SendGrid sender...")
        
        try:
            sender = SendGridSender()
            
            # Check if send_email method exists
            if hasattr(sender, 'send_email'):
                logger.info("✅ SendGridSender.send_email method exists")
            else:
                logger.error("❌ SendGridSender.send_email method missing")
                return False
            
            self.test_results['sendgrid_sender'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ SendGrid sender test failed: {e}")
            self.test_results['sendgrid_sender'] = False
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting comprehensive system fix tests...")
        
        tests = [
            ("Rate Limiter", self.test_rate_limiter),
            ("Lead Filters", self.test_lead_filters),
            ("API Keys", self.test_api_keys),
            ("Analysis Modules", self.test_analysis_modules),
            ("Email Generation", self.test_email_generation),
            ("SendGrid Sender", self.test_sendgrid_sender)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*60}")
            logger.info(f"🧪 Running test: {test_name}")
            logger.info(f"{'='*60}")
            
            try:
                if test_func():
                    passed += 1
                    logger.info(f"✅ {test_name} test PASSED")
                else:
                    logger.error(f"❌ {test_name} test FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name} test ERROR: {e}")
        
        # Print summary
        self.print_summary(passed, total)
        
        return passed == total
    
    def print_summary(self, passed: int, total: int):
        """Print test summary"""
        logger.info(f"\n{'='*60}")
        logger.info("📊 TEST SUMMARY")
        logger.info(f"{'='*60}")
        
        success_rate = (passed / total) * 100
        
        logger.info(f"✅ Tests Passed: {passed}/{total}")
        logger.info(f"❌ Tests Failed: {total - passed}/{total}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("🎉 System is ready for deployment!")
        elif success_rate >= 60:
            logger.warning("⚠️  System has some issues but may work")
        else:
            logger.error("🚨 System has critical issues that need fixing")
        
        # Detailed results
        logger.info(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
        
        logger.info(f"\n⏱️  Total test time: {datetime.now() - self.start_time}")

def main():
    """Main function"""
    tester = SystemFixTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! System is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please fix the issues.")
        sys.exit(1)

if __name__ == "__main__":
    main() 