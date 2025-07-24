import requests
import json
import time
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import re
import random
from playwright.sync_api import sync_playwright
import urllib.parse

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadCollector:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        })
        self.request_delay = int(os.getenv('REQUEST_DELAY', 3))
        
        # Rotate user agents
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
    
    def _get_random_user_agent(self):
        """Get a random user agent"""
        return random.choice(self.user_agents)
    
    def search_google_maps_with_playwright(self, query: str, region: str) -> List[Dict]:
        """Search Google Maps using Playwright with stealth techniques"""
        leads = []
        
        try:
            logger.info(f"Searching Google Maps with Playwright for: {query} in {region}")
            
            with sync_playwright() as p:
                # Launch browser with stealth options
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-images',
                        '--disable-javascript',
                        '--disable-gpu'
                    ]
                )
                
                context = browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={'width': 1280, 'height': 720},
                    locale='pt-BR',
                    timezone_id='America/Sao_Paulo'
                )
                
                # Add stealth scripts
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['pt-BR', 'pt', 'en'],
                    });
                """)
                
                page = context.new_page()
                
                # Random delay to simulate human behavior
                time.sleep(random.uniform(2, 4))
                
                # Navigate to Google Maps
                search_query = f"{query} {region}"
                encoded_query = urllib.parse.quote(search_query)
                maps_url = f"https://www.google.com/maps/search/{encoded_query}"
                
                logger.info(f"Navigating to: {maps_url}")
                page.goto(maps_url, wait_until='networkidle', timeout=30000)
                
                # Wait for results to load
                page.wait_for_timeout(5000)
                
                # Try to find business listings
                try:
                    # Look for business cards
                    business_cards = page.query_selector_all('[data-result-index]')
                    logger.info(f"Found {len(business_cards)} business cards")
                    
                    for i, card in enumerate(business_cards[:15]):
                        try:
                            # Extract business name
                            name_elem = card.query_selector('h3, [role="heading"], .fontHeadlineSmall')
                            if not name_elem:
                                continue
                            
                            name = name_elem.inner_text().strip()
                            
                            # Extract address
                            address_elem = card.query_selector('[data-item-id*="address"], .fontBodyMedium')
                            address = address_elem.inner_text().strip() if address_elem else ''
                            
                            # Extract phone
                            phone_elem = card.query_selector('[data-item-id*="phone"], [data-tooltip*="phone"]')
                            phone = phone_elem.inner_text().strip() if phone_elem else ''
                            
                            # Extract website
                            website_elem = card.query_selector('a[href*="http"]')
                            website = website_elem.get_attribute('href') if website_elem else ''
                            
                            if self._is_valid_business(name, address):
                                lead = {
                                    'name': name,
                                    'address': address,
                                    'phone': phone,
                                    'website': website,
                                    'source': 'google_maps_playwright'
                                }
                                leads.append(lead)
                                logger.info(f"Found business: {name}")
                                
                        except Exception as e:
                            logger.warning(f"Error parsing business card {i}: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error finding business cards: {e}")
                
                # If no business cards found, try alternative selectors
                if not leads:
                    logger.info("Trying alternative selectors...")
                    try:
                        # Look for any clickable elements that might be businesses
                        clickable_elements = page.query_selector_all('a[href*="place"], [role="button"]')
                        
                        for elem in clickable_elements[:10]:
                            try:
                                name = elem.inner_text().strip()
                                if len(name) > 3 and self._is_valid_business(name):
                                    lead = {
                                        'name': name,
                                        'address': '',
                                        'phone': '',
                                        'website': '',
                                        'source': 'google_maps_playwright_alt'
                                    }
                                    leads.append(lead)
                                    logger.info(f"Found business (alt): {name}")
                            except:
                                continue
                    except Exception as e:
                        logger.warning(f"Error with alternative selectors: {e}")
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Error in Google Maps Playwright search: {e}")
        
        return leads
    
    def search_google_with_playwright(self, query: str, region: str) -> List[Dict]:
        """Search Google using Playwright with stealth techniques"""
        leads = []
        
        try:
            logger.info(f"Searching Google with Playwright for: {query} in {region}")
            
            with sync_playwright() as p:
                # Launch browser with stealth options
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={'width': 1280, 'height': 720},
                    locale='pt-BR',
                    timezone_id='America/Sao_Paulo'
                )
                
                # Add stealth scripts
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                """)
                
                page = context.new_page()
                
                # Random delay to simulate human behavior
                time.sleep(random.uniform(2, 4))
                
                # Navigate to Google Search
                search_query = f"{query} {region}"
                encoded_query = urllib.parse.quote(search_query)
                search_url = f"https://www.google.com/search?q={encoded_query}&num=20&hl=pt-BR&gl=br"
                
                logger.info(f"Navigating to: {search_url}")
                page.goto(search_url, wait_until='networkidle', timeout=30000)
                
                # Wait for results to load
                page.wait_for_timeout(3000)
                
                # Try multiple selectors for search results
                selectors = [
                    'div.g',
                    'div[data-sokoban-container]',
                    'div.yuRUbf',
                    'div.rc'
                ]
                
                results = []
                for selector in selectors:
                    try:
                        results = page.query_selector_all(selector)
                        if results:
                            logger.info(f"Found {len(results)} results with selector: {selector}")
                            break
                    except:
                        continue
                
                for result in results[:15]:
                    try:
                        # Try multiple selectors for title
                        title_selectors = ['h3', 'a[data-ved]', '.LC20lb']
                        title_elem = None
                        for selector in title_selectors:
                            title_elem = result.query_selector(selector)
                            if title_elem:
                                break
                        
                        # Try multiple selectors for link
                        link_selectors = ['a[href]', '.WlydOe']
                        link_elem = None
                        for selector in link_selectors:
                            link_elem = result.query_selector(selector)
                            if link_elem:
                                break
                        
                        # Try multiple selectors for snippet
                        snippet_selectors = ['.VwiC3b', '.aCOpRe', '.IsZvec']
                        snippet_elem = None
                        for selector in snippet_selectors:
                            snippet_elem = result.query_selector(selector)
                            if snippet_elem:
                                break
                        
                        if title_elem and link_elem:
                            name = title_elem.inner_text().strip()
                            website = link_elem.get_attribute('href')
                            description = snippet_elem.inner_text().strip() if snippet_elem else ''
                            
                            if self._is_valid_business(name, description):
                                lead = {
                                    'name': name,
                                    'website': website,
                                    'description': description,
                                    'source': 'google_playwright'
                                }
                                leads.append(lead)
                                logger.info(f"Found business: {name}")
                                
                    except Exception as e:
                        logger.warning(f"Error parsing search result: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Error in Google Playwright search: {e}")
        
        return leads
    
    def search_bing_with_playwright(self, query: str, region: str) -> List[Dict]:
        """Search Bing using Playwright"""
        leads = []
        
        try:
            logger.info(f"Searching Bing with Playwright for: {query} in {region}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                context = browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={'width': 1280, 'height': 720},
                    locale='pt-BR'
                )
                
                page = context.new_page()
                time.sleep(random.uniform(2, 4))
                
                search_query = f"{query} {region}"
                encoded_query = urllib.parse.quote(search_query)
                search_url = f"https://www.bing.com/search?q={encoded_query}&cc=BR&setlang=pt-BR"
                
                page.goto(search_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(3000)
                
                # Look for search results
                results = page.query_selector_all('li.b_algo')
                
                for result in results[:10]:
                    try:
                        title_elem = result.query_selector('h2')
                        link_elem = result.query_selector('a')
                        snippet_elem = result.query_selector('p')
                        
                        if title_elem and link_elem:
                            name = title_elem.inner_text().strip()
                            website = link_elem.get_attribute('href')
                            description = snippet_elem.inner_text().strip() if snippet_elem else ''
                            
                            if self._is_valid_business(name, description):
                                lead = {
                                    'name': name,
                                    'website': website,
                                    'description': description,
                                    'source': 'bing_playwright'
                                }
                                leads.append(lead)
                                logger.info(f"Found business: {name}")
                                
                    except Exception as e:
                        logger.warning(f"Error parsing Bing result: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Error in Bing Playwright search: {e}")
        
        return leads
    
    def search_yellow_pages_with_playwright(self, query: str, region: str) -> List[Dict]:
        """Search Yellow Pages using Playwright"""
        leads = []
        
        try:
            logger.info(f"Searching Yellow Pages with Playwright for: {query} in {region}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                context = browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={'width': 1280, 'height': 720},
                    locale='pt-BR'
                )
                
                page = context.new_page()
                time.sleep(random.uniform(2, 4))
                
                # Try different Yellow Pages sites
                yellow_pages_urls = [
                    f"https://www.telelistas.net/busca/{query}/{region}",
                    f"https://www.guiatelefone.com.br/busca/{query}/{region}",
                    f"https://www.paginasamarelas.com.br/busca/{query}/{region}"
                ]
                
                for url in yellow_pages_urls:
                    try:
                        logger.info(f"Trying Yellow Pages URL: {url}")
                        page.goto(url, wait_until='networkidle', timeout=30000)
                        page.wait_for_timeout(3000)
                        
                        # Try different selectors for business listings
                        selectors = [
                            'div.listing',
                            'div.business-listing', 
                            'div.result-item',
                            'div.company-card',
                            'li.result-item',
                            '.business-name'
                        ]
                        
                        listings = []
                        for selector in selectors:
                            try:
                                listings = page.query_selector_all(selector)
                                if listings:
                                    logger.info(f"Found {len(listings)} listings with selector: {selector}")
                                    break
                            except:
                                continue
                        
                        for listing in listings[:5]:
                            try:
                                # Try to extract business information
                                name_elem = listing.query_selector('h3, a.business-name, div.company-name, .business-name')
                                phone_elem = listing.query_selector('span.phone, div.phone-number, .phone')
                                address_elem = listing.query_selector('span.address, div.address, .address')
                                
                                if name_elem:
                                    name = name_elem.inner_text().strip()
                                    phone = phone_elem.inner_text().strip() if phone_elem else ''
                                    address = address_elem.inner_text().strip() if address_elem else ''
                                    
                                    if self._is_valid_business(name, address):
                                        lead = {
                                            'name': name,
                                            'phone': phone,
                                            'address': address,
                                            'source': 'yellow_pages_playwright'
                                        }
                                        leads.append(lead)
                                        logger.info(f"Found business: {name}")
                                        
                            except Exception as e:
                                logger.warning(f"Error parsing Yellow Pages listing: {e}")
                                continue
                        
                        # If we found results, break
                        if leads:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Error with Yellow Pages URL {url}: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Error in Yellow Pages Playwright search: {e}")
        
        return leads
    
    def collect_leads(self, industry: str, region: str, test_mode: bool = False, target_count: int = 25) -> List[Dict]:
        """Collect leads from multiple sources using Playwright"""
        all_leads = []
        
        if test_mode:
            logger.info("Running in test mode - using limited data collection")
            target_count = min(target_count, 10)
        
        # Generate search keywords based on industry
        keywords = self._generate_search_keywords(industry)
        
        logger.info(f"Collecting leads for {industry} in {region}")
        logger.info(f"Using keywords: {keywords}")
        
        for keyword in keywords[:3]:  # Use top 3 keywords to avoid rate limits
            # Priority 1: Google Maps (most reliable for local businesses)
            maps_leads = self.search_google_maps_with_playwright(keyword, region)
            all_leads.extend(maps_leads)
            logger.info(f"Found {len(maps_leads)} leads from Google Maps")
            
            # Add delay between searches
            time.sleep(self.request_delay + random.uniform(2, 5))
            
            # Priority 2: Google Search
            if len(all_leads) < target_count // 2:
                google_leads = self.search_google_with_playwright(keyword, region)
                all_leads.extend(google_leads)
                logger.info(f"Found {len(google_leads)} leads from Google Search")
                
                time.sleep(self.request_delay + random.uniform(2, 5))
            
            # Priority 3: Bing Search
            if len(all_leads) < target_count // 2:
                bing_leads = self.search_bing_with_playwright(keyword, region)
                all_leads.extend(bing_leads)
                logger.info(f"Found {len(bing_leads)} leads from Bing Search")
                
                time.sleep(self.request_delay + random.uniform(2, 5))
            
            # Priority 4: Yellow Pages
            yellow_leads = self.search_yellow_pages_with_playwright(keyword, region)
            all_leads.extend(yellow_leads)
            logger.info(f"Found {len(yellow_leads)} leads from Yellow Pages")
            
            # Add delay between keywords
            time.sleep(self.request_delay + random.uniform(3, 7))
        
        # Remove duplicates based on name and clean data
        unique_leads = self._deduplicate_and_clean_leads(all_leads)
        
        # Limit to target count
        final_leads = unique_leads[:target_count]
        
        logger.info(f"Collected {len(final_leads)} unique leads from {len(all_leads)} total results")
        
        return final_leads
    
    def _generate_search_keywords(self, industry: str) -> List[str]:
        """Generate search keywords for any industry"""
        # Remove common words and create variations
        industry_clean = industry.lower().strip()
        
        # Generate multiple keyword variations
        keywords = [
            industry_clean,
            f"{industry_clean} {industry_clean}",
            f"melhor {industry_clean}",
            f"{industry_clean} perto de mim",
            f"{industry_clean} próximo",
            f"empresa {industry_clean}",
            f"negócio {industry_clean}"
        ]
        
        # Add industry-specific variations
        if industry_clean in ['restaurante', 'restaurantes']:
            keywords.extend(['gastronomia', 'comida', 'jantar', 'almoço', 'pizzaria', 'churrascaria'])
        elif industry_clean in ['advocacia', 'advogado']:
            keywords.extend(['escritório advocacia', 'advocacia', 'direito', 'consultoria jurídica'])
        elif industry_clean in ['farmácia', 'farmacia']:
            keywords.extend(['drogaria', 'medicamentos', 'remédios', 'farmácia popular'])
        elif industry_clean in ['clínica', 'clinica']:
            keywords.extend(['médico', 'consultório', 'saúde', 'médica', 'hospital'])
        elif industry_clean in ['academia', 'ginástica']:
            keywords.extend(['fitness', 'treino', 'esporte', 'musculação', 'academia de ginástica'])
        elif industry_clean in ['salão', 'salao']:
            keywords.extend(['beleza', 'cabeleireiro', 'estética', 'cabelo', 'salão de beleza'])
        elif industry_clean in ['imobiliária', 'imobiliaria']:
            keywords.extend(['imóveis', 'corretor', 'aluguel', 'venda', 'imobiliária'])
        elif industry_clean in ['consultoria', 'consultor']:
            keywords.extend(['assessoria', 'consulting', 'empresarial', 'consultoria empresarial'])
        
        return keywords
    
    def _load_lead_filters(self):
        """Load lead filtering configuration"""
        try:
            with open('config/lead_filters.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load lead filters config: {e}")
            return {
                "invalid_keywords": [],
                "invalid_domains": [],
                "valid_business_patterns": [],
                "minimum_name_length": 3
            }
    
    def _is_valid_business(self, name: str, description: str = "") -> bool:
        """Check if a result is a valid business"""
        filters = self._load_lead_filters()
        
        name_lower = name.lower()
        desc_lower = description.lower()
        
        # Check for invalid keywords in name or description
        for keyword in filters.get('invalid_keywords', []):
            if keyword in name_lower or keyword in desc_lower:
                logger.info(f"Filtered out lead '{name}' due to invalid keyword: {keyword}")
                return False
        
        # Check for minimum name length
        if len(name.strip()) < filters.get('minimum_name_length', 3):
            logger.info(f"Filtered out lead '{name}' due to short name")
            return False
        
        # Check for obvious non-business patterns
        if re.search(r'^\d+$', name.strip()):  # Just numbers
            logger.info(f"Filtered out lead '{name}' due to numeric only name")
            return False
        
        # Check for search result patterns
        if re.search(r'resultado|busca|pesquisa|encontrar', name_lower):
            logger.info(f"Filtered out lead '{name}' due to search result pattern")
            return False
        
        # Check for question patterns
        if re.search(r'\?|como|quando|onde|quem|por que|porque', name_lower):
            logger.info(f"Filtered out lead '{name}' due to question pattern")
            return False
        
        # Check for list/ranking patterns
        if re.search(r'melhores|top|ranking|lista|primeiro|segundo|terceiro', name_lower):
            logger.info(f"Filtered out lead '{name}' due to list/ranking pattern")
            return False
        
        # Check for educational/informational patterns
        if re.search(r'curso|aula|tutorial|guia|manual|aprenda|estude', name_lower):
            logger.info(f"Filtered out lead '{name}' due to educational pattern")
            return False
        
        return True
    
    def _is_valid_website(self, website: str) -> bool:
        """Check if a website is from a valid business domain"""
        if not website:
            return True  # Empty website is acceptable
        
        # Invalid domains that should be filtered out
        invalid_domains = [
            'wikipedia.org', 'wikipedia.com', 'wikimedia.org',
            'youtube.com', 'youtu.be', 'facebook.com', 'fb.com',
            'instagram.com', 'twitter.com', 'x.com', 'linkedin.com',
            'google.com', 'google.com.br', 'maps.google.com',
            'glassdoor.com', 'glassdoor.com.br', 'indeed.com',
            'monster.com', 'vagas.com', 'empregos.com',
            'estacio.br', 'estacio.edu.br', 'universidade',
            'blogspot.com', 'wordpress.com', 'medium.com',
            'reddit.com', 'quora.com', 'stackoverflow.com',
            'jusbrasil.com.br', 'salario.com.br', 'guia.com.br',
            'telelistas.net', 'guiatelefone.com.br', 'paginasamarelas.com.br'
        ]
        
        website_lower = website.lower()
        
        # Check if website contains any invalid domains
        for domain in invalid_domains:
            if domain in website_lower:
                return False
        
        return True
    
    def _deduplicate_and_clean_leads(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicates and clean lead data"""
        unique_leads = []
        seen_names = set()
        
        for lead in leads:
            name = lead.get('name', '').strip()
            website = lead.get('website', '')
            
            # Skip if no name or already seen
            if not name or name in seen_names:
                continue
            
            # Clean and validate the lead
            if self._is_valid_business(name, lead.get('description', '')) and self._is_valid_website(website):
                # Clean the lead data
                clean_lead = {
                    'name': name,
                    'website': website,
                    'email': lead.get('email', ''),
                    'phone': lead.get('phone', ''),
                    'address': lead.get('address', ''),
                    'description': lead.get('description', ''),
                    'source': lead.get('source', 'unknown')
                }
                
                unique_leads.append(clean_lead)
                seen_names.add(name)
                logger.info(f"Validated lead: {name}")
            else:
                logger.info(f"Filtered out invalid lead: {name}")
        
        return unique_leads

def main(industry: str, region: str) -> List[Dict]:
    """Main function to be called by the pipeline"""
    collector = LeadCollector()
    leads = collector.collect_leads(industry, region)
    
    # Save leads to JSON file for next step
    with open('data/leads.json', 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    
    return leads

if __name__ == "__main__":
    # Test the scraper
    test_leads = main("restaurantes", "Rio de Janeiro")
    print(f"Collected {len(test_leads)} leads")
    for lead in test_leads[:3]:
        print(f"- {lead['name']} ({lead['source']})") 