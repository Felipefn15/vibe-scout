#!/usr/bin/env python3
"""
Test Enhanced Web Scraper
Tests the improved web scraping solution
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.enhanced_web_scraper import EnhancedWebScraper
from scraper.web_problem_lead_collector import WebProblemLeadCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_enhanced_scraper():
    """Test the enhanced web scraper"""
    logger.info("Testing Enhanced Web Scraper...")
    
    try:
        async with EnhancedWebScraper(headless=True) as scraper:
            # Test 1: Basic search
            logger.info("Test 1: Basic search for 'dentista São Paulo'")
            leads = await scraper.search_multiple_sources("dentista", "São Paulo", max_results=10)
            logger.info(f"Found {len(leads)} leads from basic search")
            
            if leads:
                logger.info("Sample lead:")
                logger.info(json.dumps(leads[0], indent=2, ensure_ascii=False))
            
            # Test 2: Web problem detection
            logger.info("Test 2: Web problem detection")
            web_problem_leads = await scraper.search_google_for_problems("empresa sem site dentista São Paulo")
            logger.info(f"Found {len(web_problem_leads)} web problem leads from Google")
            
            maps_problem_leads = await scraper.search_google_maps_for_problems("negócio sem website São Paulo")
            logger.info(f"Found {len(maps_problem_leads)} web problem leads from Google Maps")
            
            # Test 3: Statistics
            stats = scraper.get_stats()
            logger.info("Scraper statistics:")
            logger.info(json.dumps(stats, indent=2))
            
            return True
            
    except Exception as e:
        logger.error(f"Enhanced scraper test failed: {e}")
        return False

async def test_web_problem_collector():
    """Test the web problem lead collector"""
    logger.info("Testing Web Problem Lead Collector...")
    
    try:
        async with WebProblemLeadCollector() as collector:
            # Test web problem lead collection
            logger.info("Collecting web problem leads for 'dentista' in 'São Paulo'")
            leads = await collector.collect_web_problem_leads("dentista", "São Paulo", max_leads=20)
            
            logger.info(f"Collected {len(leads)} web problem leads")
            
            if leads:
                logger.info("Sample web problem lead:")
                logger.info(json.dumps(leads[0], indent=2, ensure_ascii=False))
            
            # Get collection statistics
            stats = collector.get_collection_stats()
            logger.info("Collection statistics:")
            logger.info(json.dumps(stats, indent=2))
            
            return True
            
    except Exception as e:
        logger.error(f"Web problem collector test failed: {e}")
        return False

async def test_browser_simulator_fix():
    """Test that the browser simulator fix works"""
    logger.info("Testing Browser Simulator Fix...")
    
    try:
        from scraper.browser_simulator import BrowserSimulator
        
        async with BrowserSimulator() as simulator:
            # Test the fixed method
            logger.info("Testing extract_leads_from_screenshot method")
            
            # Test with a simple URL
            test_url = "https://www.google.com"
            screenshot_path = "test_screenshot.png"
            
            leads = await simulator.extract_leads_from_screenshot(test_url, screenshot_path)
            logger.info(f"Extracted {len(leads)} leads from test URL")
            
            # Clean up test screenshot
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            
            return True
            
    except Exception as e:
        logger.error(f"Browser simulator fix test failed: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("Starting Enhanced Web Scraping Tests")
    logger.info("=" * 50)
    
    results = []
    
    # Test 1: Enhanced Web Scraper
    logger.info("\n1. Testing Enhanced Web Scraper")
    result1 = await test_enhanced_scraper()
    results.append(("Enhanced Web Scraper", result1))
    
    # Test 2: Web Problem Lead Collector
    logger.info("\n2. Testing Web Problem Lead Collector")
    result2 = await test_web_problem_collector()
    results.append(("Web Problem Lead Collector", result2))
    
    # Test 3: Browser Simulator Fix
    logger.info("\n3. Testing Browser Simulator Fix")
    result3 = await test_browser_simulator_fix()
    results.append(("Browser Simulator Fix", result3))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("\n" + "=" * 50)
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED! Enhanced web scraping solution is working.")
    else:
        logger.error("❌ SOME TESTS FAILED. Please check the logs above.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1) 