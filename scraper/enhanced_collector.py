#!/usr/bin/env python3
"""
Enhanced Lead Collector with LLM Integration
Optimized lead collection with intelligent filtering and analysis
"""

import asyncio
import json
import logging
import re
import time
import random
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urljoin
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from config.lead_filters import LeadFilter
from utils.lead_scorer import LeadScorer
from llm.lead_analyzer import IntelligentLeadAnalyzer
from scraper.browser_simulator import BrowserSimulator
from scraper.website_analyzer import WebsiteAnalyzer
from scraper.social_media_scraper import SocialMediaScraper

logger = logging.getLogger(__name__)

class EnhancedLeadCollector:
    """Enhanced lead collector with LLM-powered intelligence"""
    
    def __init__(self, llm_providers: List[str] = None):
        """Initialize enhanced lead collector"""
        self.lead_filter = LeadFilter()
        self.lead_scorer = LeadScorer()
        self.intelligent_analyzer = IntelligentLeadAnalyzer(llm_providers)
        self.session = None
        
        # Initialize scrapers
        self.website_analyzer = None
        self.social_media_scraper = None
        self.browser_simulator = None
        
        # Rate limiting and performance
        self.request_count = 0
        self.last_request_time = 0
        self.min_delay = 1
        self.max_delay = 3
        self.timeout = 30000
        
        # Collection statistics
        self.collection_stats = {
            'total_sources_checked': 0,
            'leads_found': 0,
            'leads_filtered': 0,
            'leads_analyzed': 0,
            'high_quality_leads': 0,
            'llm_analysis_time': 0,
            'collection_time': 0
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        
        # Initialize scrapers
        self.website_analyzer = WebsiteAnalyzer()
        await self.website_analyzer.__aenter__()
        
        self.social_media_scraper = SocialMediaScraper()
        await self.social_media_scraper.__aenter__()
        
        self.browser_simulator = BrowserSimulator()
        await self.browser_simulator.__aenter__()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        
        # Clean up scrapers
        if self.website_analyzer:
            await self.website_analyzer.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.social_media_scraper:
            await self.social_media_scraper.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.browser_simulator:
            await self.browser_simulator.__aexit__(exc_type, exc_val, exc_tb)
    
    async def collect_intelligent_leads(self, sector: str, region: str, 
                                      min_intelligence_score: int = 70,
                                      max_leads: int = 100,
                                      include_website_analysis: bool = True,
                                      include_social_analysis: bool = True) -> List[Dict]:
        """
        Collect leads with intelligent LLM-powered analysis
        
        Args:
            sector: Target business sector
            region: Target region
            min_intelligence_score: Minimum intelligence score for leads
            max_leads: Maximum number of leads to collect
            include_website_analysis: Whether to analyze websites
            include_social_analysis: Whether to analyze social media
            
        Returns:
            List of high-quality leads with AI analysis
        """
        start_time = time.time()
        logger.info(f"Starting intelligent lead collection for {sector} in {region}")
        
        try:
            # 1. Collect raw leads from multiple sources
            raw_leads = await self._collect_raw_leads(sector, region, max_leads * 2)  # Collect more to filter
            self.collection_stats['leads_found'] = len(raw_leads)
            
            # 2. Initial filtering and validation
            validated_leads = await self._validate_and_filter_leads(raw_leads, sector)
            self.collection_stats['leads_filtered'] = len(validated_leads)
            
            # 3. Enrich leads with website analysis
            if include_website_analysis:
                enriched_leads = await self._enrich_with_website_analysis(validated_leads)
            else:
                enriched_leads = validated_leads
            
            # 4. Enrich leads with social media analysis
            if include_social_analysis:
                enriched_leads = await self._enrich_with_social_analysis(enriched_leads)
            
            # 5. Intelligent LLM analysis
            llm_start_time = time.time()
            intelligent_leads = await self._perform_intelligent_analysis(enriched_leads)
            self.collection_stats['llm_analysis_time'] = time.time() - llm_start_time
            
            # 6. Filter by intelligence score
            high_quality_leads = [
                lead for lead in intelligent_leads 
                if lead.get('intelligence_score', 0) >= min_intelligence_score
            ]
            self.collection_stats['high_quality_leads'] = len(high_quality_leads)
            
            # 7. Remove duplicates and sort by intelligence score
            final_leads = self._remove_duplicates_and_sort(high_quality_leads)
            
            # 8. Limit to max_leads
            final_leads = final_leads[:max_leads]
            
            # 9. Update statistics
            self.collection_stats['collection_time'] = time.time() - start_time
            self.collection_stats['leads_analyzed'] = len(intelligent_leads)
            
            logger.info(f"Intelligent lead collection completed: {len(final_leads)} high-quality leads")
            logger.info(f"Collection statistics: {json.dumps(self.collection_stats, indent=2)}")
            
            return final_leads
            
        except Exception as e:
            logger.error(f"Error in intelligent lead collection: {e}")
            return []
    
    async def _collect_raw_leads(self, sector: str, region: str, max_leads: int) -> List[Dict]:
        """Collect raw leads from multiple sources"""
        all_leads = []
        
        try:
            # Generate optimized keywords
            keywords = self._generate_optimized_keywords(sector)
            
            # Collect from multiple sources concurrently
            collection_tasks = []
            
            # Google Maps collection
            for keyword in keywords[:3]:  # Limit keywords for efficiency
                task = self._collect_google_maps_leads(keyword, region)
                collection_tasks.append(task)
            
            # Google Search collection
            for keyword in keywords[:3]:
                task = self._collect_google_search_leads(keyword, region)
                collection_tasks.append(task)
            
            # Bing Search collection
            for keyword in keywords[:2]:
                task = self._collect_bing_search_leads(keyword, region)
                collection_tasks.append(task)
            
            # Execute all collection tasks concurrently
            results = await asyncio.gather(*collection_tasks, return_exceptions=True)
            
            # Combine results
            for result in results:
                if isinstance(result, list):
                    all_leads.extend(result)
                else:
                    logger.error(f"Collection task failed: {result}")
            
            # Remove duplicates early
            all_leads = self._remove_duplicates(all_leads)
            
            # Limit to max_leads
            all_leads = all_leads[:max_leads]
            
            logger.info(f"Collected {len(all_leads)} raw leads from {len(collection_tasks)} sources")
            
        except Exception as e:
            logger.error(f"Error collecting raw leads: {e}")
        
        return all_leads
    
    async def _collect_google_maps_leads(self, keyword: str, region: str) -> List[Dict]:
        """Collect leads from Google Maps using browser simulator"""
        try:
            if not self.browser_simulator:
                return []
            
            leads = await self.browser_simulator.search_google_maps_with_screenshot(keyword, region)
            logger.info(f"Collected {len(leads)} leads from Google Maps for '{keyword}'")
            return leads
            
        except Exception as e:
            logger.error(f"Error collecting Google Maps leads: {e}")
            return []
    
    async def _collect_google_search_leads(self, keyword: str, region: str) -> List[Dict]:
        """Collect leads from Google Search using browser simulator"""
        try:
            if not self.browser_simulator:
                return []
            
            leads = await self.browser_simulator.search_google_with_screenshot(keyword, region)
            logger.info(f"Collected {len(leads)} leads from Google Search for '{keyword}'")
            return leads
            
        except Exception as e:
            logger.error(f"Error collecting Google Search leads: {e}")
            return []
    
    async def _collect_bing_search_leads(self, keyword: str, region: str) -> List[Dict]:
        """Collect leads from Bing Search using browser simulator"""
        try:
            if not self.browser_simulator:
                return []
            
            leads = await self.browser_simulator.search_bing_with_screenshot(keyword, region)
            logger.info(f"Collected {len(leads)} leads from Bing Search for '{keyword}'")
            return leads
            
        except Exception as e:
            logger.error(f"Error collecting Bing Search leads: {e}")
            return []
    
    async def _validate_and_filter_leads(self, leads: List[Dict], sector: str) -> List[Dict]:
        """Validate and filter leads using intelligent criteria"""
        validated_leads = []
        
        for lead in leads:
            try:
                # Basic validation
                if not self._is_valid_lead(lead):
                    continue
                
                # Sector-specific validation
                if not self._is_relevant_to_sector(lead, sector):
                    continue
                
                # Quality validation
                if not self._meets_quality_criteria(lead):
                    continue
                
                # Enrich with additional data
                enriched_lead = await self._enrich_lead_data(lead, sector)
                validated_leads.append(enriched_lead)
                
            except Exception as e:
                logger.debug(f"Error validating lead {lead.get('name', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Validated {len(validated_leads)} leads from {len(leads)} raw leads")
        return validated_leads
    
    def _is_valid_lead(self, lead: Dict) -> bool:
        """Check if lead meets basic validity criteria"""
        name = lead.get('name', '').strip()
        
        # Must have a name
        if not name or len(name) < 3:
            return False
        
        # Check for invalid patterns
        invalid_patterns = [
            'lista', 'guia', 'melhores', 'top', 'ranking',
            'preço', 'valor', 'quanto custa', 'orçamento',
            'home', 'página principal', 'centro', 'busca',
            'consulta', 'agendamento', 'marcar', 'google',
            'facebook', 'instagram', 'linkedin'
        ]
        
        name_lower = name.lower()
        for pattern in invalid_patterns:
            if pattern in name_lower:
                return False
        
        # Check for question patterns
        if '?' in name or 'como' in name_lower or 'quando' in name_lower:
            return False
        
        return True
    
    def _is_relevant_to_sector(self, lead: Dict, sector: str) -> bool:
        """Check if lead is relevant to the target sector"""
        name = lead.get('name', '').lower()
        description = lead.get('description', '').lower()
        
        # Load sector keywords
        try:
            with open('config/sectors.json', 'r', encoding='utf-8') as f:
                sectors = json.load(f)
            
            for sector_data in sectors:
                if sector_data['name'].lower() == sector.lower():
                    keywords = sector_data.get('keywords', [])
                    for keyword in keywords:
                        if keyword.lower() in name or keyword.lower() in description:
                            return True
        except Exception as e:
            logger.warning(f"Error checking sector relevance: {e}")
        
        # Fallback: check if sector name is in lead data
        return sector.lower() in name or sector.lower() in description
    
    def _meets_quality_criteria(self, lead: Dict) -> bool:
        """Check if lead meets quality criteria"""
        # Must have at least one contact method
        has_contact = bool(
            lead.get('website') or 
            lead.get('phone') or 
            lead.get('email')
        )
        
        if not has_contact:
            return False
        
        # Check for business-like characteristics
        name = lead.get('name', '').lower()
        
        # Avoid personal names
        personal_indicators = ['joão', 'maria', 'pedro', 'ana', 'carlos', 'julia']
        if any(indicator in name for indicator in personal_indicators):
            return False
        
        return True
    
    async def _enrich_lead_data(self, lead: Dict, sector: str) -> Dict:
        """Enrich lead data with additional information"""
        enriched_lead = lead.copy()
        
        # Add sector information
        enriched_lead['sector'] = sector
        
        # Add collection timestamp
        enriched_lead['collected_at'] = time.time()
        
        # Add source information
        if 'source' not in enriched_lead:
            enriched_lead['source'] = 'unknown'
        
        # Add region information if not present
        if 'region' not in enriched_lead:
            enriched_lead['region'] = 'unknown'
        
        return enriched_lead
    
    async def _enrich_with_website_analysis(self, leads: List[Dict]) -> List[Dict]:
        """Enrich leads with website analysis"""
        if not self.website_analyzer:
            return leads
        
        enriched_leads = []
        leads_with_websites = [lead for lead in leads if lead.get('website')]
        
        logger.info(f"Analyzing {len(leads_with_websites)} websites")
        
        # Analyze websites in batches
        batch_size = 5
        for i in range(0, len(leads_with_websites), batch_size):
            batch = leads_with_websites[i:i + batch_size]
            
            # Analyze websites concurrently
            website_urls = [lead['website'] for lead in batch]
            analyses = await self.website_analyzer.analyze_multiple_websites(website_urls)
            
            # Enrich leads with website analysis
            for lead, analysis in zip(batch, analyses):
                if analysis:
                    lead['website_analysis'] = analysis
                    lead['tech_stack'] = analysis.get('tech_stack', [])
                    lead['pain_points'] = analysis.get('pain_points', [])
                    lead['opportunities'] = analysis.get('opportunities', [])
                    lead['digital_maturity'] = analysis.get('digital_maturity', 'low')
                    lead['it_needs_score'] = analysis.get('it_needs_score', 0)
                    lead['recommendations'] = analysis.get('recommendations', [])
                
                enriched_leads.append(lead)
            
            # Rate limiting between batches
            await asyncio.sleep(random.uniform(2, 4))
        
        # Add leads without websites
        leads_without_websites = [lead for lead in leads if not lead.get('website')]
        enriched_leads.extend(leads_without_websites)
        
        return enriched_leads
    
    async def _enrich_with_social_analysis(self, leads: List[Dict]) -> List[Dict]:
        """Enrich leads with social media analysis"""
        if not self.social_media_scraper:
            return leads
        
        enriched_leads = []
        
        for lead in leads:
            company_name = lead.get('name', '')
            if company_name:
                try:
                    # Search for social media presence
                    social_results = await self.social_media_scraper.search_multiple_platforms(
                        company_name, lead.get('address', '')
                    )
                    
                    # Analyze social presence if found
                    if any(social_results.values()):
                        social_analysis = await self.social_media_scraper.analyze_social_presence(
                            company_name, social_results
                        )
                        
                        # Enrich lead with social analysis
                        lead['social_analysis'] = social_analysis
                        lead['social_indicators'] = social_analysis.get('it_indicators', [])
                        lead['social_growth_indicators'] = social_analysis.get('growth_indicators', [])
                        lead['social_pain_points'] = social_analysis.get('pain_points', [])
                        lead['digital_maturity_score'] = social_analysis.get('digital_maturity_score', 0)
                        lead['social_opportunities'] = social_analysis.get('opportunities', [])
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.debug(f"Error analyzing social presence for {company_name}: {e}")
            
            enriched_leads.append(lead)
        
        return enriched_leads
    
    async def _perform_intelligent_analysis(self, leads: List[Dict]) -> List[Dict]:
        """Perform intelligent LLM analysis on leads"""
        logger.info(f"Performing intelligent analysis on {len(leads)} leads")
        
        intelligent_leads = []
        
        # Process leads in batches to avoid overwhelming the LLM
        batch_size = 10
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]
            
            # Prepare data for batch analysis
            lead_data_list = []
            website_analyses = []
            social_analyses = []
            
            for lead in batch:
                lead_data_list.append(lead)
                website_analyses.append(lead.get('website_analysis', {}))
                social_analyses.append(lead.get('social_analysis', {}))
            
            # Perform batch analysis
            try:
                analyzed_leads = await self.intelligent_analyzer.analyze_bulk_leads(
                    lead_data_list, website_analyses, social_analyses
                )
                intelligent_leads.extend(analyzed_leads)
                
                logger.info(f"Analyzed batch {i//batch_size + 1}/{(len(leads) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                logger.error(f"Error in batch analysis: {e}")
                # Add leads with fallback analysis
                for lead in batch:
                    fallback_lead = self.intelligent_analyzer._generate_fallback_analysis(
                        lead, lead.get('website_analysis', {}), lead.get('social_analysis', {})
                    )
                    intelligent_leads.append(fallback_lead)
            
            # Rate limiting between batches
            if i + batch_size < len(leads):
                await asyncio.sleep(random.uniform(2, 4))
        
        return intelligent_leads
    
    def _remove_duplicates_and_sort(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicates and sort by intelligence score"""
        # Remove duplicates
        unique_leads = self._remove_duplicates(leads)
        
        # Sort by intelligence score (highest first)
        unique_leads.sort(key=lambda x: x.get('intelligence_score', 0), reverse=True)
        
        return unique_leads
    
    def _remove_duplicates(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicate leads based on name and website"""
        seen_names = set()
        seen_websites = set()
        unique_leads = []
        
        for lead in leads:
            name = lead.get('name', '').strip().lower()
            website = lead.get('website', '').strip().lower()
            
            # Check if we've seen this name or website before
            if name and name not in seen_names:
                if website and website in seen_websites:
                    continue  # Skip if website is duplicate
                
                seen_names.add(name)
                if website:
                    seen_websites.add(website)
                unique_leads.append(lead)
        
        return unique_leads
    
    def _generate_optimized_keywords(self, sector: str) -> List[str]:
        """Generate optimized search keywords for the sector"""
        # Load sector-specific keywords
        try:
            with open('config/sectors.json', 'r', encoding='utf-8') as f:
                sectors = json.load(f)
            
            for sector_data in sectors:
                if sector_data['name'].lower() == sector.lower():
                    return sector_data.get('keywords', [])
        except Exception as e:
            logger.warning(f"Error loading sector keywords: {e}")
        
        # Fallback optimized keywords
        base_keywords = [
            sector,
            f"{sector} {sector}",
            f"melhor {sector}",
            f"{sector} perto de mim",
            f"{sector} próximo",
            f"empresa {sector}",
            f"negócio {sector}"
        ]
        return base_keywords
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        return self.collection_stats.copy()
    
    def get_llm_stats(self) -> Dict:
        """Get LLM usage statistics"""
        return self.intelligent_analyzer.get_llm_stats() 