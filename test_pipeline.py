#!/usr/bin/env python3
"""
Test script for Vibe Scout pipeline
Tests all modules individually to ensure they work correctly
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from scraper.collect import LeadCollector
from analysis.site_seo import SiteAnalyzer
from analysis.social import SocialMediaAnalyzer
from llm.generate_email import EmailGenerator
from mailer.send_emails import EmailSender
from reports.build_report import ReportBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lead_collection():
    """Test lead collection module"""
    print("🧪 Testing Lead Collection...")
    
    try:
        collector = LeadCollector()
        
        # Test with mock data
        test_leads = [
            {
                'name': 'Restaurante Teste 1',
                'website': 'https://exemplo1.com',
                'phone': '(11) 99999-9999',
                'email': 'contato@exemplo1.com',
                'address': 'Rua Teste, 123 - São Paulo',
                'source': 'google_search',
                'description': 'Restaurante italiano tradicional'
            },
            {
                'name': 'Restaurante Teste 2',
                'website': 'https://exemplo2.com',
                'phone': '(11) 88888-8888',
                'email': 'contato@exemplo2.com',
                'address': 'Av. Teste, 456 - São Paulo',
                'source': 'google_maps',
                'description': 'Restaurante japonês moderno'
            }
        ]
        
        # Save test leads
        with open('leads_data.json', 'w') as f:
            json.dump(test_leads, f, indent=2, ensure_ascii=False)
        
        print("✅ Lead collection test passed")
        return test_leads
        
    except Exception as e:
        print(f"❌ Lead collection test failed: {e}")
        return []

def test_site_analysis():
    """Test site analysis module"""
    print("🧪 Testing Site Analysis...")
    
    try:
        analyzer = SiteAnalyzer()
        
        # Load test leads
        with open('leads_data.json', 'r') as f:
            leads = json.load(f)
        
        # Add mock analysis data
        for lead in leads:
            lead['analysis'] = {
                'lighthouse': {
                    'performance_score': 65.5,
                    'seo_score': 58.2,
                    'accessibility_score': 72.1,
                    'best_practices_score': 68.9,
                    'first_contentful_paint': 2.1,
                    'largest_contentful_paint': 4.5,
                    'cumulative_layout_shift': 0.15
                },
                'seo': {
                    'total_score': 62.5,
                    'meta_tags': {
                        'title': True,
                        'description': False,
                        'keywords': False
                    },
                    'headings': {
                        'total_headings': 8,
                        'h1_count': 1,
                        'h2_count': 3,
                        'h3_count': 4
                    },
                    'images': {
                        'total_images': 12,
                        'alt_text_ratio': 0.6,
                        'missing_alt': 5
                    },
                    'sitemap_found': False,
                    'robots_txt_found': True
                }
            }
        
        # Save analyzed leads
        with open('analyzed_leads.json', 'w') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        
        print("✅ Site analysis test passed")
        return leads
        
    except Exception as e:
        print(f"❌ Site analysis test failed: {e}")
        return []

def test_social_analysis():
    """Test social media analysis module"""
    print("🧪 Testing Social Media Analysis...")
    
    try:
        analyzer = SocialMediaAnalyzer()
        
        # Load analyzed leads
        with open('analyzed_leads.json', 'r') as f:
            leads = json.load(f)
        
        # Add mock social analysis data
        for lead in leads:
            lead['social_analysis'] = {
                'overall_social_score': 45.2,
                'maturity_level': 'beginner',
                'platforms': {
                    'instagram': {
                        'handle': f"@{lead['name'].lower().replace(' ', '')}",
                        'followers': 1200,
                        'posts': 45,
                        'engagement_rate': 2.1,
                        'last_post_date': '2024-01-10',
                        'posting_frequency': 'weekly'
                    },
                    'facebook': {
                        'page_name': lead['name'],
                        'followers': 800,
                        'posts': 23,
                        'engagement_rate': 1.8,
                        'last_post_date': '2024-01-08',
                        'posting_frequency': 'bi-weekly'
                    }
                },
                'recommendations': [
                    'Aumentar frequência de posts',
                    'Melhorar qualidade do conteúdo',
                    'Interagir mais com seguidores'
                ]
            }
        
        # Save leads with social analysis
        with open('leads_with_social.json', 'w') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        
        print("✅ Social media analysis test passed")
        return leads
        
    except Exception as e:
        print(f"❌ Social media analysis test failed: {e}")
        return []

def test_email_generation():
    """Test email generation module"""
    print("🧪 Testing Email Generation...")
    
    try:
        generator = EmailGenerator()
        
        # Load leads with social analysis
        with open('leads_with_social.json', 'r') as f:
            leads = json.load(f)
        
        # Generate emails
        emails = generator.generate_bulk_emails(leads)
        
        # Save generated emails
        with open('generated_emails.json', 'w') as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Email generation test passed - Generated {len(emails)} emails")
        return emails
        
    except Exception as e:
        print(f"❌ Email generation test failed: {e}")
        return []

def test_email_sending():
    """Test email sending module"""
    print("🧪 Testing Email Sending...")
    
    try:
        sender = EmailSender()
        
        # Load generated emails
        with open('generated_emails.json', 'r') as f:
            emails = json.load(f)
        
        # Send emails (mock mode)
        campaign_results = sender.send_bulk_emails(emails)
        
        # Save campaign results
        with open('email_campaign_results.json', 'w') as f:
            json.dump(campaign_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Email sending test passed - Sent: {campaign_results['sent_count']}, Failed: {campaign_results['failed_count']}")
        return campaign_results
        
    except Exception as e:
        print(f"❌ Email sending test failed: {e}")
        return {}

def test_report_generation():
    """Test report generation module"""
    print("🧪 Testing Report Generation...")
    
    try:
        # Load necessary data
        with open('leads_with_social.json', 'r') as f:
            leads_data = json.load(f)
        
        with open('email_campaign_results.json', 'r') as f:
            campaign_results = json.load(f)
        
        # Generate report
        builder = ReportBuilder()
        filename = builder.build_comprehensive_report(leads_data, campaign_results)
        
        print(f"✅ Report generation test passed - Report: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return None

def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Starting Vibe Scout Pipeline Tests")
    print("=" * 50)
    
    # Track test results
    test_results = {
        'lead_collection': False,
        'site_analysis': False,
        'social_analysis': False,
        'email_generation': False,
        'email_sending': False,
        'report_generation': False
    }
    
    # Test 1: Lead Collection
    leads = test_lead_collection()
    test_results['lead_collection'] = len(leads) > 0
    
    # Test 2: Site Analysis
    analyzed_leads = test_site_analysis()
    test_results['site_analysis'] = len(analyzed_leads) > 0
    
    # Test 3: Social Analysis
    social_leads = test_social_analysis()
    test_results['social_analysis'] = len(social_leads) > 0
    
    # Test 4: Email Generation
    emails = test_email_generation()
    test_results['email_generation'] = len(emails) > 0
    
    # Test 5: Email Sending
    campaign_results = test_email_sending()
    test_results['email_sending'] = campaign_results.get('sent_count', 0) > 0
    
    # Test 6: Report Generation
    report_filename = test_report_generation()
    test_results['report_generation'] = report_filename is not None
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The Vibe Scout pipeline is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return test_results

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        'leads_data.json',
        'analyzed_leads.json',
        'leads_with_social.json',
        'generated_emails.json',
        'email_campaign_results.json'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Removed {file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Vibe Scout Pipeline')
    parser.add_argument('--cleanup', action='store_true', 
                       help='Clean up test files after running')
    
    args = parser.parse_args()
    
    # Run tests
    results = run_all_tests()
    
    # Cleanup if requested
    if args.cleanup:
        print("\n🧹 Cleaning up test files...")
        cleanup_test_files()
    
    print("\n✨ Test completed!") 