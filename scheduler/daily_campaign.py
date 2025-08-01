#!/usr/bin/env python3
"""
Daily Campaign Scheduler
Automatically runs scraping and email campaigns for 5 random sectors daily
"""

import asyncio
import json
import os
import random
import time
from datetime import datetime
from typing import List, Dict
import psutil

from scraper.collect import LeadCollector
from analysis.site_seo import SiteSEOAnalyzer
from analysis.social import SocialMediaAnalyzer
from llm.generate_email import EmailGenerator
from email_sender.sendgrid_sender import SendGridSender
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter
from utils.email_extractor import EmailExtractor
from config.sectors import load_sectors
from config.lead_filters import LeadFilter
from reports.build_report import ReportBuilder

logger = get_logger(__name__)

class DailyCampaign:
    def __init__(self):
        self.lead_collector = LeadCollector()
        self.seo_analyzer = SiteSEOAnalyzer()
        self.social_analyzer = SocialMediaAnalyzer()
        self.email_generator = EmailGenerator()
        self.email_sender = SendGridSender()
        self.email_extractor = EmailExtractor()
        self.rate_limiter = RateLimiter()
        self.lead_filter = LeadFilter()
        self.report_builder = ReportBuilder()
        
        # Load configuration
        self.sectors = load_sectors()
        self.max_emails_per_day = int(os.getenv('MAX_EMAILS_PER_DAY', '100'))
        self.consultant_email = os.getenv('CONSULTANT_EMAIL', '')
        
    async def run_campaign(self):
        """Run the daily campaign with improved email extraction"""
        start_time = time.time()
        logger.info("🚀 Starting daily campaign")
        
        # Select random sectors
        selected_sectors = self._select_random_sectors()
        logger.info(f"Selected sectors: {selected_sectors}")
        
        total_emails_sent = 0
        all_campaign_data = []
        
        for sector in selected_sectors:
            if total_emails_sent >= self.max_emails_per_day:
                logger.info(f"Reached daily email limit ({self.max_emails_per_day})")
                break
                
            sector_data = await self._process_sector(sector, total_emails_sent)
            all_campaign_data.append(sector_data)
            total_emails_sent += sector_data['emails_sent']
            
            # Rate limiting between sectors
            await asyncio.sleep(5)
        
        # Build and send report
        await self._send_campaign_report(all_campaign_data, start_time)
        
        # Log system health
        self._log_system_health()
        
        logger.info("✅ Daily campaign completed successfully")
    
    def _select_random_sectors(self) -> List[str]:
        """Select random sectors for the campaign"""
        available_sectors = list(self.sectors.keys())
        num_sectors = min(3, len(available_sectors))  # Process 3 sectors max
        return random.sample(available_sectors, num_sectors)
    
    async def _process_sector(self, sector: str, emails_sent_so_far: int) -> Dict:
        """Process a single sector with improved email handling"""
        sector_start_time = time.time()
        logger.info(f"🏢 Processing sector: {sector}")
        
        sector_data = {
            'sector': sector,
            'leads_found': 0,
            'emails_sent': 0,
            'leads_processed': []
        }
        
        # Collect leads for each region
        for region in self.sectors[sector]:
            if emails_sent_so_far + sector_data['emails_sent'] >= self.max_emails_per_day:
                break
                
            logger.info(f"🏢 Processing setor: {sector} - {region}")
            
            try:
                # Collect leads
                leads = await self.lead_collector.collect_leads(sector, region)
                logger.info(f"Found {len(leads)} leads for {sector} in {region}")
                
                # Extract emails for leads
                leads_with_emails = await self.email_extractor.extract_emails_batch(leads)
                logger.info(f"Extracted emails for {len(leads_with_emails)} leads")
                
                # Process each lead
                for lead in leads_with_emails:
                    if emails_sent_so_far + sector_data['emails_sent'] >= self.max_emails_per_day:
                        break
                    
                    lead_result = await self._process_lead(lead, sector, region)
                    sector_data['leads_processed'].append(lead_result)
                    
                    if lead_result['email_sent']:
                        sector_data['emails_sent'] += 1
                        emails_sent_so_far += 1
                
                sector_data['leads_found'] += len(leads)
                
            except Exception as e:
                logger.error(f"Error processing {sector} - {region}: {e}")
        
        sector_duration = time.time() - sector_start_time
        logger.info(f"✅ Setor concluído: {sector} - {region} | {{'event': 'sector_complete', 'sector': '{sector}', 'region': '{region}', 'leads_found': {sector_data['leads_found']}, 'emails_sent': {sector_data['emails_sent']}, 'timestamp': '{datetime.now().isoformat()}'}}")
        
        return sector_data
    
    async def _process_lead(self, lead: Dict, sector: str, region: str) -> Dict:
        """Process a single lead with improved email handling"""
        lead_name = lead.get('name', 'Unknown')
        email = lead.get('email', '')
        
        logger.info(f"🎯 Lead coletado: {lead_name} | {{'event': 'lead_collected', 'lead_name': '{lead_name}', 'sector': '{sector}', 'region': '{region}', 'timestamp': '{datetime.now().isoformat()}'}}")
        
        result = {
            'name': lead_name,
            'sector': sector,
            'region': region,
            'email': email,
            'email_sent': False,
            'error': None
        }
        
        try:
            # Analyze website if available
            website = lead.get('website', '')
            if website:
                seo_data = await self.seo_analyzer.analyze_website(website)
                social_data = await self.social_analyzer.analyze_social_presence(lead_name)
            else:
                seo_data = {}
                social_data = {}
            
            # Generate personalized email
            email_content = await self.email_generator.generate_email(
                lead_name, sector, region, seo_data, social_data
            )
            
            # Send email if we have an email address
            if email and email.strip():
                success = await self.email_sender.send_email(
                    to_email=email,
                    to_name=lead_name,
                    subject=email_content['subject'],
                    html_content=email_content['html_content']
                )
                
                if success:
                    result['email_sent'] = True
                    logger.info(f"✅ Email enviado: {lead_name} | {{'event': 'email_sent', 'lead_name': '{lead_name}', 'email': '{email}', 'timestamp': '{datetime.now().isoformat()}'}}")
                else:
                    result['error'] = 'SendGrid error'
                    logger.error(f"❌ Falha no envio: {lead_name} | {{'event': 'email_failed', 'lead_name': '{lead_name}', 'email': '{email}', 'error': 'SendGrid error', 'timestamp': '{datetime.now().isoformat()}'}}")
            else:
                result['error'] = 'No email address'
                logger.warning(f"⚠️ Sem email: {lead_name} | {{'event': 'no_email', 'lead_name': '{lead_name}', 'timestamp': '{datetime.now().isoformat()}'}}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ Error processing lead {lead_name}: {e}")
        
        return result
    
    async def _send_campaign_report(self, campaign_data: List[Dict], start_time: float):
        """Send campaign report to consultant"""
        try:
            duration = time.time() - start_time
            total_emails = sum(sector['emails_sent'] for sector in campaign_data)
            total_leads = sum(sector['leads_found'] for sector in campaign_data)
            
            # Build report
            report_html = self.report_builder.build_campaign_report(
                campaign_data, duration, total_emails, total_leads
            )
            
            # Send report email
            if self.consultant_email:
                await self.email_sender.send_email(
                    to_email=self.consultant_email,
                    to_name="Consultor",
                    subject=f"Relatório de Campanha - {datetime.now().strftime('%d/%m/%Y')}",
                    html_content=report_html
                )
                logger.info(f"📊 Relatório enviado para {self.consultant_email}")
            
            logger.info(f"✅ Campanha concluída | {{'event': 'campaign_complete', 'total_emails': {total_emails}, 'sectors_processed': {[s['sector'] for s in campaign_data]}, 'duration_seconds': {duration:.1f}, 'timestamp': '{datetime.now().isoformat()}'}}")
            
        except Exception as e:
            logger.error(f"Error sending campaign report: {e}")
    
    def _log_system_health(self):
        """Log system health metrics"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            disk = psutil.disk_usage('/')
            
            logger.info(f"💚 Saúde do sistema | {{'event': 'system_health', 'memory_usage_mb': {memory.used / 1024 / 1024:.2f}, 'cpu_usage_percent': {cpu}, 'disk_usage_percent': {disk.percent}, 'timestamp': '{datetime.now().isoformat()}'}}")
            
        except Exception as e:
            logger.error(f"Error logging system health: {e}")

async def main():
    """Main function to run the campaign"""
    campaign = DailyCampaign()
    await campaign.run_campaign()

if __name__ == "__main__":
    asyncio.run(main()) 