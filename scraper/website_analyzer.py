#!/usr/bin/env python3
"""
Website Analyzer for IT Consulting Leads
Analyzes company websites using free techniques
"""
import asyncio
import re
import logging
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
import json
import time
import random
from collections import defaultdict

logger = logging.getLogger(__name__)

class WebsiteAnalyzer:
    """Website analyzer using free techniques"""
    
    def __init__(self):
        """Initialize website analyzer"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        self.session = None
        
        # Technology indicators
        self.tech_indicators = {
            'modern_tech': [
                'react', 'angular', 'vue', 'node.js', 'python', 'django', 'flask',
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'microservices',
                'api', 'rest', 'graphql', 'typescript', 'javascript', 'html5', 'css3'
            ],
            'legacy_tech': [
                'asp.net', 'php', 'java', 'jsp', 'servlet', 'struts', 'spring',
                'oracle', 'sql server', 'mysql', 'postgresql', 'cobol', 'fortran',
                'mainframe', 'as400', 'lotus notes', 'sharepoint', 'wordpress'
            ],
            'business_apps': [
                'sap', 'oracle erp', 'microsoft dynamics', 'salesforce', 'hubspot',
                'zoho', 'pipedrive', 'monday.com', 'asana', 'trello', 'slack',
                'microsoft office', 'google workspace', 'dropbox', 'onedrive'
            ],
            'ecommerce': [
                'shopify', 'woocommerce', 'magento', 'prestashop', 'opencart',
                'nuvemshop', 'vtex', 'mercado livre', 'amazon', 'ebay'
            ]
        }
        
        # Pain point indicators
        self.pain_indicators = [
            'sistema lento', 'processo manual', 'erro humano', 'falta de integração',
            'segurança vulnerável', 'custo alto', 'escalabilidade limitada',
            'sistema antigo', 'legacy', 'planilha excel', 'papel', 'manual',
            'duplicação', 'inconsistência', 'falta de automação'
        ]
        
        # Opportunity indicators
        self.opportunity_indicators = [
            'crescimento', 'expansão', 'inovação', 'digitalização', 'automação',
            'integração', 'migração', 'upgrade', 'reestruturação', 'transformação',
            'modernização', 'otimização', 'eficiência', 'produtividade'
        ]
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def analyze_website(self, url: str) -> Dict:
        """Analyze a company website for IT consulting opportunities"""
        analysis = {
            'url': url,
            'tech_stack': [],
            'pain_points': [],
            'opportunities': [],
            'company_info': {},
            'contact_info': {},
            'digital_maturity': 'low',
            'it_needs_score': 0,
            'recommendations': []
        }
        
        try:
            logger.info(f"Analyzing website: {url}")
            
            # Add random delay
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Analyze different aspects
                    analysis['tech_stack'] = self._analyze_tech_stack(soup, html)
                    analysis['pain_points'] = self._analyze_pain_points(soup, html)
                    analysis['opportunities'] = self._analyze_opportunities(soup, html)
                    analysis['company_info'] = self._extract_company_info(soup)
                    analysis['contact_info'] = self._extract_contact_info(soup)
                    analysis['digital_maturity'] = self._assess_digital_maturity(analysis)
                    analysis['it_needs_score'] = self._calculate_it_needs_score(analysis)
                    analysis['recommendations'] = self._generate_recommendations(analysis)
                    
                else:
                    logger.warning(f"Failed to analyze website: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error analyzing website {url}: {e}")
            
        return analysis
    
    def _analyze_tech_stack(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Analyze technology stack from website"""
        tech_stack = []
        
        try:
            # Check for technology indicators in HTML
            html_lower = html.lower()
            
            # Check for modern technologies
            for tech in self.tech_indicators['modern_tech']:
                if tech in html_lower:
                    tech_stack.append(f"modern_{tech}")
            
            # Check for legacy technologies
            for tech in self.tech_indicators['legacy_tech']:
                if tech in html_lower:
                    tech_stack.append(f"legacy_{tech}")
            
            # Check for business applications
            for app in self.tech_indicators['business_apps']:
                if app in html_lower:
                    tech_stack.append(f"business_{app}")
            
            # Check for e-commerce platforms
            for platform in self.tech_indicators['ecommerce']:
                if platform in html_lower:
                    tech_stack.append(f"ecommerce_{platform}")
            
            # Check for specific HTML patterns
            if 'wordpress' in html_lower or 'wp-content' in html_lower:
                tech_stack.append('wordpress')
            
            if 'shopify' in html_lower or 'myshopify.com' in html_lower:
                tech_stack.append('shopify')
            
            # Check for JavaScript frameworks
            if 'react' in html_lower or 'reactjs' in html_lower:
                tech_stack.append('react')
            
            if 'angular' in html_lower or 'ng-' in html_lower:
                tech_stack.append('angular')
            
            if 'vue' in html_lower or 'vuejs' in html_lower:
                tech_stack.append('vue')
            
            # Check for cloud services
            if 'aws' in html_lower or 'amazonaws.com' in html_lower:
                tech_stack.append('aws')
            
            if 'azure' in html_lower or 'microsoft.com' in html_lower:
                tech_stack.append('azure')
            
            # Check for analytics and marketing tools
            if 'google-analytics' in html_lower or 'gtag' in html_lower:
                tech_stack.append('google_analytics')
            
            if 'facebook' in html_lower or 'fbq' in html_lower:
                tech_stack.append('facebook_pixel')
            
        except Exception as e:
            logger.error(f"Error analyzing tech stack: {e}")
            
        return list(set(tech_stack))  # Remove duplicates
    
    def _analyze_pain_points(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Analyze potential pain points from website content"""
        pain_points = []
        
        try:
            # Get all text content
            text_content = soup.get_text().lower()
            
            # Check for pain point indicators
            for indicator in self.pain_indicators:
                if indicator in text_content:
                    pain_points.append(indicator)
            
            # Check for specific patterns
            if 'planilha' in text_content and 'excel' in text_content:
                pain_points.append('manual_excel_processes')
            
            if 'sistema' in text_content and 'antigo' in text_content:
                pain_points.append('legacy_systems')
            
            if 'processo' in text_content and 'manual' in text_content:
                pain_points.append('manual_processes')
            
            if 'integração' in text_content and 'falta' in text_content:
                pain_points.append('lack_of_integration')
            
            if 'segurança' in text_content and ('vulnerável' in text_content or 'risco' in text_content):
                pain_points.append('security_concerns')
            
        except Exception as e:
            logger.error(f"Error analyzing pain points: {e}")
            
        return list(set(pain_points))
    
    def _analyze_opportunities(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Analyze growth opportunities from website content"""
        opportunities = []
        
        try:
            # Get all text content
            text_content = soup.get_text().lower()
            
            # Check for opportunity indicators
            for indicator in self.opportunity_indicators:
                if indicator in text_content:
                    opportunities.append(indicator)
            
            # Check for specific growth patterns
            if 'crescimento' in text_content and ('empresa' in text_content or 'negócio' in text_content):
                opportunities.append('business_growth')
            
            if 'expansão' in text_content or 'novos mercados' in text_content:
                opportunities.append('market_expansion')
            
            if 'inovação' in text_content or 'tecnologia' in text_content:
                opportunities.append('innovation_focus')
            
            if 'digitalização' in text_content or 'transformação digital' in text_content:
                opportunities.append('digital_transformation')
            
            if 'automação' in text_content or 'automatizar' in text_content:
                opportunities.append('automation_needs')
            
        except Exception as e:
            logger.error(f"Error analyzing opportunities: {e}")
            
        return list(set(opportunities))
    
    def _extract_company_info(self, soup: BeautifulSoup) -> Dict:
        """Extract company information from website"""
        company_info = {}
        
        try:
            # Extract company name from title
            title = soup.find('title')
            if title:
                company_info['name'] = title.get_text(strip=True)
            
            # Extract description from meta tags
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                company_info['description'] = meta_desc.get('content', '')
            
            # Extract keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                company_info['keywords'] = meta_keywords.get('content', '')
            
            # Look for company information in common sections
            about_sections = soup.find_all(['h1', 'h2', 'h3'], string=re.compile(r'sobre|about|empresa|company', re.I))
            for section in about_sections:
                parent = section.parent
                if parent:
                    text = parent.get_text(strip=True)
                    if len(text) > 50:  # Meaningful content
                        company_info['about_text'] = text[:500]  # First 500 chars
                        break
            
        except Exception as e:
            logger.error(f"Error extracting company info: {e}")
            
        return company_info
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information from website"""
        contact_info = {}
        
        try:
            # Extract phone numbers
            phone_pattern = re.compile(r'\(?\d{2,3}\)?\s*\d{4,5}-?\d{4}')
            text_content = soup.get_text()
            phones = phone_pattern.findall(text_content)
            if phones:
                contact_info['phones'] = list(set(phones))
            
            # Extract email addresses
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            emails = email_pattern.findall(text_content)
            if emails:
                contact_info['emails'] = list(set(emails))
            
            # Extract addresses
            address_pattern = re.compile(r'Rua|Av\.|Avenida|R\.|Alameda|Travessa.*\d{5}-?\d{3}')
            addresses = address_pattern.findall(text_content)
            if addresses:
                contact_info['addresses'] = list(set(addresses))
            
            # Look for contact forms
            contact_forms = soup.find_all('form')
            if contact_forms:
                contact_info['has_contact_form'] = True
            
            # Look for social media links
            social_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                if any(social in href for social in ['facebook', 'instagram', 'linkedin', 'twitter']):
                    social_links.append(href)
            
            if social_links:
                contact_info['social_media'] = list(set(social_links))
            
        except Exception as e:
            logger.error(f"Error extracting contact info: {e}")
            
        return contact_info
    
    def _assess_digital_maturity(self, analysis: Dict) -> str:
        """Assess company's digital maturity level"""
        tech_stack = analysis.get('tech_stack', [])
        pain_points = analysis.get('pain_points', [])
        opportunities = analysis.get('opportunities', [])
        
        # Count modern vs legacy technologies
        modern_count = len([tech for tech in tech_stack if tech.startswith('modern_')])
        legacy_count = len([tech for tech in tech_stack if tech.startswith('legacy_')])
        
        # Assess maturity based on indicators
        if modern_count > legacy_count and len(pain_points) < 3:
            return 'high'
        elif modern_count == legacy_count or len(pain_points) < 5:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_it_needs_score(self, analysis: Dict) -> int:
        """Calculate IT needs score (0-100)"""
        score = 0
        
        # Tech stack analysis
        tech_stack = analysis.get('tech_stack', [])
        legacy_count = len([tech for tech in tech_stack if tech.startswith('legacy_')])
        modern_count = len([tech for tech in tech_stack if tech.startswith('modern_')])
        
        if legacy_count > modern_count:
            score += 30  # High legacy tech needs
        elif legacy_count > 0:
            score += 20  # Some legacy tech needs
        
        # Pain points
        pain_points = analysis.get('pain_points', [])
        score += len(pain_points) * 5  # 5 points per pain point
        
        # Opportunities
        opportunities = analysis.get('opportunities', [])
        score += len(opportunities) * 3  # 3 points per opportunity
        
        # Digital maturity
        maturity = analysis.get('digital_maturity', 'low')
        if maturity == 'low':
            score += 25
        elif maturity == 'medium':
            score += 15
        
        return min(score, 100)  # Cap at 100
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate IT consulting recommendations"""
        recommendations = []
        
        tech_stack = analysis.get('tech_stack', [])
        pain_points = analysis.get('pain_points', [])
        opportunities = analysis.get('opportunities', [])
        it_needs_score = analysis.get('it_needs_score', 0)
        
        # High-level recommendations based on score
        if it_needs_score >= 80:
            recommendations.append("Transformação digital completa recomendada")
        elif it_needs_score >= 60:
            recommendations.append("Modernização de sistemas prioritária")
        elif it_needs_score >= 40:
            recommendations.append("Otimização de processos recomendada")
        
        # Specific recommendations based on pain points
        if 'manual_excel_processes' in pain_points:
            recommendations.append("Automação de processos manuais com Excel")
        
        if 'legacy_systems' in pain_points:
            recommendations.append("Migração de sistemas legados")
        
        if 'lack_of_integration' in pain_points:
            recommendations.append("Integração de sistemas")
        
        if 'security_concerns' in pain_points:
            recommendations.append("Auditoria e melhoria de segurança")
        
        # Technology-specific recommendations
        if 'wordpress' in tech_stack:
            recommendations.append("Otimização de performance WordPress")
        
        if 'legacy_asp.net' in tech_stack:
            recommendations.append("Migração para tecnologias modernas")
        
        if 'business_sap' in tech_stack:
            recommendations.append("Otimização e integração SAP")
        
        return recommendations
    
    async def analyze_multiple_websites(self, urls: List[str]) -> List[Dict]:
        """Analyze multiple websites concurrently"""
        tasks = [self.analyze_website(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                logger.error(f"Website analysis failed: {result}")
        
        return valid_results 