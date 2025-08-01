#!/usr/bin/env python3
"""
Social Media Scraper for IT Consulting Leads
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

class SocialMediaScraper:
    """Social media scraper using free techniques"""
    
    def __init__(self):
        """Initialize social media scraper"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        self.session = None
        
        # Social media indicators for IT consulting opportunities
        self.it_indicators = [
            'tecnologia', 'software', 'sistema', 'automação', 'digitalização',
            'inovação', 'transformação digital', 'cloud', 'api', 'integração',
            'erp', 'crm', 'saas', 'startup', 'scale-up', 'investimento',
            'crescimento', 'expansão', 'modernização', 'otimização'
        ]
        
        # Growth indicators
        self.growth_indicators = [
            'crescimento', 'expansão', 'novos mercados', 'investimento',
            'contratação', 'novos clientes', 'parceria', 'acordo',
            'funding', 'venture capital', 'aceleração', 'incubadora'
        ]
        
        # Pain point indicators
        self.pain_indicators = [
            'desafio', 'problema', 'dificuldade', 'limitação', 'obstáculo',
            'sistema lento', 'processo manual', 'falta de integração',
            'segurança', 'custo alto', 'escalabilidade'
        ]
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_instagram_business(self, company_name: str, location: str = "") -> List[Dict]:
        """Search for Instagram business accounts"""
        results = []
        
        try:
            # Build search query
            search_query = f"{company_name} {location}".strip()
            encoded_query = quote(search_query)
            
            # Use Instagram's search functionality
            search_url = f"https://www.instagram.com/explore/tags/{encoded_query}/"
            
            logger.info(f"Searching Instagram for: {search_query}")
            
            # Add random delay
            await asyncio.sleep(random.uniform(2, 5))
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_instagram_search(html, company_name)
                else:
                    logger.warning(f"Instagram search failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error searching Instagram: {e}")
            
        return results
    
    async def search_facebook_business(self, company_name: str, location: str = "") -> List[Dict]:
        """Search for Facebook business pages"""
        results = []
        
        try:
            # Build search query
            search_query = f"{company_name} {location}".strip()
            encoded_query = quote(search_query)
            
            # Use Facebook's search functionality
            search_url = f"https://www.facebook.com/search/pages/?q={encoded_query}"
            
            logger.info(f"Searching Facebook for: {search_query}")
            
            # Add random delay
            await asyncio.sleep(random.uniform(2, 5))
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_facebook_search(html, company_name)
                else:
                    logger.warning(f"Facebook search failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error searching Facebook: {e}")
            
        return results
    
    async def analyze_social_presence(self, company_name: str, social_urls: Dict) -> Dict:
        """Analyze social media presence for IT consulting opportunities"""
        analysis = {
            'company_name': company_name,
            'social_presence': {},
            'it_indicators': [],
            'growth_indicators': [],
            'pain_points': [],
            'engagement_metrics': {},
            'digital_maturity_score': 0,
            'opportunities': []
        }
        
        try:
            # Analyze each social platform
            for platform, url in social_urls.items():
                if url:
                    platform_data = await self._analyze_platform(platform, url)
                    analysis['social_presence'][platform] = platform_data
                    
                    # Aggregate indicators
                    analysis['it_indicators'].extend(platform_data.get('it_indicators', []))
                    analysis['growth_indicators'].extend(platform_data.get('growth_indicators', []))
                    analysis['pain_points'].extend(platform_data.get('pain_points', []))
                    
                    # Aggregate engagement metrics
                    if 'engagement' in platform_data:
                        analysis['engagement_metrics'][platform] = platform_data['engagement']
            
            # Remove duplicates
            analysis['it_indicators'] = list(set(analysis['it_indicators']))
            analysis['growth_indicators'] = list(set(analysis['growth_indicators']))
            analysis['pain_points'] = list(set(analysis['pain_points']))
            
            # Calculate digital maturity score
            analysis['digital_maturity_score'] = self._calculate_digital_maturity(analysis)
            
            # Generate opportunities
            analysis['opportunities'] = self._generate_opportunities(analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing social presence: {e}")
            
        return analysis
    
    async def _analyze_platform(self, platform: str, url: str) -> Dict:
        """Analyze a specific social media platform"""
        platform_data = {
            'url': url,
            'it_indicators': [],
            'growth_indicators': [],
            'pain_points': [],
            'engagement': {},
            'content_analysis': {}
        }
        
        try:
            # Add random delay
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Analyze content based on platform
                    if platform == 'instagram':
                        platform_data.update(self._analyze_instagram_content(soup, html))
                    elif platform == 'facebook':
                        platform_data.update(self._analyze_facebook_content(soup, html))
                    elif platform == 'linkedin':
                        platform_data.update(self._analyze_linkedin_content(soup, html))
                    elif platform == 'twitter':
                        platform_data.update(self._analyze_twitter_content(soup, html))
                    
                else:
                    logger.warning(f"Failed to analyze {platform}: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error analyzing {platform}: {e}")
            
        return platform_data
    
    def _analyze_instagram_content(self, soup: BeautifulSoup, html: str) -> Dict:
        """Analyze Instagram content for IT consulting opportunities"""
        analysis = {
            'it_indicators': [],
            'growth_indicators': [],
            'pain_points': [],
            'engagement': {},
            'content_analysis': {}
        }
        
        try:
            # Get text content
            text_content = soup.get_text().lower()
            
            # Check for IT indicators
            for indicator in self.it_indicators:
                if indicator in text_content:
                    analysis['it_indicators'].append(indicator)
            
            # Check for growth indicators
            for indicator in self.growth_indicators:
                if indicator in text_content:
                    analysis['growth_indicators'].append(indicator)
            
            # Check for pain points
            for indicator in self.pain_indicators:
                if indicator in text_content:
                    analysis['pain_points'].append(indicator)
            
            # Look for engagement metrics (if available)
            # Instagram typically doesn't show these publicly, but we can look for patterns
            if 'seguidores' in text_content or 'followers' in text_content:
                analysis['engagement']['has_followers_info'] = True
            
            # Look for business indicators
            if 'empresa' in text_content or 'business' in text_content:
                analysis['content_analysis']['business_focus'] = True
            
            if 'tecnologia' in text_content or 'tech' in text_content:
                analysis['content_analysis']['tech_focus'] = True
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram content: {e}")
            
        return analysis
    
    def _analyze_facebook_content(self, soup: BeautifulSoup, html: str) -> Dict:
        """Analyze Facebook content for IT consulting opportunities"""
        analysis = {
            'it_indicators': [],
            'growth_indicators': [],
            'pain_points': [],
            'engagement': {},
            'content_analysis': {}
        }
        
        try:
            # Get text content
            text_content = soup.get_text().lower()
            
            # Check for IT indicators
            for indicator in self.it_indicators:
                if indicator in text_content:
                    analysis['it_indicators'].append(indicator)
            
            # Check for growth indicators
            for indicator in self.growth_indicators:
                if indicator in text_content:
                    analysis['growth_indicators'].append(indicator)
            
            # Check for pain points
            for indicator in self.pain_indicators:
                if indicator in text_content:
                    analysis['pain_points'].append(indicator)
            
            # Look for engagement metrics
            if 'curtidas' in text_content or 'likes' in text_content:
                analysis['engagement']['has_likes'] = True
            
            if 'comentários' in text_content or 'comments' in text_content:
                analysis['engagement']['has_comments'] = True
            
            # Look for business page indicators
            if 'página' in text_content or 'page' in text_content:
                analysis['content_analysis']['business_page'] = True
            
            # Look for contact information
            if 'contato' in text_content or 'contact' in text_content:
                analysis['content_analysis']['has_contact_info'] = True
            
        except Exception as e:
            logger.error(f"Error analyzing Facebook content: {e}")
            
        return analysis
    
    def _analyze_linkedin_content(self, soup: BeautifulSoup, html: str) -> Dict:
        """Analyze LinkedIn content for IT consulting opportunities"""
        analysis = {
            'it_indicators': [],
            'growth_indicators': [],
            'pain_points': [],
            'engagement': {},
            'content_analysis': {}
        }
        
        try:
            # Get text content
            text_content = soup.get_text().lower()
            
            # Check for IT indicators
            for indicator in self.it_indicators:
                if indicator in text_content:
                    analysis['it_indicators'].append(indicator)
            
            # Check for growth indicators
            for indicator in self.growth_indicators:
                if indicator in text_content:
                    analysis['growth_indicators'].append(indicator)
            
            # Check for pain points
            for indicator in self.pain_indicators:
                if indicator in text_content:
                    analysis['pain_points'].append(indicator)
            
            # Look for professional indicators
            if 'empresa' in text_content or 'company' in text_content:
                analysis['content_analysis']['company_focus'] = True
            
            if 'funcionários' in text_content or 'employees' in text_content:
                analysis['content_analysis']['has_employee_info'] = True
            
            # Look for industry information
            if 'indústria' in text_content or 'industry' in text_content:
                analysis['content_analysis']['has_industry_info'] = True
            
        except Exception as e:
            logger.error(f"Error analyzing LinkedIn content: {e}")
            
        return analysis
    
    def _analyze_twitter_content(self, soup: BeautifulSoup, html: str) -> Dict:
        """Analyze Twitter content for IT consulting opportunities"""
        analysis = {
            'it_indicators': [],
            'growth_indicators': [],
            'pain_points': [],
            'engagement': {},
            'content_analysis': {}
        }
        
        try:
            # Get text content
            text_content = soup.get_text().lower()
            
            # Check for IT indicators
            for indicator in self.it_indicators:
                if indicator in text_content:
                    analysis['it_indicators'].append(indicator)
            
            # Check for growth indicators
            for indicator in self.growth_indicators:
                if indicator in text_content:
                    analysis['growth_indicators'].append(indicator)
            
            # Check for pain points
            for indicator in self.pain_indicators:
                if indicator in text_content:
                    analysis['pain_points'].append(indicator)
            
            # Look for engagement metrics
            if 'retweets' in text_content or 'retweets' in text_content:
                analysis['engagement']['has_retweets'] = True
            
            if 'likes' in text_content or 'curtidas' in text_content:
                analysis['engagement']['has_likes'] = True
            
            # Look for business indicators
            if 'empresa' in text_content or 'business' in text_content:
                analysis['content_analysis']['business_focus'] = True
            
        except Exception as e:
            logger.error(f"Error analyzing Twitter content: {e}")
            
        return analysis
    
    def _parse_instagram_search(self, html: str, company_name: str) -> List[Dict]:
        """Parse Instagram search results"""
        results = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for business accounts
            # Instagram's structure changes frequently, so we use general patterns
            business_indicators = soup.find_all(text=re.compile(r'empresa|business|company', re.I))
            
            for indicator in business_indicators:
                # Try to extract account information
                parent = indicator.parent
                if parent:
                    # Look for links
                    links = parent.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        if '/p/' in href or '/reel/' in href:
                            results.append({
                                'platform': 'instagram',
                                'url': urljoin('https://www.instagram.com', href),
                                'type': 'business_post'
                            })
            
        except Exception as e:
            logger.error(f"Error parsing Instagram search: {e}")
            
        return results
    
    def _parse_facebook_search(self, html: str, company_name: str) -> List[Dict]:
        """Parse Facebook search results"""
        results = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for business pages
            page_links = soup.find_all('a', href=re.compile(r'/pages/'))
            
            for link in page_links:
                href = link.get('href', '')
                if href:
                    results.append({
                        'platform': 'facebook',
                        'url': urljoin('https://www.facebook.com', href),
                        'type': 'business_page'
                    })
            
        except Exception as e:
            logger.error(f"Error parsing Facebook search: {e}")
            
        return results
    
    def _calculate_digital_maturity(self, analysis: Dict) -> int:
        """Calculate digital maturity score based on social presence"""
        score = 0
        
        # Base score for having social presence
        social_presence = analysis.get('social_presence', {})
        if social_presence:
            score += 20
        
        # Points for each platform
        platform_count = len(social_presence)
        score += platform_count * 10
        
        # Points for IT indicators
        it_indicators = analysis.get('it_indicators', [])
        score += len(it_indicators) * 5
        
        # Points for growth indicators
        growth_indicators = analysis.get('growth_indicators', [])
        score += len(growth_indicators) * 3
        
        # Points for engagement
        engagement_metrics = analysis.get('engagement_metrics', {})
        if engagement_metrics:
            score += 15
        
        return min(score, 100)  # Cap at 100
    
    def _generate_opportunities(self, analysis: Dict) -> List[str]:
        """Generate opportunities based on social media analysis"""
        opportunities = []
        
        it_indicators = analysis.get('it_indicators', [])
        growth_indicators = analysis.get('growth_indicators', [])
        pain_points = analysis.get('pain_points', [])
        digital_maturity_score = analysis.get('digital_maturity_score', 0)
        
        # High-level opportunities
        if digital_maturity_score >= 80:
            opportunities.append("Empresa com forte presença digital - oportunidades de otimização")
        elif digital_maturity_score >= 60:
            opportunities.append("Empresa com presença digital moderada - oportunidades de expansão")
        elif digital_maturity_score >= 40:
            opportunities.append("Empresa com presença digital limitada - oportunidades de desenvolvimento")
        else:
            opportunities.append("Empresa com baixa presença digital - oportunidades de transformação")
        
        # Specific opportunities based on indicators
        if 'tecnologia' in it_indicators or 'software' in it_indicators:
            opportunities.append("Foco em tecnologia - oportunidades de consultoria técnica")
        
        if 'crescimento' in growth_indicators or 'expansão' in growth_indicators:
            opportunities.append("Empresa em crescimento - oportunidades de escalabilidade")
        
        if 'automação' in it_indicators:
            opportunities.append("Interesse em automação - oportunidades de implementação")
        
        if 'transformação digital' in it_indicators:
            opportunities.append("Foco em transformação digital - oportunidades de consultoria estratégica")
        
        return opportunities
    
    async def search_multiple_platforms(self, company_name: str, location: str = "") -> Dict:
        """Search for company presence across multiple social platforms"""
        results = {
            'company_name': company_name,
            'instagram': [],
            'facebook': [],
            'linkedin': [],
            'twitter': []
        }
        
        try:
            # Search Instagram
            instagram_results = await self.search_instagram_business(company_name, location)
            results['instagram'] = instagram_results
            
            # Search Facebook
            facebook_results = await self.search_facebook_business(company_name, location)
            results['facebook'] = facebook_results
            
            # Add delays between searches
            await asyncio.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.error(f"Error searching multiple platforms: {e}")
            
        return results 