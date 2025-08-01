#!/usr/bin/env python3
"""
Test script to validate performance improvements
"""

import asyncio
import time
import json
from datetime import datetime
from utils.logger import get_logger
from utils.email_extractor import EmailExtractor
from scraper.collect import LeadCollector
from config.lead_filters import LeadFilter

logger = get_logger(__name__)

async def test_email_extraction():
    """Test email extraction functionality"""
    logger.info("🧪 Testing email extraction...")
    
    extractor = EmailExtractor()
    
    # Test cases
    test_cases = [
        {
            'name': 'Test Business',
            'website': 'https://example.com',
            'expected_pattern': 'contato@example.com'
        },
        {
            'name': 'Another Business',
            'website': 'https://testcompany.com.br',
            'expected_pattern': 'info@testcompany.com.br'
        }
    ]
    
    for case in test_cases:
        email = extractor._generate_common_email(case['website'], case['name'])
        logger.info(f"Generated email for {case['name']}: {email}")
        
        if email and extractor._is_valid_email(email):
            logger.info(f"✅ Valid email generated: {email}")
        else:
            logger.warning(f"⚠️ Invalid or no email generated for {case['name']}")

async def test_lead_filtering():
    """Test improved lead filtering"""
    logger.info("🧪 Testing lead filtering...")
    
    filter = LeadFilter()
    
    # Test cases - should be filtered out
    invalid_leads = [
        "Policlínicas - Canal Saúde - Prefeitura de Fortaleza",
        "Áreas da Medicina: veja especializações mais procuradas",
        "Moinhos de Vento é o 4º melhor hospital da América Latina",
        "Centro Médico em Curitiba | Consultas e Exames",
        "Guia Completo de Clínicas médicas em Curitiba",
        "Lista das Melhores Empresas do Setor",
        "Como marcar consulta - HCPA",
        "Home - Portal Hospital de Clínicas"
    ]
    
    # Test cases - should be valid
    valid_leads = [
        "Clínica Médica São José",
        "Advocacia Silva & Associados",
        "Restaurante Sabor Brasileiro",
        "Academia Fitness Center",
        "Imobiliária Horizonte",
        "Consultoria Empresarial ABC"
    ]
    
    logger.info("Testing invalid leads (should be filtered out):")
    for lead in invalid_leads:
        is_valid = filter.is_valid_business_name(lead)
        status = "❌ PASSED" if not is_valid else "⚠️ FAILED"
        logger.info(f"{status} - {lead}")
    
    logger.info("Testing valid leads (should pass):")
    for lead in valid_leads:
        is_valid = filter.is_valid_business_name(lead)
        status = "✅ PASSED" if is_valid else "❌ FAILED"
        logger.info(f"{status} - {lead}")

async def test_scraping_performance():
    """Test scraping performance improvements"""
    logger.info("🧪 Testing scraping performance...")
    
    collector = LeadCollector()
    
    # Test with a small sector to avoid long execution
    test_sector = "Academias"
    test_region = "São Paulo"
    
    start_time = time.time()
    
    try:
        leads = await collector.collect_leads(test_sector, test_region)
        duration = time.time() - start_time
        
        logger.info(f"✅ Scraping completed in {duration:.2f} seconds")
        logger.info(f"Found {len(leads)} leads")
        
        # Test email extraction on found leads
        if leads:
            extractor = EmailExtractor()
            leads_with_emails = await extractor.extract_emails_batch(leads[:3])  # Test first 3
            
            emails_found = sum(1 for lead in leads_with_emails if lead.get('email'))
            logger.info(f"Emails extracted: {emails_found}/{len(leads_with_emails)}")
            
            for lead in leads_with_emails:
                logger.info(f"Lead: {lead.get('name')} - Email: {lead.get('email', 'N/A')}")
        
    except Exception as e:
        logger.error(f"❌ Scraping test failed: {e}")

async def test_rate_limiting():
    """Test rate limiting improvements"""
    logger.info("🧪 Testing rate limiting...")
    
    from utils.rate_limiter import RateLimiter
    
    limiter = RateLimiter()
    
    # Test multiple rapid calls
    start_time = time.time()
    
    for i in range(5):
        await limiter.wait()
        logger.info(f"Rate limit call {i+1}")
    
    duration = time.time() - start_time
    logger.info(f"✅ Rate limiting test completed in {duration:.2f} seconds")

async def main():
    """Run all performance tests"""
    logger.info("🚀 Starting performance improvement tests...")
    
    start_time = time.time()
    
    # Run tests
    await test_email_extraction()
    await test_lead_filtering()
    await test_rate_limiting()
    await test_scraping_performance()
    
    total_duration = time.time() - start_time
    logger.info(f"✅ All tests completed in {total_duration:.2f} seconds")
    
    # Generate test report
    report = {
        'test_date': datetime.now().isoformat(),
        'total_duration': total_duration,
        'tests_run': [
            'email_extraction',
            'lead_filtering', 
            'rate_limiting',
            'scraping_performance'
        ],
        'status': 'completed'
    }
    
    with open('test_performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info("📊 Test report saved to test_performance_report.json")

if __name__ == "__main__":
    asyncio.run(main()) 