#!/usr/bin/env python3
"""
Test script for rate limiting functionality
"""

import time
import logging
from utils.rate_limiter import groq_limiter, RateLimiter
from llm.generate_email import EmailGenerator
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_rate_limiter():
    """Test the rate limiter functionality"""
    logger.info("Testing rate limiter...")
    
    limiter = RateLimiter(max_requests=5, time_window=10, jitter=0.1)
    
    for i in range(10):
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        logger.info(f"Request {i+1}: {'Waited' if elapsed > 0.1 else 'Immediate'} ({elapsed:.2f}s)")

def test_groq_rate_limiting():
    """Test Groq API rate limiting with mock calls"""
    logger.info("Testing Groq rate limiting...")
    
    generator = EmailGenerator()
    
    # Create test leads
    test_leads = []
    for i in range(15):  # Test with 15 leads
        test_lead = {
            'name': f'Test Business {i+1}',
            'website': f'https://test{i+1}.com',
            'description': f'Test business description {i+1}',
            'site_analysis': {
                'lighthouse': {
                    'performance_score': 65.5,
                    'seo_score': 58.2,
                    'accessibility_score': 72.1,
                    'best_practices_score': 68.9
                },
                'seo': {
                    'total_score': 62.5,
                    'meta_tags': {'title': True, 'description': False},
                    'headings': {'total_headings': 8},
                    'images': {'alt_text_ratio': 0.6},
                    'sitemap_found': False
                }
            },
            'social_analysis': {
                'overall_social_score': 45.2,
                'platforms': {
                    'instagram': {
                        'followers': 1200,
                        'engagement_rate': 2.1
                    }
                }
            }
        }
        test_leads.append(test_lead)
    
    # Test bulk email generation
    logger.info(f"Generating emails for {len(test_leads)} test leads...")
    start_time = time.time()
    
    emails = generator.generate_bulk_emails(test_leads, test_mode=True)
    
    total_time = time.time() - start_time
    logger.info(f"Generated {len(emails)} emails in {total_time:.2f} seconds")
    logger.info(f"Average time per email: {total_time/len(emails):.2f} seconds")

def test_exponential_backoff():
    """Test exponential backoff functionality"""
    logger.info("Testing exponential backoff...")
    
    limiter = RateLimiter()
    
    for attempt in range(5):
        delay = limiter.exponential_backoff(attempt, base_delay=1.0, max_delay=30.0)
        logger.info(f"Attempt {attempt + 1}: Backoff delay = {delay:.2f} seconds")

if __name__ == "__main__":
    logger.info("Starting rate limiting tests...")
    
    try:
        # Test basic rate limiter
        test_rate_limiter()
        
        # Test exponential backoff
        test_exponential_backoff()
        
        # Test Groq rate limiting (only if API key is available)
        if os.getenv('GROQ_API_KEY'):
            test_groq_rate_limiting()
        else:
            logger.warning("GROQ_API_KEY not found. Skipping Groq API tests.")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise 