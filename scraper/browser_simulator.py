#!/usr/bin/env python3
"""
Optimized Browser Simulator for Lead Collection
Enhanced version with better performance and reliability
"""

import asyncio
import logging
import os
import time
import random
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BrowserSimulator:
    """Optimized browser simulator for lead collection"""
    
    def __init__(self, headless: bool = True, timeout: int = 15000):
        """Initialize browser simulator with optimized settings"""
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.page = None
        
        # Performance optimizations
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.viewport = {"width": 1280, "height": 720}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with optimizations
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
                '--disable-images',  # Faster loading
                '--disable-javascript',  # Faster loading for screenshots
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-ipc-flooding-protection'
            ]
        )
        
        # Create page with optimizations
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size(self.viewport)
        # Set user agent using context instead of page method
        await self.page.context.set_extra_http_headers({"User-Agent": self.user_agent})
        
        # Set timeouts
        self.page.set_default_timeout(self.timeout)
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def search_google_maps_with_screenshot(self, keyword: str, region: str) -> List[Dict]:
        """Search Google Maps and extract leads from screenshot"""
        try:
            # Construct URL
            query = f"{keyword} {region}"
            url = f"https://www.google.com/maps/search/{query.replace(' ', '%20')}"
            
            logger.info(f"Navigating to {url}")
            
            # Navigate with retry logic
            await self._navigate_with_retry(url)
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Take screenshot for debugging (optional)
            screenshot_path = f"debug_screenshots/google_maps_{keyword.replace(' ', '_')}_{region.replace(' ', '_')}.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await self.page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Extract leads from page content
            leads = await self._extract_google_maps_leads()
            
            logger.info(f"Extracted {len(leads)} leads from Google Maps screenshot")
            return leads
            
        except Exception as e:
            logger.error(f"Error in Google Maps search: {e}")
            return []
    
    async def search_google_with_screenshot(self, keyword: str, region: str) -> List[Dict]:
        """Search Google and extract leads from screenshot"""
        try:
            # Construct URL
            query = f"{keyword} {region}"
            url = f"https://www.google.com/search?q={query.replace(' ', '%20')}&num=30&hl=pt-BR&gl=br"
            
            logger.info(f"Navigating to {url}")
            
            # Navigate with retry logic
            await self._navigate_with_retry(url)
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Take screenshot for debugging (optional)
            screenshot_path = f"debug_screenshots/google_search_{keyword.replace(' ', '_')}_{region.replace(' ', '_')}.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await self.page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Extract leads from page content
            leads = await self._extract_google_search_leads()
            
            logger.info(f"Extracted {len(leads)} leads from Google Search screenshot")
            return leads
            
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
            return []
    
    async def search_bing_with_screenshot(self, keyword: str, region: str) -> List[Dict]:
        """Search Bing and extract leads from screenshot"""
        try:
            # Construct URL
            query = f"{keyword} {region}"
            url = f"https://www.bing.com/search?q={query.replace(' ', '%20')}&cc=BR&setlang=pt-BR"
            
            logger.info(f"Navigating to {url}")
            
            # Navigate with retry logic
            await self._navigate_with_retry(url)
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Take screenshot for debugging (optional)
            screenshot_path = f"debug_screenshots/bing_search_{keyword.replace(' ', '_')}_{region.replace(' ', '_')}.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await self.page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Extract leads from page content
            leads = await self._extract_bing_search_leads()
            
            logger.info(f"Extracted {len(leads)} leads from Bing screenshot")
            return leads
            
        except Exception as e:
            logger.error(f"Error in Bing search: {e}")
            return []
    
    async def extract_leads_from_screenshot(self, url: str, screenshot_path: str) -> List[Dict]:
        """Extract leads from a webpage screenshot and content"""
        try:
            logger.info(f"Extracting leads from: {url}")
            
            # Navigate to URL
            await self._navigate_with_retry(url)
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Take screenshot if path provided
            if screenshot_path:
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                await self.page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Extract leads based on URL type
            if "google.com/maps" in url:
                leads = await self._extract_google_maps_leads()
            elif "google.com/search" in url:
                leads = await self._extract_google_search_leads()
            elif "bing.com" in url:
                leads = await self._extract_bing_search_leads()
            else:
                # Generic extraction for other sites
                leads = await self._extract_generic_leads()
            
            logger.info(f"Extracted {len(leads)} leads from {url}")
            return leads
            
        except Exception as e:
            logger.error(f"Error extracting leads from {url}: {e}")
            return []
    
    async def _navigate_with_retry(self, url: str, max_retries: int = 3):
        """Navigate to URL with retry logic"""
        for attempt in range(max_retries):
            try:
                await self.page.goto(url, wait_until='domcontentloaded')
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(random.uniform(1, 3))
    
    async def _extract_google_maps_leads(self) -> List[Dict]:
        """Extract leads from Google Maps page"""
        try:
            # Wait for results to load
            await self.page.wait_for_selector('[data-result-index]', timeout=10000)
            
            # Extract business information
            leads = []
            
            # Get all business cards
            business_cards = await self.page.query_selector_all('[data-result-index]')
            
            for card in business_cards[:10]:  # Limit to first 10 results
                try:
                    # Extract business name
                    name_element = await card.query_selector('h3, .fontHeadlineSmall')
                    name = await name_element.text_content() if name_element else ""
                    
                    if not name or len(name.strip()) < 3:
                        continue
                    
                    # Extract address
                    address_element = await card.query_selector('[data-item-id*="address"]')
                    address = await address_element.text_content() if address_element else ""
                    
                    # Extract phone
                    phone_element = await card.query_selector('[data-item-id*="phone"]')
                    phone = await phone_element.text_content() if phone_element else ""
                    
                    # Extract website
                    website_element = await card.query_selector('a[href*="http"]')
                    website = await website_element.get_attribute('href') if website_element else ""
                    
                    # Create lead object
                    lead = {
                        'name': name.strip(),
                        'address': address.strip() if address else "",
                        'phone': phone.strip() if phone else "",
                        'website': website.strip() if website else "",
                        'source': 'google_maps',
                        'description': f"Found on Google Maps"
                    }
                    
                    leads.append(lead)
                    
                except Exception as e:
                    logger.debug(f"Error extracting lead from card: {e}")
                    continue
            
            return leads
            
        except Exception as e:
            logger.error(f"Error extracting Google Maps leads: {e}")
            return []
    
    async def _extract_google_search_leads(self) -> List[Dict]:
        """Extract leads from Google Search page"""
        try:
            # Wait for results to load
            await self.page.wait_for_selector('h3', timeout=10000)
            
            leads = []
            
            # Get all search results
            results = await self.page.query_selector_all('h3')
            
            for result in results[:15]:  # Limit to first 15 results
                try:
                    # Get the title
                    title = await result.text_content()
                    
                    if not title or len(title.strip()) < 3:
                        continue
                    
                    # Get the parent container for more info
                    parent = await result.query_selector('xpath=..')
                    if not parent:
                        continue
                    
                    # Extract snippet
                    snippet_element = await parent.query_selector('[data-snf]')
                    snippet = await snippet_element.text_content() if snippet_element else ""
                    
                    # Extract URL
                    link_element = await result.query_selector('xpath=..')
                    url = await link_element.get_attribute('href') if link_element else ""
                    
                    # Create lead object
                    lead = {
                        'name': title.strip(),
                        'description': snippet.strip() if snippet else "",
                        'website': url.strip() if url else "",
                        'source': 'google_search',
                        'address': "",
                        'phone': ""
                    }
                    
                    leads.append(lead)
                    
                except Exception as e:
                    logger.debug(f"Error extracting lead from result: {e}")
                    continue
            
            return leads
            
        except Exception as e:
            logger.error(f"Error extracting Google Search leads: {e}")
            return []
    
    async def _extract_bing_search_leads(self) -> List[Dict]:
        """Extract leads from Bing Search page"""
        try:
            # Wait for results to load
            await self.page.wait_for_selector('h2', timeout=10000)
            
            leads = []
            
            # Get all search results
            results = await self.page.query_selector_all('h2')
            
            for result in results[:15]:  # Limit to first 15 results
                try:
                    # Get the title
                    title = await result.text_content()
                    
                    if not title or len(title.strip()) < 3:
                        continue
                    
                    # Get the parent container for more info
                    parent = await result.query_selector('xpath=..')
                    if not parent:
                        continue
                    
                    # Extract snippet
                    snippet_element = await parent.query_selector('p')
                    snippet = await snippet_element.text_content() if snippet_element else ""
                    
                    # Extract URL
                    link_element = await result.query_selector('xpath=..')
                    url = await link_element.get_attribute('href') if link_element else ""
                    
                    # Create lead object
                    lead = {
                        'name': title.strip(),
                        'description': snippet.strip() if snippet else "",
                        'website': url.strip() if url else "",
                        'source': 'bing_search',
                        'address': "",
                        'phone': ""
                    }
                    
                    leads.append(lead)
                    
                except Exception as e:
                    logger.debug(f"Error extracting lead from result: {e}")
                    continue
            
            return leads
            
        except Exception as e:
            logger.error(f"Error extracting Bing Search leads: {e}")
            return [] 

    async def _extract_generic_leads(self) -> List[Dict]:
        """Extract leads from generic websites"""
        try:
            # Get page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            leads = []
            
            # Look for business information in common patterns
            # Business names in headings
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                text = heading.get_text(strip=True)
                if len(text) > 3 and len(text) < 100:  # Reasonable business name length
                    leads.append({
                        'name': text,
                        'source': 'generic_heading',
                        'description': '',
                        'website': '',
                        'phone': '',
                        'email': '',
                        'address': '',
                        'confidence': 0.3
                    })
            
            # Look for contact information
            contact_patterns = [
                r'[\w\.-]+@[\w\.-]+\.\w+',  # Email
                r'\(\d{2,3}\)\s*\d{4,5}-?\d{4}',  # Brazilian phone
                r'\d{2,3}\s*\d{4,5}-?\d{4}'  # Brazilian phone without parentheses
            ]
            
            page_text = soup.get_text()
            for pattern in contact_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    leads.append({
                        'name': 'Unknown Business',
                        'source': 'generic_contact',
                        'description': '',
                        'website': '',
                        'phone': match if 'phone' in pattern else '',
                        'email': match if '@' in match else '',
                        'address': '',
                        'confidence': 0.2
                    })
            
            # Remove duplicates based on name
            unique_leads = []
            seen_names = set()
            for lead in leads:
                name = lead['name'].lower().strip()
                if name not in seen_names and name != 'unknown business':
                    seen_names.add(name)
                    unique_leads.append(lead)
            
            return unique_leads[:20]  # Limit results
            
        except Exception as e:
            logger.error(f"Error in generic lead extraction: {e}")
            return [] 