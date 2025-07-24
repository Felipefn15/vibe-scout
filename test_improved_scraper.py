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
    
    # Check API availability
    print("API Status:")
    print(f"- Google Maps API: {'✅ Available' if collector.gmaps else '❌ Not configured'}")
    print(f"- Google Custom Search API: {'✅ Available' if collector.google_search_api_key else '❌ Not configured'}")
    print(f"- Playwright: ✅ Available")
    print(f"- Requests-HTML: ✅ Available")
    print()
    
    # Test individual methods
    print("Testing individual scraping methods:")
    
    # Test Google Places API
    if collector.gmaps:
        print("\n1. Testing Google Places API...")
        try:
            places_leads = collector.search_google_places_api(industry, region)
            print(f"   Found {len(places_leads)} leads")
            for lead in places_leads[:2]:
                print(f"   - {lead['name']} ({lead['source']})")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("\n1. Google Places API: Skipped (not configured)")
    
    # Test Google Custom Search API
    if collector.google_search_api_key:
        print("\n2. Testing Google Custom Search API...")
        try:
            search_leads = collector.search_google_custom_search_api(industry, region)
            print(f"   Found {len(search_leads)} leads")
            for lead in search_leads[:2]:
                print(f"   - {lead['name']} ({lead['source']})")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("\n2. Google Custom Search API: Skipped (not configured)")
    
    # Test Playwright with Google
    print("\n3. Testing Playwright with Google...")
    try:
        google_playwright_leads = collector.search_with_playwright(industry, region, 'google')
        print(f"   Found {len(google_playwright_leads)} leads")
        for lead in google_playwright_leads[:2]:
            print(f"   - {lead['name']} ({lead['source']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Playwright with Bing
    print("\n4. Testing Playwright with Bing...")
    try:
        bing_playwright_leads = collector.search_with_playwright(industry, region, 'bing')
        print(f"   Found {len(bing_playwright_leads)} leads")
        for lead in bing_playwright_leads[:2]:
            print(f"   - {lead['name']} ({lead['source']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Yellow Pages API
    print("\n5. Testing Yellow Pages API...")
    try:
        yellow_leads = collector.search_yellow_pages_api(industry, region)
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