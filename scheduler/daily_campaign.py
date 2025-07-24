#!/usr/bin/env python3
"""
Daily Campaign Scheduler
Automatically runs scraping and email campaigns for 5 random sectors daily
"""

import os
import sys
import json
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import schedule
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.collect import LeadCollector
from analysis.social import SocialMediaAnalyzer
from analysis.site_seo import SiteSEOAnalyzer
from llm.generate_email import EmailGenerator
from email_sender.sendgrid_sender import SendGridSender
from utils.rate_limiter import RateLimiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_campaign.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyCampaignScheduler:
    def __init__(self):
        self.lead_collector = LeadCollector()
        self.social_analyzer = SocialMediaAnalyzer()
        self.site_analyzer = SiteSEOAnalyzer()
        self.email_generator = EmailGenerator()
        self.email_sender = SendGridSender()
        self.rate_limiter = RateLimiter()
        
        # Load sector configuration
        self.sectors = self._load_sectors()
        self.regions = self._load_regions()
        
        # Campaign limits
        self.max_leads_per_sector = 20  # 5 sectors * 20 leads = 100 emails max
        self.max_emails_per_day = 100
        
        # Track daily usage
        self.daily_usage_file = 'data/daily_usage.json'
        self.daily_usage = self._load_daily_usage()
    
    def _load_sectors(self) -> List[Dict]:
        """Load available sectors from configuration"""
        try:
            with open('config/sectors.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("sectors.json not found, using default sectors")
            return [
                {"name": "Advocacia", "keywords": ["advocacia", "advogados", "escritório de advocacia"]},
                {"name": "Restaurantes", "keywords": ["restaurante", "pizzaria", "churrascaria"]},
                {"name": "Farmácias", "keywords": ["farmácia", "drogaria", "farmacia"]},
                {"name": "Clínicas", "keywords": ["clínica", "consultório", "clinica"]},
                {"name": "Academias", "keywords": ["academia", "ginástica", "fitness"]},
                {"name": "Salões de Beleza", "keywords": ["salão de beleza", "salao de beleza", "estética"]},
                {"name": "Imobiliárias", "keywords": ["imobiliária", "imobiliaria", "imóveis"]},
                {"name": "Consultorias", "keywords": ["consultoria", "assessoria", "empresarial"]},
                {"name": "Padarias", "keywords": ["padaria", "panificadora", "confeitaria"]},
                {"name": "Lojas", "keywords": ["loja", "comércio", "comercio", "varejo"]}
            ]
    
    def _load_regions(self) -> List[str]:
        """Load available regions"""
        return [
            "Rio de Janeiro",
            "São Paulo",
            "Belo Horizonte",
            "Brasília",
            "Salvador",
            "Fortaleza",
            "Recife",
            "Porto Alegre",
            "Curitiba",
            "Goiânia"
        ]
    
    def _load_daily_usage(self) -> Dict:
        """Load daily email usage tracking"""
        try:
            with open(self.daily_usage_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"date": "", "emails_sent": 0, "sectors_processed": []}
    
    def _save_daily_usage(self):
        """Save daily email usage tracking"""
        os.makedirs(os.path.dirname(self.daily_usage_file), exist_ok=True)
        with open(self.daily_usage_file, 'w') as f:
            json.dump(self.daily_usage, f, indent=2)
    
    def _reset_daily_usage(self):
        """Reset daily usage counter if it's a new day"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.daily_usage.get('date') != today:
            self.daily_usage = {
                "date": today,
                "emails_sent": 0,
                "sectors_processed": []
            }
            self._save_daily_usage()
            logger.info(f"Reset daily usage counter for {today}")
    
    def _select_random_sectors(self, count: int = 5) -> List[Dict]:
        """Select random sectors for today's campaign"""
        # Get sectors that haven't been processed today
        processed_sectors = set(self.daily_usage.get('sectors_processed', []))
        available_sectors = [s for s in self.sectors if s['name'] not in processed_sectors]
        
        # If we've processed all sectors, reset and start over
        if not available_sectors:
            logger.info("All sectors processed today, resetting for tomorrow")
            return random.sample(self.sectors, min(count, len(self.sectors)))
        
        # Select random sectors
        selected = random.sample(available_sectors, min(count, len(available_sectors)))
        logger.info(f"Selected sectors for today: {[s['name'] for s in selected]}")
        return selected
    
    def _select_random_regions(self, count: int = 3) -> List[str]:
        """Select random regions for today's campaign"""
        return random.sample(self.regions, min(count, len(self.regions)))
    
    def _can_send_more_emails(self) -> bool:
        """Check if we can send more emails today"""
        return self.daily_usage.get('emails_sent', 0) < self.max_emails_per_day
    
    def _process_sector(self, sector: Dict, regions: List[str]) -> int:
        """Process a single sector and return number of emails sent"""
        sector_name = sector['name']
        logger.info(f"Processing sector: {sector_name}")
        
        emails_sent = 0
        
        for region in regions:
            if not self._can_send_more_emails():
                logger.info(f"Daily email limit reached ({self.max_emails_per_day})")
                break
            
            try:
                # Collect leads for this sector and region
                leads = self.lead_collector.collect_leads(
                    industry=sector_name,
                    region=region,
                    test_mode=False,
                    target_count=self.max_leads_per_sector
                )
                
                if not leads:
                    logger.warning(f"No leads found for {sector_name} in {region}")
                    continue
                
                logger.info(f"Found {len(leads)} leads for {sector_name} in {region}")
                
                # Process each lead
                for lead in leads:
                    if not self._can_send_more_emails():
                        break
                    
                    try:
                        # Analyze lead
                        analysis_data = self.site_analyzer.analyze_website(lead.get('website', ''))
                        social_data = self.social_analyzer.analyze_social_presence(lead.get('name', ''))
                        
                        # Generate email
                        email_data = self.email_generator.generate_email(lead, analysis_data, social_data)
                        
                        if email_data and email_data.get('body'):
                            # Send email
                            success = self.email_sender.send_email(
                                to_email=lead.get('email', ''),
                                subject=email_data.get('subject', ''),
                                body=email_data.get('body', ''),
                                lead_name=lead.get('name', '')
                            )
                            
                            if success:
                                emails_sent += 1
                                self.daily_usage['emails_sent'] += 1
                                logger.info(f"Email sent to {lead.get('name')} ({emails_sent}/{self.max_emails_per_day})")
                            else:
                                logger.warning(f"Failed to send email to {lead.get('name')}")
                        
                        # Rate limiting
                        self.rate_limiter.wait()
                        
                    except Exception as e:
                        logger.error(f"Error processing lead {lead.get('name', '')}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing sector {sector_name} in region {region}: {e}")
                continue
        
        # Mark sector as processed
        self.daily_usage['sectors_processed'].append(sector_name)
        self._save_daily_usage()
        
        logger.info(f"Completed sector {sector_name}: {emails_sent} emails sent")
        return emails_sent
    
    def run_daily_campaign(self):
        """Run the daily campaign"""
        logger.info("=== Starting Daily Campaign ===")
        
        # Reset daily usage if it's a new day
        self._reset_daily_usage()
        
        # Check if we've already sent emails today
        if self.daily_usage.get('emails_sent', 0) >= self.max_emails_per_day:
            logger.info("Daily email limit already reached, skipping campaign")
            return
        
        # Select random sectors and regions
        selected_sectors = self._select_random_sectors(5)
        selected_regions = self._select_random_regions(3)
        
        logger.info(f"Selected regions: {selected_regions}")
        
        total_emails_sent = 0
        
        # Process each sector
        for sector in selected_sectors:
            if not self._can_send_more_emails():
                break
            
            emails_sent = self._process_sector(sector, selected_regions)
            total_emails_sent += emails_sent
        
        logger.info(f"=== Daily Campaign Complete ===")
        logger.info(f"Total emails sent: {total_emails_sent}")
        logger.info(f"Daily usage: {self.daily_usage['emails_sent']}/{self.max_emails_per_day}")
        logger.info(f"Sectors processed: {self.daily_usage['sectors_processed']}")
    
    def schedule_daily_campaign(self, time: str = "08:00"):
        """Schedule the daily campaign to run at specified time"""
        schedule.every().day.at(time).do(self.run_daily_campaign)
        logger.info(f"Scheduled daily campaign to run at {time}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function to run the scheduler"""
    scheduler = DailyCampaignScheduler()
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Run immediately if called directly
    if len(sys.argv) > 1 and sys.argv[1] == '--run-now':
        scheduler.run_daily_campaign()
    else:
        # Schedule to run daily at 8 AM
        scheduler.schedule_daily_campaign("08:00")

if __name__ == "__main__":
    main() 