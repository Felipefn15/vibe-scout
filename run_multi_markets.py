#!/usr/bin/env python3
"""
Vibe Scout - Multi-Market Pipeline Runner
Executes the pipeline for multiple markets and regions
"""

import json
import os
import sys
import logging
import time
from datetime import datetime
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/multi_markets.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_markets_config() -> Dict:
    """Load markets configuration"""
    try:
        with open('config/markets.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading markets config: {e}")
        return {"markets": [], "regions": []}

def run_market_pipeline(market: Dict, region: Dict, test_mode: bool = False) -> Dict:
    """Run pipeline for a specific market and region"""
    try:
        logger.info(f"Starting pipeline for {market['display_name']} in {region['display_name']}")
        
        # Import and run the pipeline
        from main import run_pipeline_simple
        
        result = run_pipeline_simple(
            industry=market['name'],
            region=region['display_name'],
            test_mode=test_mode
        )
        
        logger.info(f"Completed pipeline for {market['display_name']} in {region['display_name']}")
        return result
        
    except Exception as e:
        logger.error(f"Error running pipeline for {market['display_name']}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "market": market['name'],
            "region": region['display_name']
        }

def run_multi_markets(test_mode: bool = False, max_markets: int = None, max_regions: int = None):
    """Run pipeline for multiple markets and regions"""
    
    # Load configuration
    config = load_markets_config()
    markets = config.get('markets', [])
    regions = config.get('regions', [])
    
    if not markets or not regions:
        logger.error("No markets or regions configured")
        return
    
    # Sort by priority
    markets.sort(key=lambda x: x.get('priority', 999))
    regions.sort(key=lambda x: x.get('priority', 999))
    
    # Limit if specified
    if max_markets:
        markets = markets[:max_markets]
    if max_regions:
        regions = regions[:max_regions]
    
    logger.info(f"Running multi-market pipeline for {len(markets)} markets and {len(regions)} regions")
    
    results = []
    total_start_time = time.time()
    
    for i, market in enumerate(markets, 1):
        logger.info(f"Processing market {i}/{len(markets)}: {market['display_name']}")
        
        for j, region in enumerate(regions, 1):
            logger.info(f"Processing region {j}/{len(regions)}: {region['display_name']}")
            
            # Run pipeline for this market/region combination
            result = run_market_pipeline(market, region, test_mode)
            
            # Add metadata
            result.update({
                'market': market['name'],
                'market_display': market['display_name'],
                'region': region['name'],
                'region_display': region['display_name'],
                'timestamp': datetime.now().isoformat()
            })
            
            results.append(result)
            
            # Add delay between runs to avoid overwhelming APIs
            if not test_mode:
                time.sleep(30)  # 30 second delay between runs
            else:
                time.sleep(5)   # 5 second delay in test mode
    
    # Calculate total time
    total_time = time.time() - total_start_time
    
    # Save results
    results_file = f"multi_markets_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_markets': len(markets),
                'total_regions': len(regions),
                'total_runs': len(results),
                'total_time_seconds': total_time,
                'test_mode': test_mode,
                'timestamp': datetime.now().isoformat()
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("MULTI-MARKET PIPELINE SUMMARY")
    print("="*60)
    print(f"Total markets processed: {len(markets)}")
    print(f"Total regions processed: {len(regions)}")
    print(f"Total pipeline runs: {len(results)}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Results saved to: {results_file}")
    
    # Count successes and failures
    successes = [r for r in results if r.get('status') == 'success']
    failures = [r for r in results if r.get('status') == 'error']
    no_leads = [r for r in results if r.get('status') == 'no_new_leads']
    
    print(f"\nSuccesses: {len(successes)}")
    print(f"Failures: {len(failures)}")
    print(f"No new leads: {len(no_leads)}")
    
    if failures:
        print("\nFailed runs:")
        for failure in failures:
            print(f"- {failure['market_display']} in {failure['region_display']}: {failure.get('error', 'Unknown error')}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vibe Scout - Multi-Market Pipeline Runner')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--max-markets', type=int, help='Maximum number of markets to process')
    parser.add_argument('--max-regions', type=int, help='Maximum number of regions to process')
    
    args = parser.parse_args()
    
    print("="*60)
    print("VIBE SCOUT - MULTI-MARKET PIPELINE")
    print("="*60)
    print(f"Test mode: {args.test}")
    print(f"Max markets: {args.max_markets or 'All'}")
    print(f"Max regions: {args.max_regions or 'All'}")
    print("="*60)
    
    run_multi_markets(
        test_mode=args.test,
        max_markets=args.max_markets,
        max_regions=args.max_regions
    )

if __name__ == "__main__":
    main() 