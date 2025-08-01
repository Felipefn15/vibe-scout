#!/usr/bin/env python3
"""
Enhanced Lead Collection System
Integrates multiple free sources for IT consulting leads
"""
import asyncio
import json
import logging
import re
import time
import random
from typing import Dict, List, Optional
from urllib.parse import quote, urljoin
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from config.lead_filters import LeadFilter
from utils.lead_scorer import LeadScorer
from scraper.linkedin_scraper import LinkedInScraper
from scraper.website_analyzer import WebsiteAnalyzer
from scraper.social_media_scraper import SocialMediaScraper
from scraper.browser_simulator import BrowserSimulator

logger = logging.getLogger(__name__)

class LeadCollector:
    """Enhanced lead collector with multiple free sources"""
    
    def __init__(self):
        """Initialize enhanced lead collector"""
        self.lead_filter = LeadFilter()
        self.lead_scorer = LeadScorer()
        self.session = None
        
        # Initialize new scrapers
        self.linkedin_scraper = None
        self.website_analyzer = None
        self.social_media_scraper = None
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = 0
        self.min_delay = 1
        self.max_delay = 3
        self.timeout = 30000  # 30 seconds in milliseconds
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        
        # Initialize scrapers
        self.linkedin_scraper = LinkedInScraper()
        await self.linkedin_scraper.__aenter__()
        
        self.website_analyzer = WebsiteAnalyzer()
        await self.website_analyzer.__aenter__()
        
        self.social_media_scraper = SocialMediaScraper()
        await self.social_media_scraper.__aenter__()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        
        # Clean up scrapers
        if self.linkedin_scraper:
            await self.linkedin_scraper.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.website_analyzer:
            await self.website_analyzer.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.social_media_scraper:
            await self.social_media_scraper.__aexit__(exc_type, exc_val, exc_tb)
    
    async def collect_leads(self, sector: str, region: str, min_score: int = 60, 
                          include_linkedin: bool = True, include_website_analysis: bool = True,
                          include_social_media: bool = True) -> List[Dict]:
        """Collect leads from multiple sources with enhanced scoring"""
        logger.info(f"Starting enhanced lead collection for {sector} in {region}")
        
        all_leads = []
        
        try:
            # 1. Traditional sources (Google, Bing, etc.)
            traditional_leads = await self._collect_traditional_leads(sector, region)
            all_leads.extend(traditional_leads)
            
            # 2. LinkedIn scraping (if enabled)
            if include_linkedin:
                linkedin_leads = await self._collect_linkedin_leads(sector, region)
                all_leads.extend(linkedin_leads)
            
            # 3. Website analysis for leads with websites
            if include_website_analysis:
                website_leads = await self._analyze_lead_websites(all_leads)
                all_leads = website_leads  # Replace with enriched leads
            
            # 4. Social media analysis
            if include_social_media:
                social_leads = await self._analyze_social_presence(all_leads)
                all_leads = social_leads  # Replace with enriched leads
            
            # 5. Validate and filter leads
            validated_leads = []
            for lead in all_leads:
                if self._is_valid_search_result(lead):
                    validated_leads.append(lead)
            
            logger.info(f"Validated {len(validated_leads)} leads from {len(all_leads)} total")
            
            # 6. Enrich lead data
            enriched_leads = []
            for lead in validated_leads:
                enriched_lead = await self.lead_scorer.enrich_lead_data(lead)
                enriched_leads.append(enriched_lead)
            
            # 7. Score and filter by minimum score
            scored_leads = self.lead_scorer.filter_leads_by_score(enriched_leads, min_score)
            
            # 8. Remove duplicates
            final_leads = self._remove_duplicates(scored_leads)
            
            # 9. Log statistics
            stats = self.lead_scorer.get_scoring_stats(final_leads)
            logger.info(f"Final lead collection results: {stats}")
            
            return final_leads
            
        except Exception as e:
            logger.error(f"Error in enhanced lead collection: {e}")
            return []
    
    async def _collect_traditional_leads(self, sector: str, region: str) -> List[Dict]:
        """Collect leads from traditional sources (Google, Bing, etc.) using browser simulator"""
        logger.info(f"Collecting traditional leads for {sector} in {region}")
        leads = []
        
        try:
            # Generate keywords for the sector
            keywords = self._generate_keywords(sector)
            
            # Use browser simulator for better results
            async with BrowserSimulator() as browser_sim:
                for keyword in keywords:
                    # Google Maps search with screenshot analysis
                    maps_leads = await browser_sim.search_google_maps_with_screenshot(keyword, region)
                    logger.info(f"Collected {len(maps_leads)} leads from Google Maps for keyword: {keyword}")
                    leads.extend(maps_leads)
                    
                    # Google Search with screenshot analysis
                    search_leads = await browser_sim.search_google_with_screenshot(keyword, region)
                    logger.info(f"Collected {len(search_leads)} leads from Google Search for keyword: {keyword}")
                    leads.extend(search_leads)
                    
                    # Bing Search with screenshot analysis
                    bing_leads = await browser_sim.search_bing_with_screenshot(keyword, region)
                    logger.info(f"Collected {len(bing_leads)} leads from Bing Search for keyword: {keyword}")
                    leads.extend(bing_leads)
                    
                    # Add delay between searches
                    await asyncio.sleep(random.uniform(2, 4))
                
        except Exception as e:
            logger.error(f"Error collecting traditional leads: {e}")
            
        return leads
    
    async def _collect_linkedin_leads(self, sector: str, region: str) -> List[Dict]:
        """Collect leads from LinkedIn"""
        leads = []
        
        try:
            if not self.linkedin_scraper:
                logger.warning("LinkedIn scraper not initialized")
                return leads
            
            # Generate keywords for LinkedIn search
            keywords = self._generate_keywords(sector)
            
            for keyword in keywords:
                # Search for companies
                companies = await self.linkedin_scraper.search_companies(keyword, region, limit=15)
                
                for company in companies:
                    # Get detailed company information
                    if company.get('linkedin_url'):
                        details = await self.linkedin_scraper.get_company_details(company['linkedin_url'])
                        if details:
                            company.update(details)
                    
                    # Convert to lead format
                    lead = {
                        'name': company.get('name', ''),
                        'website': company.get('website', ''),
                        'phone': company.get('phone', ''),
                        'address': company.get('location', ''),
                        'description': company.get('description', ''),
                        'sector': company.get('industry', sector),
                        'source': 'linkedin',
                        'linkedin_url': company.get('linkedin_url', ''),
                        'size': company.get('size', ''),
                        'founded': company.get('founded', '')
                    }
                    
                    leads.append(lead)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(2, 4))
                
        except Exception as e:
            logger.error(f"Error collecting LinkedIn leads: {e}")
            
        return leads
    
    async def _analyze_lead_websites(self, leads: List[Dict]) -> List[Dict]:
        """Analyze websites for leads that have them"""
        enriched_leads = []
        
        try:
            if not self.website_analyzer:
                logger.warning("Website analyzer not initialized")
                return leads
            
            # Filter leads with websites
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
                await asyncio.sleep(random.uniform(3, 6))
            
            # Add leads without websites
            leads_without_websites = [lead for lead in leads if not lead.get('website')]
            enriched_leads.extend(leads_without_websites)
            
        except Exception as e:
            logger.error(f"Error analyzing lead websites: {e}")
            return leads
            
        return enriched_leads
    
    async def _analyze_social_presence(self, leads: List[Dict]) -> List[Dict]:
        """Analyze social media presence for leads"""
        enriched_leads = []
        
        try:
            if not self.social_media_scraper:
                logger.warning("Social media scraper not initialized")
                return leads
            
            logger.info(f"Analyzing social presence for {len(leads)} leads")
            
            # Analyze social presence for leads with company names
            for lead in leads:
                company_name = lead.get('name', '')
                if company_name:
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
                    await asyncio.sleep(random.uniform(1, 3))
                
                enriched_leads.append(lead)
                
        except Exception as e:
            logger.error(f"Error analyzing social presence: {e}")
            return leads
            
        return enriched_leads
    
    async def _search_google_maps_with_retry(self, keyword: str, region: str) -> List[Dict]:
        """Search Google Maps with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                return await self._search_google_maps(keyword, region)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Google Maps attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Google Maps search failed after {self.max_retries} attempts: {e}")
                    return []
    
    async def _search_google_maps(self, keyword: str, region: str) -> List[Dict]:
        """Search Google Maps with improved timeout handling and data extraction"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Set shorter timeout for faster failure
                page.set_default_timeout(self.timeout)
                
                url = f"https://www.google.com/maps/search/{keyword.replace(' ', '%20')}%20{region.replace(' ', '%20')}"
                logger.info(f"Navigating to: {url}")
                
                await page.goto(url, wait_until="domcontentloaded")  # Changed from networkidle
                await asyncio.sleep(5)  # Allow page to load more time
                
                # Take screenshot for debug
                await page.screenshot(path="debug_google_maps.png")
                logger.info("Screenshot salvo como debug_google_maps.png")
                
                # Extract business information with enhanced data
                businesses = await page.query_selector_all('[data-result-index]')
                logger.info(f"Found {len(businesses)} businesses with data-result-index")
                
                # Try alternative selectors if no results
                if not businesses:
                    businesses = await page.query_selector_all('.hfpxzc')
                    logger.info(f"Found {len(businesses)} businesses with .hfpxzc")
                
                if not businesses:
                    businesses = await page.query_selector_all('[role="article"]')
                    logger.info(f"Found {len(businesses)} businesses with [role='article']")
                
                if not businesses:
                    businesses = await page.query_selector_all('div[jsaction*="pane"]')
                    logger.info(f"Found {len(businesses)} businesses with div[jsaction*='pane']")
                
                if not businesses:
                    businesses = await page.query_selector_all('div[data-ved]')
                    logger.info(f"Found {len(businesses)} businesses with div[data-ved]")
                
                leads = []
                
                for business in businesses[:15]:  # Increased limit for better coverage
                    try:
                        # Try multiple selectors for business name
                        name_elem = await business.query_selector('h3, .fontHeadlineSmall, .fontTitleLarge')
                        if not name_elem:
                            name_elem = await business.query_selector('[role="heading"]')
                        if not name_elem:
                            name_elem = await business.query_selector('.fontHeadlineSmall')
                        if not name_elem:
                            name_elem = await business.query_selector('div[role="heading"]')
                        if not name_elem:
                            name_elem = await business.query_selector('span[aria-label]')
                        if not name_elem:
                            name_elem = await business.query_selector('div[aria-label]')
                        if not name_elem:
                            name_elem = await business.query_selector('a[aria-label]')
                        
                        if name_elem:
                            name = await name_elem.text_content()
                            logger.debug(f"Found business name: {name}")
                            
                            if name and self.lead_filter.is_valid_business_name(name):
                                # Extract additional information
                                lead_data = {
                                    'name': name.strip(),
                                    'source': 'google_maps',
                                    'keyword': keyword,
                                    'region': region,
                                    'sector': self._infer_sector_from_keyword(keyword)
                                }
                                
                                # Try to extract website with multiple selectors
                                website_elem = await business.query_selector('a[data-item-id*="website"]')
                                if not website_elem:
                                    website_elem = await business.query_selector('a[href*="http"]')
                                if website_elem:
                                    website = await website_elem.get_attribute('href')
                                    if website:
                                        lead_data['website'] = website
                                        logger.debug(f"Found website: {website}")
                                
                                # Try to extract phone with multiple selectors
                                phone_elem = await business.query_selector('a[data-item-id*="phone"]')
                                if not phone_elem:
                                    phone_elem = await business.query_selector('a[href*="tel:"]')
                                if not phone_elem:
                                    phone_elem = await business.query_selector('[aria-label*="telefone"]')
                                if phone_elem:
                                    phone = await phone_elem.text_content()
                                    if phone:
                                        lead_data['phone'] = phone.strip()
                                        logger.debug(f"Found phone: {phone}")
                                
                                # Try to extract address with multiple selectors
                                address_elem = await business.query_selector('[data-item-id*="address"]')
                                if not address_elem:
                                    address_elem = await business.query_selector('[aria-label*="endereço"]')
                                if not address_elem:
                                    address_elem = await business.query_selector('.fontBodyMedium')
                                if address_elem:
                                    address = await address_elem.text_content()
                                    if address:
                                        lead_data['address'] = address.strip()
                                        logger.debug(f"Found address: {address}")
                                
                                logger.info(f"Successfully extracted lead: {lead_data['name']}")
                                leads.append(lead_data)
                            else:
                                logger.debug(f"Invalid business name: {name}")
                        else:
                            logger.debug("No name element found for business")
                    except Exception as e:
                        logger.debug(f"Error extracting business info: {e}")
                        continue
                
                return leads
                
            finally:
                await browser.close()
    
    async def _search_google(self, keyword: str, region: str) -> List[Dict]:
        """Search Google with improved result extraction and sector inference"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                page.set_default_timeout(self.timeout)
                
                url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}+{region.replace(' ', '+')}&num=30&hl=pt-BR&gl=br"
                logger.info(f"Navigating to: {url}")
                
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                
                # Extract search results with multiple selectors
                results = await page.query_selector_all('div.yuRUbf')
                if not results:
                    results = await page.query_selector_all('div.g')
                if not results:
                    results = await page.query_selector_all('div[data-sokoban-container]')
                if not results:
                    results = await page.query_selector_all('div.tF2Cxc')
                
                logger.info(f"Found {len(results)} results with multiple selectors")
                
                leads = []
                for result in results:
                    try:
                        # Try multiple selectors for title
                        title_elem = await result.query_selector('h3')
                        if not title_elem:
                            title_elem = await result.query_selector('h2')
                        if not title_elem:
                            title_elem = await result.query_selector('a')
                        if not title_elem:
                            title_elem = await result.query_selector('[role="heading"]')
                        
                        # Try multiple selectors for link
                        link_elem = await result.query_selector('a')
                        if not link_elem:
                            link_elem = await result.query_selector('h3 a')
                        if not link_elem:
                            link_elem = await result.query_selector('h2 a')
                        
                        if title_elem and link_elem:
                            title = await title_elem.text_content()
                            link = await link_elem.get_attribute('href')
                            
                            logger.debug(f"Found Google result - Title: {title}, Link: {link}")
                            
                            if title and link and self._is_valid_search_result(title, keyword):
                                lead_data = {
                                    'name': title.strip(),
                                    'website': link,
                                    'source': 'google_search',
                                    'keyword': keyword,
                                    'region': region,
                                    'sector': self._infer_sector_from_keyword(keyword)
                                }
                                
                                # Try to extract description with multiple selectors
                                desc_elem = await result.query_selector('.VwiC3b')
                                if not desc_elem:
                                    desc_elem = await result.query_selector('.s3v9rd')
                                if not desc_elem:
                                    desc_elem = await result.query_selector('span')
                                if not desc_elem:
                                    desc_elem = await result.query_selector('p')
                                
                                if desc_elem:
                                    description = await desc_elem.text_content()
                                    if description:
                                        lead_data['description'] = description.strip()
                                        logger.debug(f"Found description: {description[:100]}...")
                                
                                logger.info(f"Successfully extracted Google lead: {lead_data['name']}")
                                leads.append(lead_data)
                            else:
                                logger.debug(f"Invalid Google result - Title: {title}, Keyword: {keyword}")
                        else:
                            logger.debug("No title or link element found for Google result")
                    except Exception as e:
                        logger.debug(f"Error extracting search result: {e}")
                        continue
                
                return leads
                
            finally:
                await browser.close()
    
    async def _search_bing(self, keyword: str, region: str) -> List[Dict]:
        """Search Bing with improved result extraction and debug logging"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                page.set_default_timeout(self.timeout)
                # Set User-Agent para navegador real
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                url = f"https://www.bing.com/search?q={keyword.replace(' ', '+')}+{region.replace(' ', '+')}&cc=BR&setlang=pt-BR"
                logger.info(f"Navigating to: {url}")
                response = await page.goto(url, wait_until="domcontentloaded")
                logger.info(f"Bing page status: {response.status if response else 'unknown'}")
                await asyncio.sleep(4)  # Delay maior para evitar bloqueio
                # Salvar HTML para debug
                html = await page.content()
                with open("debug_bing.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info("HTML da página Bing salvo em debug_bing.html")
                # Extract search results
                results = await page.query_selector_all('h2 a')
                logger.info(f"Found {len(results)} results with selector 'h2 a'")
                leads = []
                for result in results[:20]:
                    try:
                        title = await result.text_content()
                        link = await result.get_attribute('href')
                        if title and link and self._is_valid_search_result(title, keyword):
                            lead_data = {
                                'name': title.strip(),
                                'website': link,
                                'source': 'bing_search',
                                'keyword': keyword,
                                'region': region,
                                'sector': self._infer_sector_from_keyword(keyword)
                            }
                            # Try to extract description
                            parent = await result.query_selector('xpath=..')
                            if parent:
                                desc_elem = await parent.query_selector('p')
                                if desc_elem:
                                    description = await desc_elem.text_content()
                                    if description:
                                        lead_data['description'] = description.strip()
                            leads.append(lead_data)
                            logger.info(f"Exemplo de lead Bing: {lead_data['name']} - {lead_data['website']}")
                    except Exception as e:
                        logger.debug(f"Error extracting Bing result: {e}")
                        continue
                if not leads:
                    logger.warning("Nenhum lead coletado do Bing. Veja debug_bing.html para análise de seletores.")
                return leads
            finally:
                await browser.close()
    
    async def _search_yellow_pages(self, keyword: str, region: str) -> List[Dict]:
        """Search Yellow Pages with fallback URLs and improved error handling"""
        urls = [
            f"https://www.telelistas.net/busca/{keyword}/{region}",
            f"https://www.guiatelefone.com.br/busca/{keyword}/{region}",
            f"https://www.paginasamarelas.com.br/busca/{keyword}/{region}"
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                page.set_default_timeout(15000)  # Shorter timeout for Yellow Pages
                
                for url in urls:
                    try:
                        logger.info(f"Trying Yellow Pages URL: {url}")
                        await page.goto(url, wait_until="domcontentloaded")
                        await asyncio.sleep(2)
                        
                        # Extract business listings
                        listings = await page.query_selector_all('.business-listing, .result-item, .listing')
                        leads = []
                        
                        for listing in listings[:15]:  # Increased limit
                            try:
                                name_elem = await listing.query_selector('h3, .business-name, .title')
                                if name_elem:
                                    name = await name_elem.text_content()
                                    if name and self.lead_filter.is_valid_business_name(name):
                                        lead_data = {
                                            'name': name.strip(),
                                            'source': 'yellow_pages',
                                            'keyword': keyword,
                                            'region': region,
                                            'sector': self._infer_sector_from_keyword(keyword)
                                        }
                                        
                                        # Try to extract phone
                                        phone_elem = await listing.query_selector('.phone, .telefone')
                                        if phone_elem:
                                            phone = await phone_elem.text_content()
                                            if phone:
                                                lead_data['phone'] = phone.strip()
                                        
                                        # Try to extract address
                                        address_elem = await listing.query_selector('.address, .endereco')
                                        if address_elem:
                                            address = await address_elem.text_content()
                                            if address:
                                                lead_data['address'] = address.strip()
                                        
                                        leads.append(lead_data)
                            except Exception as e:
                                logger.debug(f"Error extracting Yellow Pages listing: {e}")
                                continue
                        
                        if leads:
                            return leads
                            
                    except Exception as e:
                        logger.warning(f"Error with Yellow Pages URL {url}: {e}")
                        continue
                
                return []
                
            finally:
                await browser.close()
    
    def _infer_sector_from_keyword(self, keyword: str) -> str:
        """Infer sector from search keyword"""
        keyword_lower = keyword.lower()
        
        # Load sectors configuration
        try:
            with open('config/sectors.json', 'r', encoding='utf-8') as f:
                sectors = json.load(f)
            
            for sector in sectors:
                for sector_keyword in sector['keywords']:
                    if sector_keyword.lower() in keyword_lower:
                        return sector['name']
        except Exception as e:
            logger.warning(f"Error loading sectors config: {e}")
        
        return "Outros"
    
    def _is_valid_search_result(self, lead: Dict) -> bool:
        """Improved validation for search results with IT consulting focus"""
        name = lead.get('name', '').strip().lower()
        website = lead.get('website', '').strip().lower()
        
        # Check for invalid patterns
        invalid_patterns = [
            'lista', 'guia', 'melhores', 'top', 'ranking',
            'preço', 'valor', 'quanto custa', 'orçamento',
            'home', 'página principal', 'centro', 'busca',
            'consulta', 'agendamento', 'marcar'
        ]
        
        for pattern in invalid_patterns:
            if pattern in name:
                logger.info(f"Filtered out lead '{name}' due to invalid keyword: {pattern}")
                return False
        
        # Check for question patterns
        if '?' in name or 'como' in name or 'quando' in name:
            logger.info(f"Filtered out lead '{name}' due to question pattern")
            return False
        
        # Must contain keyword or be a business name
        if not self.lead_filter.is_valid_business_name(name):
            return False
        
        return True
    
    def _generate_keywords(self, sector: str) -> List[str]:
        """Generate search keywords optimized for IT consulting"""
        # Load sector-specific keywords
        try:
            with open('config/sectors.json', 'r', encoding='utf-8') as f:
                sectors = json.load(f)
            
            for sector_data in sectors:
                if sector_data['name'].lower() == sector.lower():
                    return sector_data['keywords']
        except Exception as e:
            logger.warning(f"Error loading sector keywords: {e}")
        
        # Fallback keywords
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