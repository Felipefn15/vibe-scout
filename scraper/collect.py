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
import googlemaps
from requests_html import HTMLSession

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
        
        # Initialize Google Maps API client
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if self.google_maps_api_key and self.google_maps_api_key != 'your_google_maps_api_key_here':
            try:
                self.gmaps = googlemaps.Client(key=self.google_maps_api_key)
                logger.info("Google Maps API initialized")
            except ValueError:
                self.gmaps = None
                logger.warning("Invalid Google Maps API key - using fallback methods")
        else:
            self.gmaps = None
            logger.warning("Google Maps API key not found - using fallback methods")
        
        # Initialize Google Custom Search API
        self.google_search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        # Rotate user agents
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Initialize HTML session for requests-html
        self.html_session = HTMLSession()
    
    def _get_random_user_agent(self):
        """Get a random user agent"""
        return random.choice(self.user_agents)
    
    def search_google_places_api(self, query: str, region: str) -> List[Dict]:
        """Search using Google Places API (most reliable)"""
        leads = []
        
        if not self.gmaps:
            logger.warning("Google Maps API not available")
            return leads
        
        try:
            # Get coordinates for the region
            geocode_result = self.gmaps.geocode(f"{region}, Brazil")
            if not geocode_result:
                logger.warning(f"Could not geocode region: {region}")
                return leads
            
            location = geocode_result[0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            logger.info(f"Searching Google Places API for: {query} in {region}")
            
            # Search for places
            places_result = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=50000,  # 50km radius
                keyword=query,
                type='establishment'
            )
            
            for place in places_result.get('results', []):
                try:
                    name = place.get('name', '')
                    address = place.get('vicinity', '')
                    place_id = place.get('place_id', '')
                    
                    if self._is_valid_business(name, address):
                        # Get detailed information
                        place_details = self.gmaps.place(place_id, fields=['formatted_phone_number', 'website', 'formatted_address'])
                        details = place_details.get('result', {})
                        
                        lead = {
                            'name': name,
                            'address': details.get('formatted_address', address),
                            'phone': details.get('formatted_phone_number', ''),
                            'website': details.get('website', ''),
                            'source': 'google_places_api'
                        }
                        leads.append(lead)
                        
                except Exception as e:
                    logger.warning(f"Error processing place: {e}")
                    continue
            
            # Add delay to respect API limits
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in Google Places API search: {e}")
        
        return leads
    
    def search_google_custom_search_api(self, query: str, region: str) -> List[Dict]:
        """Search using Google Custom Search API"""
        leads = []
        
        if not self.google_search_api_key or not self.google_search_engine_id:
            logger.warning("Google Custom Search API not configured")
            return leads
        
        try:
            logger.info(f"Searching Google Custom Search API for: {query} in {region}")
            
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_search_api_key,
                'cx': self.google_search_engine_id,
                'q': f"{query} {region}",
                'num': 10,
                'gl': 'br',
                'lr': 'lang_pt'
            }
            
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('items', []):
                try:
                    name = item.get('title', '')
                    website = item.get('link', '')
                    description = item.get('snippet', '')
                    
                    if self._is_valid_business(name, description):
                        lead = {
                            'name': name,
                            'website': website,
                            'description': description,
                            'source': 'google_custom_search'
                        }
                        leads.append(lead)
                        
                except Exception as e:
                    logger.warning(f"Error processing search result: {e}")
                    continue
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in Google Custom Search API: {e}")
        
        return leads
    
    def search_with_playwright(self, query: str, region: str, search_type: str = 'google') -> List[Dict]:
        """Search using Playwright with stealth techniques"""
        leads = []
        
        try:
            logger.info(f"Searching {search_type} with Playwright for: {query} in {region}")
            
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
                time.sleep(random.uniform(1, 3))
                
                if search_type == 'google':
                    search_url = f"https://www.google.com/search?q={query}+{region}&num=20&hl=pt-BR&gl=br"
                    page.goto(search_url)
                    
                    # Wait for results to load
                    page.wait_for_selector('div.g', timeout=10000)
                    
                    # Extract results
                    results = page.query_selector_all('div.g')
                    
                    for result in results[:15]:
                        try:
                            title_elem = result.query_selector('h3')
                            link_elem = result.query_selector('a')
                            snippet_elem = result.query_selector('div.VwiC3b')
                            
                            if title_elem and link_elem:
                                name = title_elem.inner_text().strip()
                                website = link_elem.get_attribute('href', '')
                                description = snippet_elem.inner_text().strip() if snippet_elem else ''
                                
                                if self._is_valid_business(name, description):
                                    lead = {
                                        'name': name,
                                        'website': website,
                                        'description': description,
                                        'source': 'google_playwright'
                                    }
                                    leads.append(lead)
                                    
                        except Exception as e:
                            logger.warning(f"Error parsing Playwright result: {e}")
                            continue
                
                elif search_type == 'bing':
                    search_url = f"https://www.bing.com/search?q={query}+{region}&cc=BR&setlang=pt-BR"
                    page.goto(search_url)
                    
                    # Wait for results
                    page.wait_for_selector('li.b_algo', timeout=10000)
                    
                    results = page.query_selector_all('li.b_algo')
                    
                    for result in results[:10]:
                        try:
                            title_elem = result.query_selector('h2')
                            link_elem = result.query_selector('a')
                            snippet_elem = result.query_selector('p')
                            
                            if title_elem and link_elem:
                                name = title_elem.inner_text().strip()
                                website = link_elem.get_attribute('href', '')
                                description = snippet_elem.inner_text().strip() if snippet_elem else ''
                                
                                if self._is_valid_business(name, description):
                                    lead = {
                                        'name': name,
                                        'website': website,
                                        'description': description,
                                        'source': 'bing_playwright'
                                    }
                                    leads.append(lead)
                                    
                        except Exception as e:
                            logger.warning(f"Error parsing Bing result: {e}")
                            continue
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Error in Playwright search: {e}")
        
        return leads
    
    def search_yellow_pages_api(self, query: str, region: str) -> List[Dict]:
        """Search Yellow Pages using requests-html (more reliable)"""
        leads = []
        
        try:
            # Try different Yellow Pages URLs with requests-html
            yellow_pages_urls = [
                f"https://www.telelistas.net/busca/{query}/{region}",
                f"https://www.guiatelefone.com.br/busca/{query}/{region}"
            ]
            
            for url in yellow_pages_urls:
                try:
                    logger.info(f"Searching Yellow Pages: {url}")
                    
                    # Use requests-html for better JavaScript support
                    response = self.html_session.get(url, timeout=30)
                    response.html.render(timeout=30)
                    
                    # Try different selectors for business listings
                    business_listings = response.html.find('div.listing, div.business-listing, div.result-item, div.company-card')
                    
                    for listing in business_listings[:5]:
                        try:
                            name_elem = listing.find('h3, a.business-name, div.company-name', first=True)
                            phone_elem = listing.find('span.phone, div.phone-number', first=True)
                            address_elem = listing.find('span.address, div.address', first=True)
                            
                            if name_elem:
                                name = name_elem.text.strip()
                                phone = phone_elem.text.strip() if phone_elem else ''
                                address = address_elem.text.strip() if address_elem else ''
                                
                                if self._is_valid_business(name, address):
                                    lead = {
                                        'name': name,
                                        'phone': phone,
                                        'address': address,
                                        'source': 'yellow_pages_api'
                                    }
                                    leads.append(lead)
                                    
                        except Exception as e:
                            logger.warning(f"Error parsing Yellow Pages listing: {e}")
                            continue
                    
                    # If we found results, break
                    if leads:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error with Yellow Pages URL {url}: {e}")
                    continue
            
            time.sleep(self.request_delay + random.uniform(1, 3))
            
        except Exception as e:
            logger.error(f"Error in Yellow Pages API search: {e}")
        
        return leads
    
    def collect_leads(self, industry: str, region: str, test_mode: bool = False, target_count: int = 25) -> List[Dict]:
        """Collect leads from multiple sources with priority to APIs"""
        all_leads = []
        
        if test_mode:
            logger.info("Running in test mode - using limited data collection")
            target_count = min(target_count, 5)
        
        # Generate search keywords based on industry
        keywords = self._generate_search_keywords(industry)
        
        logger.info(f"Collecting leads for {industry} in {region}")
        logger.info(f"Using keywords: {keywords}")
        
        for keyword in keywords[:3]:  # Use top 3 keywords to avoid rate limits
            # Priority 1: Google Places API (most reliable)
            if self.gmaps:
                places_leads = self.search_google_places_api(keyword, region)
                all_leads.extend(places_leads)
                logger.info(f"Found {len(places_leads)} leads from Google Places API")
            
            # Priority 2: Google Custom Search API
            if self.google_search_api_key:
                custom_search_leads = self.search_google_custom_search_api(keyword, region)
                all_leads.extend(custom_search_leads)
                logger.info(f"Found {len(custom_search_leads)} leads from Google Custom Search API")
            
            # Priority 3: Playwright with Google (fallback)
            if len(all_leads) < target_count // 2:
                google_playwright_leads = self.search_with_playwright(keyword, region, 'google')
                all_leads.extend(google_playwright_leads)
                logger.info(f"Found {len(google_playwright_leads)} leads from Google Playwright")
            
            # Priority 4: Playwright with Bing (fallback)
            if len(all_leads) < target_count // 2:
                bing_playwright_leads = self.search_with_playwright(keyword, region, 'bing')
                all_leads.extend(bing_playwright_leads)
                logger.info(f"Found {len(bing_playwright_leads)} leads from Bing Playwright")
            
            # Priority 5: Yellow Pages API
            yellow_leads = self.search_yellow_pages_api(keyword, region)
            all_leads.extend(yellow_leads)
            logger.info(f"Found {len(yellow_leads)} leads from Yellow Pages API")
            
            # Add delay between searches
            time.sleep(self.request_delay + random.uniform(2, 5))
        
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
    
    def _is_valid_business(self, name: str, description: str = "") -> bool:
        """Check if a result is a valid business"""
        # Filter out obvious non-business results
        invalid_keywords = [
            'wikipedia', 'wiki', 'youtube', 'facebook', 'instagram', 'twitter',
            'linkedin', 'google', 'maps', 'search', 'resultado', 'resultados',
            'página', 'página inicial', 'home', 'início', 'sobre', 'contato',
            'política', 'termos', 'privacidade', 'cookies', 'anúncio', 'anúncios',
            'busca', 'pesquisa', 'encontrar', 'localizar', 'direções', 'rota'
        ]
        
        name_lower = name.lower()
        desc_lower = description.lower()
        
        # Check for invalid keywords
        for keyword in invalid_keywords:
            if keyword in name_lower or keyword in desc_lower:
                return False
        
        # Check for minimum name length
        if len(name.strip()) < 3:
            return False
        
        # Check for obvious non-business patterns
        if re.search(r'^\d+$', name.strip()):  # Just numbers
            return False
        
        # Check for search result patterns
        if re.search(r'resultado|busca|pesquisa|encontrar', name_lower):
            return False
        
        return True
    
    def _deduplicate_and_clean_leads(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicates and clean lead data"""
        unique_leads = []
        seen_names = set()
        
        for lead in leads:
            name = lead.get('name', '').strip()
            
            # Skip if no name or already seen
            if not name or name in seen_names:
                continue
            
            # Clean and validate the lead
            if self._is_valid_business(name, lead.get('description', '')):
                # Clean the lead data
                clean_lead = {
                    'name': name,
                    'website': lead.get('website', ''),
                    'email': lead.get('email', ''),
                    'phone': lead.get('phone', ''),
                    'address': lead.get('address', ''),
                    'description': lead.get('description', ''),
                    'source': lead.get('source', 'unknown')
                }
                
                unique_leads.append(clean_lead)
                seen_names.add(name)
        
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