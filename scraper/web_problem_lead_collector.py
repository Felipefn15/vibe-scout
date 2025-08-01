#!/usr/bin/env python3
"""
Web Problem Lead Collector
Specialized collector for finding businesses with web visibility issues
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
from scraper.enhanced_web_scraper import EnhancedWebScraper
from scraper.website_analyzer import WebsiteAnalyzer

logger = logging.getLogger(__name__)

class WebProblemLeadCollector:
    """Specialized collector for businesses with web visibility problems"""
    
    def __init__(self, config_path: str = "config/lead_filters_improved.json"):
        """Initialize web problem lead collector"""
        self.lead_filter = LeadFilter(config_path)
        self.lead_scorer = LeadScorer()
        self.session = None
        
        # Initialize scrapers
        self.enhanced_scraper = None
        self.website_analyzer = None
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = 0
        self.min_delay = 2
        self.max_delay = 5
        
        # Collection statistics
        self.collection_stats = {
            'total_searches': 0,
            'leads_found': 0,
            'leads_with_web_problems': 0,
            'leads_without_website': 0,
            'leads_with_poor_seo': 0,
            'high_priority_leads': 0,
            'collection_time': 0
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        
        # Initialize scrapers
        self.enhanced_scraper = EnhancedWebScraper()
        await self.enhanced_scraper.__aenter__()
        
        self.website_analyzer = WebsiteAnalyzer()
        await self.website_analyzer.__aenter__()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        
        if self.enhanced_scraper:
            await self.enhanced_scraper.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.website_analyzer:
            await self.website_analyzer.__aexit__(exc_type, exc_val, exc_tb)
    
    async def collect_web_problem_leads(self, sector: str, region: str, 
                                      max_leads: int = 50) -> List[Dict]:
        """
        Collect leads specifically with web visibility problems
        
        Args:
            sector: Business sector (e.g., 'restaurant', 'lawyer')
            region: Geographic region (e.g., 'São Paulo')
            max_leads: Maximum number of leads to collect
            
        Returns:
            List of leads with web problems
        """
        start_time = time.time()
        logger.info(f"Starting web problem lead collection for {sector} in {region}")
        
        all_leads = []
        
        try:
            # 1. Search for businesses explicitly mentioning web problems
            web_problem_leads = await self._search_web_problem_keywords(sector, region)
            all_leads.extend(web_problem_leads)
            
            # 2. Search for businesses without websites
            no_website_leads = await self._search_no_website_businesses(sector, region)
            all_leads.extend(no_website_leads)
            
            # 3. Search for businesses with poor SEO indicators
            poor_seo_leads = await self._search_poor_seo_businesses(sector, region)
            all_leads.extend(poor_seo_leads)
            
            # 4. Search for businesses seeking digital services
            digital_service_leads = await self._search_digital_service_seekers(sector, region)
            all_leads.extend(digital_service_leads)
            
            # 5. Filter and validate leads
            valid_leads = self._filter_and_validate_leads(all_leads, sector)
            
            # 6. Analyze websites for existing leads
            enriched_leads = await self._analyze_websites_for_problems(valid_leads)
            
            # 7. Score and prioritize leads
            scored_leads = self._score_web_problem_leads(enriched_leads)
            
            # 8. Remove duplicates and sort by priority
            final_leads = self._remove_duplicates_and_sort(scored_leads)
            
            # Limit to max_leads
            final_leads = final_leads[:max_leads]
            
            # Update statistics
            self.collection_stats['collection_time'] = time.time() - start_time
            self.collection_stats['leads_found'] = len(final_leads)
            self.collection_stats['leads_with_web_problems'] = len([l for l in final_leads if l.get('web_problems', [])])
            self.collection_stats['leads_without_website'] = len([l for l in final_leads if not l.get('website')])
            self.collection_stats['leads_with_poor_seo'] = len([l for l in final_leads if l.get('seo_score', 100) < 50])
            self.collection_stats['high_priority_leads'] = len([l for l in final_leads if l.get('priority_level') == 'high'])
            
            logger.info(f"Collected {len(final_leads)} web problem leads")
            return final_leads
            
        except Exception as e:
            logger.error(f"Error in web problem lead collection: {e}")
            return []
    
    async def _search_web_problem_keywords(self, sector: str, region: str) -> List[Dict]:
        """Search for businesses mentioning web problems"""
        leads = []
        
        # Load web problem search terms from config
        config = self.lead_filter.filters
        search_terms = config.get('web_problem_search_terms', [])
        
        for term in search_terms[:10]:  # Limit to first 10 terms
            try:
                # Add sector to search term
                search_query = f"{term} {sector} {region}"
                
                # Search Google
                google_leads = await self._search_google_for_problems(search_query)
                leads.extend(google_leads)
                
                # Search Google Maps
                maps_leads = await self._search_google_maps_for_problems(search_query)
                leads.extend(maps_leads)
                
                # Add delay between searches
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error searching for term '{term}': {e}")
                continue
        
        return leads
    
    async def _search_no_website_businesses(self, sector: str, region: str) -> List[Dict]:
        """Search for businesses that likely don't have websites"""
        leads = []
        
        # Search terms that indicate no website
        no_website_terms = [
            f"empresa {sector} sem site {region}",
            f"negócio {sector} sem site {region}",
            f"negocio {sector} sem site {region}",
            f"empresa {sector} sem página web {region}",
            f"empresa {sector} sem pagina web {region}",
            f"empresa {sector} sem presença digital {region}",
            f"empresa {sector} sem presenca digital {region}"
        ]
        
        for term in no_website_terms:
            try:
                # Search Google
                google_leads = await self._search_google_for_problems(term)
                leads.extend(google_leads)
                
                # Search Google Maps
                maps_leads = await self._search_google_maps_for_problems(term)
                leads.extend(maps_leads)
                
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error searching for no website term '{term}': {e}")
                continue
        
        return leads
    
    async def _search_poor_seo_businesses(self, sector: str, region: str) -> List[Dict]:
        """Search for businesses with poor SEO indicators"""
        leads = []
        
        # Search terms that indicate SEO problems
        seo_problem_terms = [
            f"empresa {sector} não aparece no google {region}",
            f"empresa {sector} nao aparece no google {region}",
            f"negócio {sector} não aparece no google {region}",
            f"negocio {sector} nao aparece no google {region}",
            f"empresa {sector} não aparece na busca {region}",
            f"empresa {sector} nao aparece na busca {region}",
            f"empresa {sector} site ruim {region}",
            f"empresa {sector} site antigo {region}",
            f"empresa {sector} site que não funciona {region}",
            f"empresa {sector} site que nao funciona {region}"
        ]
        
        for term in seo_problem_terms:
            try:
                # Search Google
                google_leads = await self._search_google_for_problems(term)
                leads.extend(google_leads)
                
                # Search Google Maps
                maps_leads = await self._search_google_maps_for_problems(term)
                leads.extend(maps_leads)
                
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error searching for SEO problem term '{term}': {e}")
                continue
        
        return leads
    
    async def _search_digital_service_seekers(self, sector: str, region: str) -> List[Dict]:
        """Search for businesses seeking digital services"""
        leads = []
        
        # Search terms that indicate seeking digital services
        digital_service_terms = [
            f"empresa {sector} que precisa de site {region}",
            f"negócio {sector} que precisa de site {region}",
            f"negocio {sector} que precisa de site {region}",
            f"empresa {sector} que quer site {region}",
            f"negócio {sector} que quer site {region}",
            f"negocio {sector} que quer site {region}",
            f"empresa {sector} que quer aparecer no google {region}",
            f"negócio {sector} que quer aparecer no google {region}",
            f"negocio {sector} que quer aparecer no google {region}",
            f"empresa {sector} que quer marketing digital {region}",
            f"negócio {sector} que quer marketing digital {region}",
            f"negocio {sector} que quer marketing digital {region}",
            f"empresa {sector} que quer seo {region}",
            f"negócio {sector} que quer seo {region}",
            f"negocio {sector} que quer seo {region}"
        ]
        
        for term in digital_service_terms:
            try:
                # Search Google
                google_leads = await self._search_google_for_problems(term)
                leads.extend(google_leads)
                
                # Search Google Maps
                maps_leads = await self._search_google_maps_for_problems(term)
                leads.extend(maps_leads)
                
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error searching for digital service term '{term}': {e}")
                continue
        
        return leads
    
    async def _search_google_for_problems(self, search_query: str) -> List[Dict]:
        """Search Google for web problem indicators"""
        try:
            logger.info(f"Searching Google for web problems: {search_query}")
            
            # Use enhanced scraper to search Google
            leads = await self.enhanced_scraper.search_google_for_problems(search_query)
            
            # Mark these leads as having web problems
            for lead in leads:
                lead['web_problem_source'] = 'google_search'
                lead['web_problem_query'] = search_query
            
            logger.info(f"Found {len(leads)} leads from Google search for web problems")
            return leads
            
        except Exception as e:
            logger.error(f"Error searching Google for web problems: {e}")
            return []
    
    async def _search_google_maps_for_problems(self, search_query: str) -> List[Dict]:
        """Search Google Maps for web problem indicators"""
        try:
            logger.info(f"Searching Google Maps for web problems: {search_query}")
            
            # Use enhanced scraper to search Google Maps
            leads = await self.enhanced_scraper.search_google_maps_for_problems(search_query)
            
            # Mark these leads as having web problems
            for lead in leads:
                lead['web_problem_source'] = 'google_maps'
                lead['web_problem_query'] = search_query
            
            logger.info(f"Found {len(leads)} leads from Google Maps for web problems")
            return leads
            
        except Exception as e:
            logger.error(f"Error searching Google Maps for web problems: {e}")
            return []
    
    def _filter_and_validate_leads(self, leads: List[Dict], sector: str) -> List[Dict]:
        """Filter and validate leads"""
        valid_leads = []
        
        for lead in leads:
            try:
                # Basic validation
                if not self.lead_filter.is_valid_business_name(lead.get('name', '')):
                    continue
                
                # Check if lead is relevant to sector
                if not self._is_relevant_to_sector(lead, sector):
                    continue
                
                # Check if lead has web problem indicators
                if not self._has_web_problem_indicators(lead):
                    continue
                
                valid_leads.append(lead)
                
            except Exception as e:
                logger.error(f"Error validating lead {lead.get('name', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Validated {len(valid_leads)} leads from {len(leads)} total")
        return valid_leads
    
    def _is_relevant_to_sector(self, lead: Dict, sector: str) -> bool:
        """Check if lead is relevant to the target sector"""
        name = lead.get('name', '').lower()
        description = lead.get('description', '').lower()
        
        # Check if sector keywords are present
        sector_keywords = sector.lower().split()
        for keyword in sector_keywords:
            if keyword in name or keyword in description:
                return True
        
        return False
    
    def _has_web_problem_indicators(self, lead: Dict) -> bool:
        """Check if lead has web problem indicators"""
        name = lead.get('name', '').lower()
        description = lead.get('description', '').lower()
        
        # Load web problem indicators from config
        config = self.lead_filter.filters
        web_problem_indicators = config.get('web_problem_indicators', [])
        seo_problem_keywords = config.get('seo_problem_keywords', [])
        
        # Check for web problem indicators
        for indicator in web_problem_indicators:
            if indicator.lower() in name or indicator.lower() in description:
                return True
        
        # Check for SEO problem keywords
        for keyword in seo_problem_keywords:
            if keyword.lower() in name or keyword.lower() in description:
                return True
        
        return False
    
    async def _analyze_websites_for_problems(self, leads: List[Dict]) -> List[Dict]:
        """Analyze websites for existing leads to identify problems"""
        enriched_leads = []
        
        for lead in leads:
            try:
                website = lead.get('website')
                if website:
                    # Analyze website for problems
                    analysis = await self.website_analyzer.analyze_website(website)
                    
                    # Check for web problems
                    web_problems = []
                    if analysis.get('digital_maturity') == 'low':
                        web_problems.append('low_digital_maturity')
                    
                    if analysis.get('it_needs_score', 0) > 70:
                        web_problems.append('high_it_needs')
                    
                    if len(analysis.get('pain_points', [])) > 0:
                        web_problems.append('pain_points_identified')
                    
                    # Add analysis to lead
                    lead['website_analysis'] = analysis
                    lead['web_problems'] = web_problems
                    lead['seo_score'] = self._calculate_seo_score(analysis)
                else:
                    # No website - this is a web problem
                    lead['web_problems'] = ['no_website']
                    lead['seo_score'] = 0
                
                enriched_leads.append(lead)
                
            except Exception as e:
                logger.error(f"Error analyzing website for {lead.get('name', 'Unknown')}: {e}")
                lead['web_problems'] = ['analysis_error']
                enriched_leads.append(lead)
        
        return enriched_leads
    
    def _calculate_seo_score(self, analysis: Dict) -> int:
        """Calculate SEO score based on website analysis"""
        score = 100
        
        # Deduct points for various issues
        if analysis.get('digital_maturity') == 'low':
            score -= 30
        
        if len(analysis.get('pain_points', [])) > 0:
            score -= len(analysis.get('pain_points', [])) * 5
        
        if analysis.get('it_needs_score', 0) > 70:
            score -= 20
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))
    
    def _score_web_problem_leads(self, leads: List[Dict]) -> List[Dict]:
        """Score leads based on web problems"""
        scored_leads = []
        
        for lead in leads:
            try:
                score = 0
                
                # Base score for having web problems
                score += 50
                
                # Bonus for specific web problems
                web_problems = lead.get('web_problems', [])
                if 'no_website' in web_problems:
                    score += 30
                
                if 'low_digital_maturity' in web_problems:
                    score += 25
                
                if 'high_it_needs' in web_problems:
                    score += 20
                
                if 'pain_points_identified' in web_problems:
                    score += 15
                
                # Bonus for low SEO score
                seo_score = lead.get('seo_score', 100)
                if seo_score < 50:
                    score += 25
                elif seo_score < 70:
                    score += 15
                
                # Bonus for having contact information
                if lead.get('email'):
                    score += 10
                
                if lead.get('phone'):
                    score += 10
                
                # Determine priority level
                if score >= 80:
                    priority = 'high'
                elif score >= 60:
                    priority = 'medium'
                else:
                    priority = 'low'
                
                # Add scoring information
                lead['web_problem_score'] = score
                lead['priority_level'] = priority
                
                scored_leads.append(lead)
                
            except Exception as e:
                logger.error(f"Error scoring lead {lead.get('name', 'Unknown')}: {e}")
                lead['web_problem_score'] = 0
                lead['priority_level'] = 'low'
                scored_leads.append(lead)
        
        return scored_leads
    
    def _remove_duplicates_and_sort(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicates and sort by priority"""
        # Remove duplicates based on name
        seen_names = set()
        unique_leads = []
        
        for lead in leads:
            name = lead.get('name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_leads.append(lead)
        
        # Sort by web problem score (descending)
        unique_leads.sort(key=lambda x: x.get('web_problem_score', 0), reverse=True)
        
        logger.info(f"Removed duplicates: {len(leads)} -> {len(unique_leads)}")
        return unique_leads
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        return self.collection_stats.copy() 