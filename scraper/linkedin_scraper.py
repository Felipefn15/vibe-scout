#!/usr/bin/env python3
"""
LinkedIn Scraper for IT Consulting Leads
Uses only free resources and techniques
"""
import asyncio
import re
import logging
from typing import Dict, List, Optional
from urllib.parse import quote, urljoin
import aiohttp
from bs4 import BeautifulSoup
import json
import time
import random

logger = logging.getLogger(__name__)

class LinkedInScraper:
    """LinkedIn scraper using free techniques"""
    
    def __init__(self):
        """Initialize LinkedIn scraper"""
        self.base_url = "https://www.linkedin.com"
        self.search_url = "https://www.linkedin.com/search/results/companies/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = None
        self.rate_limit_delay = 2  # seconds between requests
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_companies(self, keywords: str, location: str = "Brazil", limit: int = 20) -> List[Dict]:
        """Search for companies on LinkedIn"""
        companies = []
        
        try:
            # Build search URL with parameters
            search_params = {
                'keywords': keywords,
                'location': location,
                'origin': 'GLOBAL_SEARCH_HEADER',
                'sid': 'random_string'
            }
            
            url = f"{self.search_url}?{'&'.join([f'{k}={quote(str(v))}' for k, v in search_params.items()])}"
            
            logger.info(f"Searching LinkedIn companies: {keywords} in {location}")
            
            # Add random delay to avoid rate limiting
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    companies = self._parse_company_search_results(html, limit)
                else:
                    logger.warning(f"LinkedIn search failed with status {response.status}")
                    
        except Exception as e:
            logger.error(f"Error searching LinkedIn companies: {e}")
            
        return companies
    
    def _parse_company_search_results(self, html: str, limit: int) -> List[Dict]:
        """Parse company search results from HTML"""
        companies = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for company cards in search results
            company_cards = soup.find_all('div', class_=re.compile(r'entity-result__item'))
            
            for card in company_cards[:limit]:
                company = self._extract_company_from_card(card)
                if company:
                    companies.append(company)
                    
        except Exception as e:
            logger.error(f"Error parsing LinkedIn search results: {e}")
            
        return companies
    
    def _extract_company_from_card(self, card) -> Optional[Dict]:
        """Extract company information from a search result card"""
        try:
            company = {}
            
            # Extract company name
            name_elem = card.find('span', class_=re.compile(r'entity-result__title-text'))
            if name_elem:
                company['name'] = name_elem.get_text(strip=True)
            
            # Extract industry/sector
            industry_elem = card.find('span', class_=re.compile(r'entity-result__primary-subtitle'))
            if industry_elem:
                company['industry'] = industry_elem.get_text(strip=True)
            
            # Extract location
            location_elem = card.find('span', class_=re.compile(r'entity-result__secondary-subtitle'))
            if location_elem:
                company['location'] = location_elem.get_text(strip=True)
            
            # Extract company size (if available)
            size_elem = card.find('span', class_=re.compile(r'entity-result__tertiary-subtitle'))
            if size_elem:
                company['size'] = size_elem.get_text(strip=True)
            
            # Extract company URL
            link_elem = card.find('a', href=re.compile(r'/company/'))
            if link_elem:
                company['linkedin_url'] = urljoin(self.base_url, link_elem.get('href'))
            
            # Add source information
            company['source'] = 'LinkedIn'
            company['scraped_at'] = time.time()
            
            return company if company.get('name') else None
            
        except Exception as e:
            logger.error(f"Error extracting company from card: {e}")
            return None
    
    async def get_company_details(self, company_url: str) -> Optional[Dict]:
        """Get detailed company information"""
        try:
            await asyncio.sleep(self.rate_limit_delay)
            
            async with self.session.get(company_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_company_details(html, company_url)
                else:
                    logger.warning(f"Failed to get company details: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting company details: {e}")
            
        return None
    
    def _parse_company_details(self, html: str, company_url: str) -> Optional[Dict]:
        """Parse detailed company information from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            details = {
                'linkedin_url': company_url,
                'source': 'LinkedIn',
                'scraped_at': time.time()
            }
            
            # Extract company description
            desc_elem = soup.find('div', class_=re.compile(r'break-words'))
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Extract website
            website_elem = soup.find('a', href=re.compile(r'^https?://'))
            if website_elem:
                details['website'] = website_elem.get('href')
            
            # Extract employee count
            employee_elem = soup.find('span', string=re.compile(r'\d+.*employee'))
            if employee_elem:
                details['employee_count'] = employee_elem.get_text(strip=True)
            
            # Extract founded year
            founded_elem = soup.find('span', string=re.compile(r'Founded'))
            if founded_elem:
                details['founded'] = founded_elem.get_text(strip=True)
            
            return details
            
        except Exception as e:
            logger.error(f"Error parsing company details: {e}")
            return None
    
    async def search_employees(self, company_name: str, keywords: str = "IT", limit: int = 10) -> List[Dict]:
        """Search for employees at a specific company"""
        employees = []
        
        try:
            # Build employee search URL
            search_query = f"{company_name} {keywords}"
            search_url = f"{self.base_url}/search/results/people/?keywords={quote(search_query)}"
            
            logger.info(f"Searching employees: {search_query}")
            
            await asyncio.sleep(self.rate_limit_delay)
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    employees = self._parse_employee_search_results(html, limit)
                else:
                    logger.warning(f"Employee search failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error searching employees: {e}")
            
        return employees
    
    def _parse_employee_search_results(self, html: str, limit: int) -> List[Dict]:
        """Parse employee search results from HTML"""
        employees = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for employee cards
            employee_cards = soup.find_all('div', class_=re.compile(r'entity-result__item'))
            
            for card in employee_cards[:limit]:
                employee = self._extract_employee_from_card(card)
                if employee:
                    employees.append(employee)
                    
        except Exception as e:
            logger.error(f"Error parsing employee search results: {e}")
            
        return employees
    
    def _extract_employee_from_card(self, card) -> Optional[Dict]:
        """Extract employee information from a search result card"""
        try:
            employee = {}
            
            # Extract name
            name_elem = card.find('span', class_=re.compile(r'entity-result__title-text'))
            if name_elem:
                employee['name'] = name_elem.get_text(strip=True)
            
            # Extract title
            title_elem = card.find('span', class_=re.compile(r'entity-result__primary-subtitle'))
            if title_elem:
                employee['title'] = title_elem.get_text(strip=True)
            
            # Extract company
            company_elem = card.find('span', class_=re.compile(r'entity-result__secondary-subtitle'))
            if company_elem:
                employee['company'] = company_elem.get_text(strip=True)
            
            # Extract location
            location_elem = card.find('span', class_=re.compile(r'entity-result__tertiary-subtitle'))
            if location_elem:
                employee['location'] = location_elem.get_text(strip=True)
            
            # Extract profile URL
            link_elem = card.find('a', href=re.compile(r'/in/'))
            if link_elem:
                employee['linkedin_url'] = urljoin(self.base_url, link_elem.get('href'))
            
            # Add source information
            employee['source'] = 'LinkedIn'
            employee['scraped_at'] = time.time()
            
            return employee if employee.get('name') else None
            
        except Exception as e:
            logger.error(f"Error extracting employee from card: {e}")
            return None

async def test_linkedin_scraper():
    """Test the LinkedIn scraper"""
    async with LinkedInScraper() as scraper:
        # Test company search
        companies = await scraper.search_companies("software development", "São Paulo", 5)
        print(f"Found {len(companies)} companies")
        
        for company in companies:
            print(f"- {company.get('name')} ({company.get('industry', 'N/A')})")
            
            # Get detailed information for first company
            if company.get('linkedin_url'):
                details = await scraper.get_company_details(company['linkedin_url'])
                if details:
                    print(f"  Website: {details.get('website', 'N/A')}")
                    print(f"  Employees: {details.get('employee_count', 'N/A')}")
        
        # Test employee search
        if companies:
            employees = await scraper.search_employees(companies[0]['name'], "CTO", 3)
            print(f"\nFound {len(employees)} employees")
            
            for employee in employees:
                print(f"- {employee.get('name')} ({employee.get('title', 'N/A')})")

if __name__ == "__main__":
    asyncio.run(test_linkedin_scraper()) 