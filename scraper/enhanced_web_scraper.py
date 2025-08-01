#!/usr/bin/env python3
"""
Enhanced Web Scraper
Combines multiple free web scraping approaches for maximum effectiveness
"""

import asyncio
import json
import logging
import re
import time
import random
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import requests
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class EnhancedWebScraper:
    """Enhanced web scraper using multiple approaches"""
    
    def __init__(self, headless: bool = True):
        """Initialize enhanced web scraper"""
        self.headless = headless
        self.session = None
        self.playwright = None
        self.browser = None
        self.page = None
        self.ua = UserAgent()
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = 0
        self.min_delay = 1
        self.max_delay = 3
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'leads_found': 0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        
        # Initialize Playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-ipc-flooding-protection'
            ]
        )
        
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def search_multiple_sources(self, query: str, region: str, max_results: int = 50) -> List[Dict]:
        """Search multiple sources for leads"""
        all_leads = []
        
        # 1. Google Search (using requests + BeautifulSoup)
        try:
            google_leads = await self._search_google_requests(query, region)
            all_leads.extend(google_leads)
            logger.info(f"Found {len(google_leads)} leads from Google (requests)")
        except Exception as e:
            logger.error(f"Google search (requests) failed: {e}")
        
        # 2. Google Maps (using Playwright)
        try:
            maps_leads = await self._search_google_maps_playwright(query, region)
            all_leads.extend(maps_leads)
            logger.info(f"Found {len(maps_leads)} leads from Google Maps (Playwright)")
        except Exception as e:
            logger.error(f"Google Maps search failed: {e}")
        
        # 3. Bing Search (using requests)
        try:
            bing_leads = await self._search_bing_requests(query, region)
            all_leads.extend(bing_leads)
            logger.info(f"Found {len(bing_leads)} leads from Bing (requests)")
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
        
        # 4. Local business directories
        try:
            directory_leads = await self._search_local_directories(query, region)
            all_leads.extend(directory_leads)
            logger.info(f"Found {len(directory_leads)} leads from local directories")
        except Exception as e:
            logger.error(f"Local directory search failed: {e}")
        
        # Remove duplicates and limit results
        unique_leads = self._remove_duplicates(all_leads)
        self.stats['leads_found'] = len(unique_leads)
        
        return unique_leads[:max_results]
    
    async def search_google_for_problems(self, search_query: str) -> List[Dict]:
        """Search Google for web problem indicators"""
        try:
            # Use the existing Google search method
            leads = await self._search_google_requests(search_query, "")
            
            # Filter for web problem indicators
            web_problem_leads = []
            for lead in leads:
                if self._has_web_problem_indicators(lead, search_query):
                    lead['web_problem_source'] = 'google_search'
                    lead['web_problem_query'] = search_query
                    web_problem_leads.append(lead)
            
            return web_problem_leads
            
        except Exception as e:
            logger.error(f"Error searching Google for web problems: {e}")
            return []
    
    async def search_google_maps_for_problems(self, search_query: str) -> List[Dict]:
        """Search Google Maps for web problem indicators"""
        try:
            # Use the existing Google Maps search method
            leads = await self._search_google_maps_playwright(search_query, "")
            
            # Filter for web problem indicators
            web_problem_leads = []
            for lead in leads:
                if self._has_web_problem_indicators(lead, search_query):
                    lead['web_problem_source'] = 'google_maps'
                    lead['web_problem_query'] = search_query
                    web_problem_leads.append(lead)
            
            return web_problem_leads
            
        except Exception as e:
            logger.error(f"Error searching Google Maps for web problems: {e}")
            return []
    
    def _has_web_problem_indicators(self, lead: Dict, search_query: str) -> bool:
        """Check if lead has web problem indicators"""
        name = lead.get('name', '').lower()
        description = lead.get('description', '').lower()
        
        # Web problem keywords
        web_problem_keywords = [
            'sem site', 'sem página', 'sem presença digital', 'não aparece no google',
            'site ruim', 'site antigo', 'site que não funciona', 'precisa de site',
            'quer site', 'quer aparecer no google', 'quer marketing digital', 'quer seo',
            'sem website', 'sem pagina', 'sem presenca digital', 'nao aparece no google',
            'site que nao funciona', 'precisa de website', 'quer website'
        ]
        
        # Check if any web problem keywords are in the search query or lead info
        for keyword in web_problem_keywords:
            if keyword in search_query.lower() or keyword in name or keyword in description:
                return True
        
        # Check if lead has no website
        website = lead.get('website', '')
        if not website or website == '':
            return True
        
        return False
    
    async def _search_google_requests(self, query: str, region: str) -> List[Dict]:
        """Search Google using requests and BeautifulSoup"""
        try:
            await self._rate_limit()
            
            # Construct search URL
            search_query = f"{query} {region}"
            url = f"https://www.google.com/search?q={quote(search_query)}&num=30&hl=pt-BR&gl=br"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_google_search_results(content, query, region)
                else:
                    logger.warning(f"Google search returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in Google search (requests): {e}")
            return []
    
    async def _search_google_maps_playwright(self, query: str, region: str) -> List[Dict]:
        """Search Google Maps using Playwright"""
        try:
            await self._rate_limit()
            
            search_query = f"{query} {region}"
            url = f"https://www.google.com/maps/search/{quote(search_query)}"
            
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)  # Wait for dynamic content
            
            # Scroll to load more results
            for _ in range(3):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
            
            # Extract business information
            leads = await self.page.evaluate("""
                () => {
                    const leads = [];
                    const elements = document.querySelectorAll('[data-result-index]');
                    
                    elements.forEach((element, index) => {
                        try {
                            const nameElement = element.querySelector('h3, .fontHeadlineSmall, [role="heading"]');
                            const name = nameElement ? nameElement.textContent.trim() : '';
                            
                            const addressElement = element.querySelector('[data-item-id*="address"], .fontBodyMedium');
                            const address = addressElement ? addressElement.textContent.trim() : '';
                            
                            const phoneElement = element.querySelector('[data-item-id*="phone"], [data-tooltip*="phone"]');
                            const phone = phoneElement ? phoneElement.textContent.trim() : '';
                            
                            const websiteElement = element.querySelector('a[href*="http"]');
                            const website = websiteElement ? websiteElement.href : '';
                            
                            if (name) {
                                leads.push({
                                    name: name,
                                    address: address,
                                    phone: phone,
                                    website: website,
                                    source: 'google_maps',
                                    confidence: 0.8
                                });
                            }
                        } catch (e) {
                            console.error('Error extracting lead:', e);
                        }
                    });
                    
                    return leads;
                }
            """)
            
            return leads
            
        except Exception as e:
            logger.error(f"Error in Google Maps search (Playwright): {e}")
            return []
    
    async def _search_bing_requests(self, query: str, region: str) -> List[Dict]:
        """Search Bing using requests and BeautifulSoup"""
        try:
            await self._rate_limit()
            
            search_query = f"{query} {region}"
            url = f"https://www.bing.com/search?q={quote(search_query)}&cc=BR&setlang=pt-BR"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_bing_search_results(content, query, region)
                else:
                    logger.warning(f"Bing search returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in Bing search: {e}")
            return []
    
    async def _search_local_directories(self, query: str, region: str) -> List[Dict]:
        """Search local business directories"""
        leads = []
        
        # List of free local business directories
        directories = [
            {
                'name': 'Yellow Pages Brazil',
                'url': f"https://www.yellowpages.com.br/search?q={quote(query)}&l={quote(region)}",
                'parser': self._parse_yellow_pages
            },
            {
                'name': 'Guia Mais',
                'url': f"https://www.guiamais.com.br/busca/{quote(query)}/{quote(region)}",
                'parser': self._parse_guia_mais
            }
        ]
        
        for directory in directories:
            try:
                await self._rate_limit()
                
                headers = {
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                }
                
                async with self.session.get(directory['url'], headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        directory_leads = await directory['parser'](content, query, region)
                        leads.extend(directory_leads)
                        logger.info(f"Found {len(directory_leads)} leads from {directory['name']}")
                    else:
                        logger.warning(f"{directory['name']} returned status {response.status}")
                        
            except Exception as e:
                logger.error(f"Error searching {directory['name']}: {e}")
                continue
        
        return leads
    
    def _parse_google_search_results(self, content: str, query: str, region: str) -> List[Dict]:
        """Parse Google search results"""
        leads = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find search result containers
        results = soup.find_all('div', {'class': ['g', 'rc', 'result']})
        
        for result in results:
            try:
                # Extract business name
                title_element = result.find('h3') or result.find('a')
                if not title_element:
                    continue
                
                name = title_element.get_text(strip=True)
                if not name or len(name) < 3:
                    continue
                
                # Extract snippet/description
                snippet_element = result.find('span', {'class': ['st', 'snippet']})
                description = snippet_element.get_text(strip=True) if snippet_element else ''
                
                # Extract website
                link_element = result.find('a')
                website = link_element.get('href', '') if link_element else ''
                
                # Clean website URL
                if website.startswith('/url?q='):
                    website = website.split('/url?q=')[1].split('&')[0]
                
                leads.append({
                    'name': name,
                    'description': description,
                    'website': website,
                    'source': 'google_search',
                    'confidence': 0.7
                })
                
            except Exception as e:
                logger.error(f"Error parsing Google result: {e}")
                continue
        
        return leads
    
    def _parse_bing_search_results(self, content: str, query: str, region: str) -> List[Dict]:
        """Parse Bing search results"""
        leads = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find search result containers
        results = soup.find_all('li', {'class': 'b_algo'})
        
        for result in results:
            try:
                # Extract business name
                title_element = result.find('h2') or result.find('a')
                if not title_element:
                    continue
                
                name = title_element.get_text(strip=True)
                if not name or len(name) < 3:
                    continue
                
                # Extract snippet/description
                snippet_element = result.find('p')
                description = snippet_element.get_text(strip=True) if snippet_element else ''
                
                # Extract website
                link_element = result.find('a')
                website = link_element.get('href', '') if link_element else ''
                
                leads.append({
                    'name': name,
                    'description': description,
                    'website': website,
                    'source': 'bing_search',
                    'confidence': 0.6
                })
                
            except Exception as e:
                logger.error(f"Error parsing Bing result: {e}")
                continue
        
        return leads
    
    async def _parse_yellow_pages(self, content: str, query: str, region: str) -> List[Dict]:
        """Parse Yellow Pages Brazil results"""
        leads = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find business listings
        listings = soup.find_all('div', {'class': ['result', 'listing']})
        
        for listing in listings:
            try:
                # Extract business name
                name_element = listing.find('h3') or listing.find('a', {'class': 'business-name'})
                if not name_element:
                    continue
                
                name = name_element.get_text(strip=True)
                if not name:
                    continue
                
                # Extract phone
                phone_element = listing.find('span', {'class': 'phone'})
                phone = phone_element.get_text(strip=True) if phone_element else ''
                
                # Extract address
                address_element = listing.find('span', {'class': 'address'})
                address = address_element.get_text(strip=True) if address_element else ''
                
                leads.append({
                    'name': name,
                    'phone': phone,
                    'address': address,
                    'source': 'yellow_pages',
                    'confidence': 0.8
                })
                
            except Exception as e:
                logger.error(f"Error parsing Yellow Pages result: {e}")
                continue
        
        return leads
    
    async def _parse_guia_mais(self, content: str, query: str, region: str) -> List[Dict]:
        """Parse Guia Mais results"""
        leads = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find business listings
        listings = soup.find_all('div', {'class': ['result-item', 'business-card']})
        
        for listing in listings:
            try:
                # Extract business name
                name_element = listing.find('h3') or listing.find('a', {'class': 'business-name'})
                if not name_element:
                    continue
                
                name = name_element.get_text(strip=True)
                if not name:
                    continue
                
                # Extract phone
                phone_element = listing.find('span', {'class': 'phone'})
                phone = phone_element.get_text(strip=True) if phone_element else ''
                
                # Extract address
                address_element = listing.find('span', {'class': 'address'})
                address = address_element.get_text(strip=True) if address_element else ''
                
                leads.append({
                    'name': name,
                    'phone': phone,
                    'address': address,
                    'source': 'guia_mais',
                    'confidence': 0.8
                })
                
            except Exception as e:
                logger.error(f"Error parsing Guia Mais result: {e}")
                continue
        
        return leads
    
    def _remove_duplicates(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicate leads based on name and phone"""
        unique_leads = []
        seen = set()
        
        for lead in leads:
            name = lead.get('name', '').lower().strip()
            phone = lead.get('phone', '').strip()
            
            # Create unique identifier
            identifier = f"{name}_{phone}"
            
            if identifier not in seen and name:
                seen.add(identifier)
                unique_leads.append(lead)
        
        return unique_leads
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            await asyncio.sleep(self.min_delay - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return self.stats.copy() 