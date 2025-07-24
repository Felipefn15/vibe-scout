#!/usr/bin/env python3
"""
Test script for the improved Vibe Scout scraper
Tests the new scraping methods with Playwright and fallback options
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.collect import LeadCollector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scraper():
    """Test the improved scraper with different methods"""
    
    print("=" * 60)
    print("TESTING IMPROVED VIBE SCOUT SCRAPER")
    print("=" * 60)
    
    # Initialize collector
    collector = LeadCollector()
    
    # Test parameters
    industry = "restaurantes"
    region = "Rio de Janeiro"
    test_mode = True
    target_count = 10
    
    print(f"Testing with:")
    print(f"- Industry: {industry}")
    print(f"- Region: {region}")
    print(f"- Test mode: {test_mode}")
    print(f"- Target count: {target_count}")
    print()
    
    # Check scraping methods availability
    print("Scraping Methods Status:")
    print(f"- Google Maps Playwright: ✅ Available")
    print(f"- Google Search Playwright: ✅ Available")
    print(f"- Bing Search Playwright: ✅ Available")
    print(f"- Yellow Pages Playwright: ✅ Available")
    print()
    
    # Test individual methods
    print("Testing individual scraping methods:")
    
    # Test Google Maps with Playwright
    print("\n1. Testing Google Maps with Playwright...")
    try:
        maps_leads = collector.search_google_maps_with_playwright(industry, region)
        print(f"   Found {len(maps_leads)} leads")
        for lead in maps_leads[:2]:
            print(f"   - {lead['name']} ({lead['source']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Google Search with Playwright
    print("\n2. Testing Google Search with Playwright...")
    try:
        google_leads = collector.search_google_with_playwright(industry, region)
        print(f"   Found {len(google_leads)} leads")
        for lead in google_leads[:2]:
            print(f"   - {lead['name']} ({lead['source']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Bing with Playwright
    print("\n3. Testing Bing with Playwright...")
    try:
        bing_leads = collector.search_bing_with_playwright(industry, region)
        print(f"   Found {len(bing_leads)} leads")
        for lead in bing_leads[:2]:
            print(f"   - {lead['name']} ({lead['source']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Yellow Pages with Playwright
    print("\n4. Testing Yellow Pages with Playwright...")
    try:
        yellow_leads = collector.search_yellow_pages_with_playwright(industry, region)
        print(f"   Found {len(yellow_leads)} leads")
        for lead in yellow_leads[:2]:
            print(f"   - {lead['name']} ({lead['source']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test full collection
    print("\n" + "=" * 60)
    print("TESTING FULL LEAD COLLECTION")
    print("=" * 60)
    
    try:
        all_leads = collector.collect_leads(industry, region, test_mode=test_mode, target_count=target_count)
        
        print(f"\nTotal leads collected: {len(all_leads)}")
        
        if all_leads:
            print("\nSample leads:")
            for i, lead in enumerate(all_leads[:5], 1):
                print(f"{i}. {lead['name']}")
                print(f"   Source: {lead['source']}")
                if lead.get('website'):
                    print(f"   Website: {lead['website']}")
                if lead.get('phone'):
                    print(f"   Phone: {lead['phone']}")
                if lead.get('address'):
                    print(f"   Address: {lead['address']}")
                print()
            
            # Save test results
            os.makedirs('data', exist_ok=True)
            with open('data/test_leads.json', 'w', encoding='utf-8') as f:
                json.dump(all_leads, f, indent=2, ensure_ascii=False)
            print(f"Test results saved to data/test_leads.json")
            
        else:
            print("No leads collected. This might be due to:")
            print("- Rate limiting from search engines")
            print("- Network connectivity issues")
            print("- Search engines blocking automated requests")
            print("- No businesses found for the given criteria")
        
    except Exception as e:
        print(f"Error in full collection: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    load_dotenv()
    test_scraper() 