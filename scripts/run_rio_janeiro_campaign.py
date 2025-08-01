#!/usr/bin/env python3
"""
Vibe Scout - Rio de Janeiro Campaign Runner
Executes the pipeline for 5 specific areas in Rio de Janeiro
"""

import json
import os
import sys
import logging
import time
import asyncio
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rio_janeiro_campaign.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_campaign_config() -> Dict:
    """Load campaign configuration"""
    try:
        with open('config/rio_janeiro_campaign.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading campaign config: {e}")
        return {}

async def run_area_pipeline(area: Dict, region: str, test_mode: bool = False) -> Dict:
    """Run pipeline for a specific area"""
    try:
        logger.info(f"Starting pipeline for {area['display_name']} in {region}")
        
        # Import and run the pipeline
        from main import run_pipeline_simple
        
        result = await run_pipeline_simple(
            industry=area['name'],
            region=region,
            test_mode=test_mode
        )
        
        logger.info(f"Completed pipeline for {area['display_name']} in {region}")
        return {
            "status": "success",
            "area": area['name'],
            "area_display": area['display_name'],
            "region": region,
            "leads_count": len(result) if result else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running pipeline for {area['display_name']}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "area": area['name'],
            "area_display": area['display_name'],
            "region": region,
            "timestamp": datetime.now().isoformat()
        }

async def run_rio_janeiro_campaign(test_mode: bool = False):
    """Run campaign for Rio de Janeiro areas"""
    
    # Load configuration
    config = load_campaign_config()
    if not config:
        logger.error("Failed to load campaign configuration")
        return
    
    areas = config.get('areas', [])
    region = config.get('region', 'Rio de Janeiro')
    settings = config.get('settings', {})
    
    if not areas:
        logger.error("No areas configured")
        return
    
    # Sort by priority
    areas.sort(key=lambda x: x.get('priority', 999))
    
    logger.info(f"Running Rio de Janeiro campaign for {len(areas)} areas")
    logger.info(f"Region: {region}")
    logger.info(f"Test mode: {test_mode}")
    
    results = []
    total_start_time = time.time()
    
    for i, area in enumerate(areas, 1):
        logger.info(f"Processing area {i}/{len(areas)}: {area['display_name']}")
        
        # Run pipeline for this area
        result = await run_area_pipeline(area, region, test_mode)
        results.append(result)
        
        # Add delay between areas
        if i < len(areas) and not test_mode:
            delay = settings.get('delay_between_areas', 30)
            logger.info(f"Waiting {delay} seconds before next area...")
            time.sleep(delay)
    
    # Calculate total time
    total_time = time.time() - total_start_time
    
    # Save results
    results_file = f"rio_janeiro_campaign_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'campaign_name': config.get('campaign_name', 'Rio de Janeiro Campaign'),
            'summary': {
                'total_areas': len(areas),
                'region': region,
                'total_runs': len(results),
                'total_time_seconds': total_time,
                'test_mode': test_mode,
                'timestamp': datetime.now().isoformat()
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("RIO DE JANEIRO CAMPAIGN SUMMARY")
    print("="*60)
    print(f"Campaign: {config.get('campaign_name', 'Rio de Janeiro Campaign')}")
    print(f"Region: {region}")
    print(f"Total areas processed: {len(areas)}")
    print(f"Total pipeline runs: {len(results)}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Results saved to: {results_file}")
    
    # Count successes and failures
    successes = [r for r in results if r.get('status') == 'success']
    failures = [r for r in results if r.get('status') == 'error']
    
    print(f"\nSuccesses: {len(successes)}")
    print(f"Failures: {len(failures)}")
    
    # Show results by area
    print(f"\nResults by area:")
    for result in results:
        status = result.get('status', 'unknown')
        area = result.get('area_display', 'Unknown')
        leads = result.get('leads_count', 0)
        print(f"- {area}: {status} ({leads} leads)")
    
    if failures:
        print(f"\nFailed runs:")
        for failure in failures:
            print(f"- {failure['area_display']}: {failure.get('error', 'Unknown error')}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vibe Scout - Rio de Janeiro Campaign Runner')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    print("="*60)
    print("VIBE SCOUT - RIO DE JANEIRO CAMPAIGN")
    print("="*60)
    print(f"Test mode: {args.test}")
    print("Areas: Advocacia, Contabilidade, Psicologia, Dentista, Imobiliária")
    print("Region: Rio de Janeiro")
    print("="*60)
    
    asyncio.run(run_rio_janeiro_campaign(test_mode=args.test))

if __name__ == "__main__":
    main() 