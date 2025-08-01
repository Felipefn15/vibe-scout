#!/usr/bin/env python3
"""
Test Web Problem Lead Collector
Test the new specialized collector for businesses with web visibility issues
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.web_problem_lead_collector import WebProblemLeadCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web_problem_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def test_web_problem_collector():
    """Test the web problem lead collector"""
    
    # Test parameters
    sector = "restaurante"
    region = "São Paulo"
    max_leads = 20
    
    logger.info(f"Testing Web Problem Lead Collector")
    logger.info(f"Sector: {sector}")
    logger.info(f"Region: {region}")
    logger.info(f"Max leads: {max_leads}")
    
    try:
        # Initialize collector
        async with WebProblemLeadCollector() as collector:
            logger.info("Collector initialized successfully")
            
            # Collect leads
            logger.info("Starting lead collection...")
            leads = await collector.collect_web_problem_leads(
                sector=sector,
                region=region,
                max_leads=max_leads
            )
            
            # Display results
            logger.info(f"Collection completed. Found {len(leads)} leads")
            
            # Show statistics
            stats = collector.get_collection_stats()
            logger.info("Collection Statistics:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")
            
            # Display leads
            if leads:
                logger.info("\nTop 10 Leads:")
                for i, lead in enumerate(leads[:10], 1):
                    logger.info(f"\n{i}. {lead.get('name', 'Unknown')}")
                    logger.info(f"   Score: {lead.get('web_problem_score', 0)}")
                    logger.info(f"   Priority: {lead.get('priority_level', 'unknown')}")
                    logger.info(f"   Web Problems: {lead.get('web_problems', [])}")
                    logger.info(f"   SEO Score: {lead.get('seo_score', 'N/A')}")
                    logger.info(f"   Website: {lead.get('website', 'No website')}")
                    logger.info(f"   Email: {lead.get('email', 'No email')}")
                    logger.info(f"   Phone: {lead.get('phone', 'No phone')}")
                    
                    # Show website analysis if available
                    if lead.get('website_analysis'):
                        analysis = lead['website_analysis']
                        logger.info(f"   Digital Maturity: {analysis.get('digital_maturity', 'unknown')}")
                        logger.info(f"   IT Needs Score: {analysis.get('it_needs_score', 0)}")
                        logger.info(f"   Pain Points: {analysis.get('pain_points', [])}")
                        logger.info(f"   Opportunities: {analysis.get('opportunities', [])}")
            
            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"data/web_problem_leads_{sector}_{region}_{timestamp}.json"
            
            # Prepare results for saving
            results = {
                'metadata': {
                    'sector': sector,
                    'region': region,
                    'max_leads': max_leads,
                    'timestamp': timestamp,
                    'collection_stats': stats
                },
                'leads': leads
            }
            
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Save to file
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Results saved to: {results_file}")
            
            # Summary
            logger.info("\n" + "="*50)
            logger.info("TEST SUMMARY")
            logger.info("="*50)
            logger.info(f"Total leads found: {len(leads)}")
            logger.info(f"Leads with web problems: {stats.get('leads_with_web_problems', 0)}")
            logger.info(f"Leads without website: {stats.get('leads_without_website', 0)}")
            logger.info(f"Leads with poor SEO: {stats.get('leads_with_poor_seo', 0)}")
            logger.info(f"High priority leads: {stats.get('high_priority_leads', 0)}")
            logger.info(f"Collection time: {stats.get('collection_time', 0):.2f} seconds")
            
            if leads:
                avg_score = sum(lead.get('web_problem_score', 0) for lead in leads) / len(leads)
                logger.info(f"Average web problem score: {avg_score:.2f}")
                
                high_priority = [lead for lead in leads if lead.get('priority_level') == 'high']
                logger.info(f"High priority leads: {len(high_priority)}")
                
                no_website = [lead for lead in leads if 'no_website' in lead.get('web_problems', [])]
                logger.info(f"Leads without website: {len(no_website)}")
            
            return leads
            
    except Exception as e:
        logger.error(f"Error in test: {e}")
        return []

async def test_multiple_sectors():
    """Test the collector with multiple sectors"""
    
    sectors = [
        "restaurante",
        "advogado", 
        "dentista",
        "psicologo",
        "imobiliaria"
    ]
    
    region = "São Paulo"
    max_leads_per_sector = 10
    
    all_results = {}
    
    for sector in sectors:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing sector: {sector}")
        logger.info(f"{'='*60}")
        
        try:
            async with WebProblemLeadCollector() as collector:
                leads = await collector.collect_web_problem_leads(
                    sector=sector,
                    region=region,
                    max_leads=max_leads_per_sector
                )
                
                stats = collector.get_collection_stats()
                
                all_results[sector] = {
                    'leads': leads,
                    'stats': stats
                }
                
                logger.info(f"Found {len(leads)} leads for {sector}")
                logger.info(f"High priority: {stats.get('high_priority_leads', 0)}")
                logger.info(f"Without website: {stats.get('leads_without_website', 0)}")
                
        except Exception as e:
            logger.error(f"Error testing sector {sector}: {e}")
            all_results[sector] = {'leads': [], 'stats': {}}
    
    # Save combined results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"data/multi_sector_web_problem_leads_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\nCombined results saved to: {results_file}")
    
    # Summary across all sectors
    total_leads = sum(len(result['leads']) for result in all_results.values())
    total_high_priority = sum(result['stats'].get('high_priority_leads', 0) for result in all_results.values())
    total_no_website = sum(result['stats'].get('leads_without_website', 0) for result in all_results.values())
    
    logger.info(f"\n{'='*60}")
    logger.info("MULTI-SECTOR SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total leads across all sectors: {total_leads}")
    logger.info(f"Total high priority leads: {total_high_priority}")
    logger.info(f"Total leads without website: {total_no_website}")
    
    return all_results

async def main():
    """Main test function"""
    logger.info("Starting Web Problem Lead Collector Tests")
    
    # Test single sector
    logger.info("\n" + "="*60)
    logger.info("SINGLE SECTOR TEST")
    logger.info("="*60)
    await test_web_problem_collector()
    
    # Test multiple sectors
    logger.info("\n" + "="*60)
    logger.info("MULTI-SECTOR TEST")
    logger.info("="*60)
    await test_multiple_sectors()
    
    logger.info("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 