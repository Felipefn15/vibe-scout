#!/usr/bin/env python3
"""
Script simplificado para executar a campanha diária uma vez
Railway vai gerenciar o cron, então não precisamos de scheduling interno
"""

import os
import sys
import time
from daily_campaign import DailyCampaignScheduler
from utils.logger import VibeScoutLogger

def main():
    """Executa a campanha diária uma vez"""
    logger = VibeScoutLogger()
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting daily campaign execution")
    
    try:
        scheduler = DailyCampaignScheduler()
        scheduler.run_daily_campaign()
        logger.info("Daily campaign completed successfully")
    except Exception as e:
        logger.error(f"Error running daily campaign: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 