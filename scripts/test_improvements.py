#!/usr/bin/env python3
"""
Test script for the improvements implemented
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.lead_filters import LeadFilters
from scheduler.daily_campaign import DailyCampaignScheduler

def test_lead_filters():
    """Test the improved lead filters"""
    print("🔍 Testing Lead Filters...")
    
    filters = LeadFilters()
    
    # Test cases
    test_cases = [
        # Should be rejected (generic/ranking)
        ("Oficinas em Recife", False),
        ("Os 10 maiores escritórios", False),
        ("Advocacia", False),
        ("Oficinas", False),
        ("Padarias", False),
        
        # Should be accepted (specific businesses)
        ("Silva & Associados Advocacia", True),
        ("Auto Center Recife Ltda", True),
        ("Padaria Vianney", True),
        ("Clínica Médica Dr. João", True),
        ("Escritório de Advocacia Santos", True),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for lead_name, expected in test_cases:
        result = filters.is_valid_business(lead_name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{lead_name}' -> {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\n📊 Lead Filter Accuracy: {passed}/{total} ({passed/total*100:.1f}%)")
    return passed == total

def test_sectors():
    """Test the improved sectors configuration"""
    print("\n🎯 Testing Sectors Configuration...")
    
    try:
        with open('config/sectors.json', 'r', encoding='utf-8') as f:
            sectors = json.load(f)
        
        high_value = [s for s in sectors if s.get('priority') == 'high']
        medium_value = [s for s in sectors if s.get('priority') == 'medium']
        low_value = [s for s in sectors if s.get('priority') == 'low']
        
        print(f"✅ High-value sectors: {len(high_value)}")
        for sector in high_value:
            print(f"   - {sector['name']}")
        
        print(f"✅ Medium-value sectors: {len(medium_value)}")
        for sector in medium_value:
            print(f"   - {sector['name']}")
        
        print(f"✅ Low-value sectors: {len(low_value)}")
        for sector in low_value:
            print(f"   - {sector['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sectors: {e}")
        return False

def test_regions():
    """Test the improved regions configuration"""
    print("\n🏙️ Testing Regions Configuration...")
    
    scheduler = DailyCampaignScheduler()
    regions = scheduler.regions
    
    print(f"✅ Total regions: {len(regions)}")
    print("Top 5 regions (highest ROI):")
    for i, region in enumerate(regions[:5], 1):
        print(f"   {i}. {region}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Vibe Scout Improvements")
    print("=" * 50)
    
    tests = [
        ("Lead Filters", test_lead_filters),
        ("Sectors Configuration", test_sectors),
        ("Regions Configuration", test_regions),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All improvements working correctly!")
    else:
        print("⚠️ Some improvements need attention")

if __name__ == "__main__":
    main() 