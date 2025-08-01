#!/usr/bin/env python3
"""
Improved Browser Simulator with Enhanced Lead Extraction
Better OCR and text analysis for extracting business leads
"""
import asyncio
import json
import logging
import random
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import base64
from urllib.parse import quote
from playwright.async_api import async_playwright, Browser, Page
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

logger = logging.getLogger(__name__)

class ImprovedBrowserSimulator:
    """Enhanced browser simulator with better lead extraction"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.screenshot_dir = Path("debug_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Real browser configurations
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # Viewport configurations
        self.viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864}
        ]
        
        # Business keywords for better detection
        self.business_keywords = [
            'advocacia', 'advogado', 'escritório', 'contabilidade', 'contador',
            'psicologia', 'psicólogo', 'dentista', 'odontologia', 'imobiliária',
            'imóveis', 'restaurante', 'pizzaria', 'farmácia', 'drogaria',
            'clínica', 'academia', 'salão', 'beleza', 'consultoria',
            'empresa', 'negócio', 'serviços', 'prestação', 'assessoria'
        ]
        
    async def __aenter__(self):
        """Initialize browser with realistic settings"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with realistic settings
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--enable-features=NetworkService,NetworkServiceLogging',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--disable-extensions-except',
                '--disable-component-extensions-with-background-pages',
                '--disable-default-apps',
                '--disable-sync',
                '--disable-translate',
                '--hide-scrollbars',
                '--mute-audio',
                '--no-default-browser-check',
                '--no-pings',
                '--no-zygote',
                '--password-store=basic',
                '--use-mock-keychain',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic settings
        viewport = random.choice(self.viewports)
        user_agent = random.choice(self.user_agents)
        
        self.context = await self.browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
            geolocation={'latitude': -22.9068, 'longitude': -43.1729},  # Rio de Janeiro
            permissions=['geolocation'],
            extra_http_headers={
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        self.page = await self.context.new_page()
        
        # Set additional headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def simulate_human_behavior(self, page: Page):
        """Simulate human-like behavior"""
        # Random mouse movements
        await page.mouse.move(
            random.randint(100, 800),
            random.randint(100, 600)
        )
        
        # Random scroll
        await page.evaluate(f"window.scrollTo(0, {random.randint(100, 500)})")
        
        # Random wait
        await asyncio.sleep(random.uniform(1, 3))

    async def take_screenshot_with_analysis(self, url: str, filename: str, 
                                          wait_time: int = 5) -> Tuple[str, Dict]:
        """Take screenshot and analyze for leads"""
        try:
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Simulate human behavior
            await self.simulate_human_behavior(self.page)
            
            # Wait for content to load
            await asyncio.sleep(wait_time)
            
            # Take screenshot
            screenshot_path = self.screenshot_dir / f"{filename}.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Analyze screenshot for leads
            analysis = await self.analyze_screenshot_for_leads(screenshot_path)
            
            return str(screenshot_path), analysis
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return "", {}

    async def analyze_screenshot_for_leads(self, screenshot_path: Path) -> Dict:
        """Enhanced screenshot analysis for lead extraction"""
        try:
            # Load image
            image = cv2.imread(str(screenshot_path))
            if image is None:
                logger.error(f"Could not load image: {screenshot_path}")
                return {}
            
            # Convert to PIL for OCR
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Extract text using OCR with better configuration
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:()[]{}@#$%&*!?-_+=/\\|<>"\' '
            text = pytesseract.image_to_string(pil_image, lang='por+eng', config=custom_config)
            
            # Parse text for lead information
            leads = self.parse_text_for_leads_improved(text)
            
            logger.info(f"Extracted {len(leads)} potential leads from screenshot")
            return {"leads": leads, "raw_text": text[:1000]}  # First 1000 chars for debug
            
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {e}")
            return {}

    def parse_text_for_leads_improved(self, text: str) -> List[Dict]:
        """Improved text parsing for lead extraction"""
        leads = []
        
        # Split text into lines and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_lead = {}
        potential_names = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip common UI elements
            if self.is_ui_element(line):
                continue
            
            # Look for business names (improved detection)
            if self.is_business_name_improved(line):
                potential_names.append(line)
                
                # If we have a previous lead, save it
                if current_lead and len(current_lead) > 1:
                    leads.append(current_lead)
                
                # Start new lead
                current_lead = {"name": line}
                
                # Look ahead for additional information
                current_lead = self.extract_lead_info_from_context(lines, i, current_lead)
                
                # If this lead has enough info, add it
                if len(current_lead) > 1:
                    leads.append(current_lead)
                    current_lead = {}
            
            # Look for phone numbers
            phone_match = re.search(r'\(?\d{2,3}\)?\s*\d{4,5}-?\d{4}', line)
            if phone_match and current_lead:
                current_lead["phone"] = phone_match.group()
            
            # Look for websites
            website_match = re.search(r'https?://[^\s]+', line)
            if website_match and current_lead:
                current_lead["website"] = website_match.group()
            
            # Look for addresses
            if self.is_address_improved(line) and current_lead:
                current_lead["address"] = line
            
            # Look for business descriptions
            if self.is_description_improved(line) and current_lead:
                current_lead["description"] = line
        
        # Add the last lead if it has meaningful content
        if current_lead and len(current_lead) > 1:
            leads.append(current_lead)
        
        # Filter and validate leads
        filtered_leads = []
        for lead in leads:
            if self.is_valid_lead_improved(lead):
                filtered_leads.append(lead)
        
        return filtered_leads

    def extract_lead_info_from_context(self, lines: List[str], current_index: int, lead: Dict) -> Dict:
        """Extract additional information from surrounding lines"""
        # Look at next few lines for additional info
        for i in range(current_index + 1, min(current_index + 5, len(lines))):
            line = lines[i].strip()
            
            # Phone number
            if not lead.get('phone'):
                phone_match = re.search(r'\(?\d{2,3}\)?\s*\d{4,5}-?\d{4}', line)
                if phone_match:
                    lead["phone"] = phone_match.group()
            
            # Website
            if not lead.get('website'):
                website_match = re.search(r'https?://[^\s]+', line)
                if website_match:
                    lead["website"] = website_match.group()
            
            # Address
            if not lead.get('address') and self.is_address_improved(line):
                lead["address"] = line
            
            # Description
            if not lead.get('description') and self.is_description_improved(line):
                lead["description"] = line
        
        return lead

    def is_business_name_improved(self, text: str) -> bool:
        """Improved business name detection"""
        # Skip if too short or too long
        if len(text) < 3 or len(text) > 80:
            return False
        
        # Skip if it's just numbers or symbols
        if re.match(r'^[\d\s\-_\.]+$', text):
            return False
        
        # Skip if it's a phone number or website
        if re.search(r'\(?\d{2,3}\)?\s*\d{4,5}-?\d{4}', text):
            return False
        if re.search(r'https?://', text):
            return False
        
        # Check if it contains business keywords
        text_lower = text.lower()
        has_business_keyword = any(keyword in text_lower for keyword in self.business_keywords)
        
        # Check if it looks like a business name (2-6 words, some capitalization)
        words = text.split()
        if 2 <= len(words) <= 6:
            # Check if it has some capitalization (business names often do)
            has_caps = any(word[0].isupper() for word in words if word)
            
            # If it has business keywords or looks like a proper name
            if has_business_keyword or has_caps:
                return True
        
        return False

    def is_address_improved(self, text: str) -> bool:
        """Improved address detection"""
        # Addresses usually contain street indicators
        address_indicators = [
            'rua', 'avenida', 'av.', 'alameda', 'praça', 'travessa', 'vila', 'bairro',
            'centro', 'zona', 'distrito', 'bairro', 'conjunto', 'residencial',
            'copacabana', 'ipanema', 'leblon', 'botafogo', 'flamengo', 'tijuca',
            'barra', 'recreio', 'jacarepaguá', 'grajaú', 'vila isabel'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in address_indicators)

    def is_ui_element(self, text: str) -> bool:
        """Check if text is a UI element that should be ignored"""
        ui_elements = [
            'menu', 'navegar', 'buscar', 'pesquisar', 'resultados', 'página',
            'anterior', 'próximo', 'mais', 'menos', 'ver', 'clique', 'toque',
            'selecione', 'filtros', 'ordenar', 'compartilhar', 'favoritos',
            'histórico', 'configurações', 'ajuda', 'sobre', 'contato',
            'política', 'termos', 'privacidade', 'cookies', 'anúncio'
        ]
        text_lower = text.lower()
        return any(element in text_lower for element in ui_elements)

    def is_description_improved(self, text: str) -> bool:
        """Improved description detection"""
        # Descriptions are usually longer and contain business-related words
        if len(text) < 10 or len(text) > 200:
            return False
        
        # Skip if it's a UI element
        if self.is_ui_element(text):
            return False
        
        # Check if it contains business-related content
        business_words = [
            'consultório', 'escritório', 'loja', 'supermercado', 'hotel',
            'pousada', 'academia', 'escola', 'universidade', 'banco',
            'seguros', 'imobiliária', 'advocacia', 'contabilidade',
            'serviços', 'atendimento', 'especializado', 'profissional',
            'experiência', 'qualidade', 'confiança', 'tradição'
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in business_words)

    def is_valid_lead_improved(self, lead: Dict) -> bool:
        """Improved lead validation"""
        name = lead.get('name', '').strip()
        
        # Skip leads with generic names
        generic_names = [
            'instalar', 'abrir', 'fechar', 'menu', 'navegar', 'buscar',
            'resultados', 'página', 'anterior', 'próximo', 'mais',
            'menos', 'ver', 'clique', 'toque', 'selecione'
        ]
        
        if any(generic in name.lower() for generic in generic_names):
            return False
        
        # Skip leads that are too short or too long
        if len(name) < 3 or len(name) > 100:
            return False
        
        # Skip leads that are just numbers or symbols
        if re.match(r'^[\d\s\-_\.]+$', name):
            return False
        
        # Must have at least a name and one other piece of information
        return len(lead) >= 2

    async def search_google_maps_with_screenshot(self, keyword: str, region: str) -> List[Dict]:
        """Search Google Maps using screenshot analysis"""
        url = f"https://www.google.com/maps/search/{quote(f'{keyword} {region}')}"
        filename = f"google_maps_{keyword.replace(' ', '_')}_{region.replace(' ', '_')}"
        
        screenshot_path, analysis = await self.take_screenshot_with_analysis(
            url, filename, wait_time=8
        )
        
        leads = analysis.get("leads", [])
        
        # Add source information
        for lead in leads:
            lead.update({
                "source": "google_maps",
                "keyword": keyword,
                "region": region,
                "screenshot": screenshot_path
            })
        
        logger.info(f"Extracted {len(leads)} leads from Google Maps screenshot")
        return leads

    async def search_google_with_screenshot(self, keyword: str, region: str) -> List[Dict]:
        """Search Google using screenshot analysis"""
        url = f"https://www.google.com/search?q={quote(f'{keyword} {region}')}&num=30&hl=pt-BR&gl=br"
        filename = f"google_search_{keyword.replace(' ', '_')}_{region.replace(' ', '_')}"
        
        screenshot_path, analysis = await self.take_screenshot_with_analysis(
            url, filename, wait_time=6
        )
        
        leads = analysis.get("leads", [])
        
        # Add source information
        for lead in leads:
            lead.update({
                "source": "google_search",
                "keyword": keyword,
                "region": region,
                "screenshot": screenshot_path
            })
        
        logger.info(f"Extracted {len(leads)} leads from Google Search screenshot")
        return leads

    async def search_bing_with_screenshot(self, keyword: str, region: str) -> List[Dict]:
        """Search Bing using screenshot analysis"""
        url = f"https://www.bing.com/search?q={quote(f'{keyword} {region}')}&cc=BR&setlang=pt-BR"
        filename = f"bing_search_{keyword.replace(' ', '_')}_{region.replace(' ', '_')}"
        
        screenshot_path, analysis = await self.take_screenshot_with_analysis(
            url, filename, wait_time=5
        )
        
        leads = analysis.get("leads", [])
        
        # Add source information
        for lead in leads:
            lead.update({
                "source": "bing_search",
                "keyword": keyword,
                "region": region,
                "screenshot": screenshot_path
            })
        
        logger.info(f"Extracted {len(leads)} leads from Bing screenshot")
        return leads 