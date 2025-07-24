import requests
import json
import time
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

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
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.request_delay = int(os.getenv('REQUEST_DELAY', 2))
    
    def search_google(self, query: str, region: str) -> List[Dict]:
        """Search Google for businesses in the specified region and industry"""
        leads = []
        
        try:
            # Google Search API simulation (using search results)
            search_url = f"https://www.google.com/search?q={query}+{region}"
            
            logger.info(f"Searching Google for: {query} in {region}")
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract business information from search results
            search_results = soup.find_all('div', class_='g')
            
            for result in search_results[:10]:  # Limit to first 10 results
                try:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    snippet_elem = result.find('div', class_='VwiC3b')
                    
                    if title_elem and link_elem:
                        lead = {
                            'name': title_elem.get_text().strip(),
                            'website': link_elem.get('href', ''),
                            'description': snippet_elem.get_text().strip() if snippet_elem else '',
                            'source': 'google_search'
                        }
                        leads.append(lead)
                        
                except Exception as e:
                    logger.warning(f"Error parsing search result: {e}")
                    continue
            
            time.sleep(self.request_delay)
            
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
        
        return leads
    
    def search_google_maps(self, query: str, region: str) -> List[Dict]:
        """Search Google Maps for local businesses"""
        leads = []
        
        try:
            # Google Maps search simulation
            maps_url = f"https://www.google.com/maps/search/{query}+{region}"
            
            logger.info(f"Searching Google Maps for: {query} in {region}")
            response = self.session.get(maps_url)
            response.raise_for_status()
            
            # Extract business information from Maps results
            # Note: This is a simplified version. In production, you might need to use
            # Google Places API or more sophisticated scraping techniques
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for business listings
            business_elements = soup.find_all('div', {'data-result-index': True})
            
            for element in business_elements[:10]:
                try:
                    name_elem = element.find('h3') or element.find('span', class_='fontHeadlineSmall')
                    address_elem = element.find('span', class_='fontBodyMedium')
                    phone_elem = element.find('span', class_='fontBodyMedium')
                    
                    if name_elem:
                        lead = {
                            'name': name_elem.get_text().strip(),
                            'address': address_elem.get_text().strip() if address_elem else '',
                            'phone': phone_elem.get_text().strip() if phone_elem else '',
                            'source': 'google_maps'
                        }
                        leads.append(lead)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Maps result: {e}")
                    continue
            
            time.sleep(self.request_delay)
            
        except Exception as e:
            logger.error(f"Error in Google Maps search: {e}")
        
        return leads
    
    def search_instagram(self, query: str, region: str) -> List[Dict]:
        """Search Instagram for business profiles"""
        leads = []
        
        try:
            # Instagram search simulation
            # Note: Instagram has strict anti-scraping measures
            # In production, you might need to use Instagram's API or other methods
            
            logger.info(f"Searching Instagram for: {query} in {region}")
            
            # For demo purposes, we'll create mock Instagram data
            # In a real implementation, you would scrape Instagram or use their API
            
            mock_instagram_leads = [
                {
                    'name': f"{query.capitalize()} {region}",
                    'instagram_handle': f"@{query.lower()}_{region.lower()}",
                    'followers': '1.2k',
                    'posts_count': 45,
                    'source': 'instagram'
                },
                {
                    'name': f"Premium {query} {region}",
                    'instagram_handle': f"@premium_{query.lower()}",
                    'followers': '3.5k',
                    'posts_count': 120,
                    'source': 'instagram'
                }
            ]
            
            leads.extend(mock_instagram_leads)
            time.sleep(self.request_delay)
            
        except Exception as e:
            logger.error(f"Error in Instagram search: {e}")
        
        return leads
    
    def collect_leads(self, industry: str, region: str, test_mode: bool = False) -> List[Dict]:
        """Main method to collect leads from all sources"""
        all_leads = []
        
        logger.info(f"Starting lead collection for {industry} in {region}")
        
        if test_mode:
            # Return mock data for testing
            mock_leads = [
                {
                    'name': f'Restaurante Teste 1',
                    'website': 'https://restauranteteste1.com',
                    'email': 'test.restauranteteste1@example.com',
                    'phone': '(11) 99999-9999',
                    'address': 'Rua Teste 1, São Paulo, SP',
                    'source': 'google_search'
                },
                {
                    'name': f'Restaurante Teste 2',
                    'website': 'https://restauranteteste2.com',
                    'email': 'test.restauranteteste2@example.com',
                    'phone': '(11) 88888-8888',
                    'address': 'Rua Teste 2, São Paulo, SP',
                    'source': 'google_maps'
                }
            ]
            logger.info(f"Test mode: Collected {len(mock_leads)} mock leads")
            return mock_leads
        
        # Collect from Google Search
        google_leads = self.search_google(industry, region)
        all_leads.extend(google_leads)
        
        # Collect from Google Maps
        maps_leads = self.search_google_maps(industry, region)
        all_leads.extend(maps_leads)
        
        # Collect from Instagram
        instagram_leads = self.search_instagram(industry, region)
        all_leads.extend(instagram_leads)
        
        # Remove duplicates based on name
        unique_leads = []
        seen_names = set()
        
        for lead in all_leads:
            if lead['name'] not in seen_names:
                unique_leads.append(lead)
                seen_names.add(lead['name'])
        
        logger.info(f"Collected {len(unique_leads)} unique leads")
        
        return unique_leads

def main(industry: str, region: str) -> List[Dict]:
    """Main function to be called by CrewAI"""
    collector = LeadCollector()
    leads = collector.collect_leads(industry, region)
    
    # Save leads to JSON file for next step
    with open('leads_data.json', 'w') as f:
        json.dump(leads, f, indent=2)
    
    return leads

if __name__ == "__main__":
    # Test the scraper
    test_leads = main("restaurant", "São Paulo")
    print(f"Collected {len(test_leads)} leads")
    for lead in test_leads[:3]:
        print(f"- {lead['name']} ({lead['source']})") 