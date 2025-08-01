import re
import asyncio
import aiohttp
from typing import Optional, List, Dict
from playwright.async_api import async_playwright
from utils.logger import get_logger

logger = get_logger(__name__)

class EmailExtractor:
    def __init__(self):
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'contato@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            r'info@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            r'comercial@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            r'vendas@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            r'atendimento@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
        ]
        
        self.common_contact_paths = [
            '/contato',
            '/contact',
            '/fale-conosco',
            '/atendimento',
            '/sobre',
            '/about',
            '/empresa',
            '/company'
        ]
    
    async def extract_email_from_website(self, website_url: str, business_name: str) -> Optional[str]:
        """Extract email from business website with multiple strategies"""
        if not website_url or not website_url.startswith('http'):
            return None
        
        try:
            # Strategy 1: Extract from main page
            email = await self._extract_from_page(website_url)
            if email:
                logger.info(f"Found email on main page for {business_name}: {email}")
                return email
            
            # Strategy 2: Try contact pages
            for path in self.common_contact_paths:
                contact_url = f"{website_url.rstrip('/')}{path}"
                email = await self._extract_from_page(contact_url)
                if email:
                    logger.info(f"Found email on contact page for {business_name}: {email}")
                    return email
            
            # Strategy 3: Generate common email patterns
            email = self._generate_common_email(website_url, business_name)
            if email:
                logger.info(f"Generated common email for {business_name}: {email}")
                return email
            
            logger.warning(f"No email found for {business_name} at {website_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting email for {business_name}: {e}")
            return None
    
    async def _extract_from_page(self, url: str) -> Optional[str]:
        """Extract email from a specific page"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    # Set shorter timeout
                    page.set_default_timeout(15000)
                    
                    # Navigate to page
                    await page.goto(url, wait_until="domcontentloaded")
                    await asyncio.sleep(2)
                    
                    # Get page content
                    content = await page.content()
                    
                    # Extract emails from content
                    emails = self._extract_emails_from_text(content)
                    
                    if emails:
                        # Return the first valid email
                        for email in emails:
                            if self._is_valid_email(email):
                                return email
                    
                    return None
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.debug(f"Error extracting from page {url}: {e}")
            return None
    
    def _extract_emails_from_text(self, text: str) -> List[str]:
        """Extract all email addresses from text"""
        emails = []
        
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emails.extend(matches)
        
        # Remove duplicates and filter
        unique_emails = list(set(emails))
        valid_emails = [email for email in unique_emails if self._is_valid_email(email)]
        
        return valid_emails
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address"""
        if not email or '@' not in email:
            return False
        
        # Basic validation
        if len(email) < 5 or len(email) > 100:
            return False
        
        # Check for common invalid patterns
        invalid_patterns = [
            'example.com',
            'test.com',
            'domain.com',
            'yourdomain.com',
            'noreply',
            'no-reply',
            'donotreply',
            'do-not-reply'
        ]
        
        email_lower = email.lower()
        for pattern in invalid_patterns:
            if pattern in email_lower:
                return False
        
        return True
    
    def _generate_common_email(self, website_url: str, business_name: str) -> Optional[str]:
        """Generate common email patterns based on domain and business name"""
        try:
            # Extract domain from URL
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', website_url)
            if not domain_match:
                return None
            
            domain = domain_match.group(1)
            
            # Clean business name for email generation
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', business_name.lower())
            
            # Common email patterns
            email_patterns = [
                f"contato@{domain}",
                f"info@{domain}",
                f"comercial@{domain}",
                f"vendas@{domain}",
                f"atendimento@{domain}",
                f"admin@{domain}",
                f"{clean_name}@{domain}",
                f"contato.{clean_name}@{domain}"
            ]
            
            # Return the first pattern (we'll validate it's not a generic one)
            for email in email_patterns:
                if self._is_valid_email(email):
                    return email
            
            return None
            
        except Exception as e:
            logger.debug(f"Error generating email for {business_name}: {e}")
            return None
    
    async def extract_emails_batch(self, leads: List[Dict]) -> List[Dict]:
        """Extract emails for a batch of leads"""
        updated_leads = []
        
        for lead in leads:
            website = lead.get('website', '')
            business_name = lead.get('name', '')
            
            if website and business_name:
                email = await self.extract_email_from_website(website, business_name)
                if email:
                    lead['email'] = email
                else:
                    # Generate fallback email
                    fallback_email = self._generate_common_email(website, business_name)
                    if fallback_email:
                        lead['email'] = fallback_email
                        logger.info(f"Using fallback email for {business_name}: {fallback_email}")
                    else:
                        lead['email'] = ''
                        logger.warning(f"No email found for {business_name}")
            else:
                lead['email'] = ''
                logger.warning(f"Missing website or name for lead: {lead}")
            
            updated_leads.append(lead)
        
        return updated_leads 