import json
import subprocess
import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SiteAnalyzer:
    def __init__(self):
        self.lighthouse_timeout = int(os.getenv('LIGHTHOUSE_TIMEOUT', 30000))
        self.seo_threshold = int(os.getenv('SEO_SCORE_THRESHOLD', 70))
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def run_lighthouse(self, url: str) -> Dict:
        """Run Lighthouse analysis on a website"""
        try:
            logger.info(f"Running Lighthouse analysis for: {url}")
            
            # Check if lighthouse is installed
            try:
                subprocess.run(['lighthouse', '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("Lighthouse CLI not found. Using empty data.")
                return self._get_empty_lighthouse_data(url)
            
            # Run Lighthouse in headless mode
            cmd = [
                'lighthouse',
                url,
                '--output=json',
                '--output-path=stdout',
                '--chrome-flags=--headless',
                '--only-categories=performance,accessibility,best-practices,seo',
                f'--timeout={self.lighthouse_timeout}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                lighthouse_data = json.loads(result.stdout)
                return self._parse_lighthouse_results(lighthouse_data)
            else:
                logger.error(f"Lighthouse failed: {result.stderr}")
                return self._get_empty_lighthouse_data(url)
                
        except Exception as e:
            logger.error(f"Error running Lighthouse: {e}")
            return self._get_empty_lighthouse_data(url)
    
    def _parse_lighthouse_results(self, data: Dict) -> Dict:
        """Parse Lighthouse results and extract key metrics"""
        try:
            categories = data.get('categories', {})
            
            return {
                'performance_score': categories.get('performance', {}).get('score', 0) * 100,
                'accessibility_score': categories.get('accessibility', {}).get('score', 0) * 100,
                'best_practices_score': categories.get('best-practices', {}).get('score', 0) * 100,
                'seo_score': categories.get('seo', {}).get('score', 0) * 100,
                'first_contentful_paint': data.get('audits', {}).get('first-contentful-paint', {}).get('numericValue', 0),
                'largest_contentful_paint': data.get('audits', {}).get('largest-contentful-paint', {}).get('numericValue', 0),
                'cumulative_layout_shift': data.get('audits', {}).get('cumulative-layout-shift', {}).get('numericValue', 0),
                'total_blocking_time': data.get('audits', {}).get('total-blocking-time', {}).get('numericValue', 0),
                'speed_index': data.get('audits', {}).get('speed-index', {}).get('numericValue', 0)
            }
        except Exception as e:
            logger.error(f"Error parsing Lighthouse results: {e}")
            return self._get_empty_lighthouse_data("")
    
    def _get_empty_lighthouse_data(self, url: str) -> Dict:
        """Return empty Lighthouse data when CLI is not available"""
        return {
            'performance_score': 0.0,
            'accessibility_score': 0.0,
            'best_practices_score': 0.0,
            'seo_score': 0.0,
            'first_contentful_paint': 0,
            'largest_contentful_paint': 0,
            'cumulative_layout_shift': 0.0,
            'total_blocking_time': 0,
            'speed_index': 0,
            'status': 'no_data'
        }
    
    def _get_mock_lighthouse_data(self, url: str) -> Dict:
        """Return mock Lighthouse data for testing"""
        return {
            'performance_score': 75.5,
            'accessibility_score': 82.3,
            'best_practices_score': 78.9,
            'seo_score': 71.2,
            'first_contentful_paint': 1200,
            'largest_contentful_paint': 2500,
            'cumulative_layout_shift': 0.05,
            'total_blocking_time': 150,
            'speed_index': 1800
        }
    
    def analyze_seo_onpage(self, url: str) -> Dict:
        """Analyze on-page SEO elements"""
        try:
            logger.info(f"Analyzing on-page SEO for: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Analyze meta tags
            meta_analysis = self._analyze_meta_tags(soup)
            
            # Analyze headings
            heading_analysis = self._analyze_headings(soup)
            
            # Analyze images
            image_analysis = self._analyze_images(soup)
            
            # Analyze links
            link_analysis = self._analyze_links(soup)
            
            # Check for sitemap
            sitemap_found = self._check_sitemap(url)
            
            return {
                'meta_tags': meta_analysis,
                'headings': heading_analysis,
                'images': image_analysis,
                'links': link_analysis,
                'sitemap_found': sitemap_found,
                'total_score': self._calculate_seo_score(meta_analysis, heading_analysis, image_analysis, link_analysis, sitemap_found)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing SEO: {e}")
            return self._get_empty_seo_data()
    
    def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict:
        """Analyze meta tags for SEO"""
        meta_tags = soup.find_all('meta')
        
        analysis = {
            'title': False,
            'description': False,
            'keywords': False,
            'viewport': False,
            'robots': False,
            'og_tags': 0,
            'twitter_tags': 0
        }
        
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            property = meta.get('property', '').lower()
            
            if name == 'title' or soup.find('title'):
                analysis['title'] = True
            elif name == 'description':
                analysis['description'] = True
            elif name == 'keywords':
                analysis['keywords'] = True
            elif name == 'viewport':
                analysis['viewport'] = True
            elif name == 'robots':
                analysis['robots'] = True
            elif property.startswith('og:'):
                analysis['og_tags'] += 1
            elif name.startswith('twitter:'):
                analysis['twitter_tags'] += 1
        
        return analysis
    
    def _analyze_headings(self, soup: BeautifulSoup) -> Dict:
        """Analyze heading structure"""
        headings = {
            'h1': len(soup.find_all('h1')),
            'h2': len(soup.find_all('h2')),
            'h3': len(soup.find_all('h3')),
            'h4': len(soup.find_all('h4')),
            'h5': len(soup.find_all('h5')),
            'h6': len(soup.find_all('h6'))
        }
        
        # Check heading hierarchy
        has_proper_hierarchy = (
            headings['h1'] == 1 and  # Should have exactly one H1
            headings['h2'] > 0 and   # Should have H2s
            headings['h3'] > 0       # Should have H3s
        )
        
        return {
            'counts': headings,
            'has_proper_hierarchy': has_proper_hierarchy,
            'total_headings': sum(headings.values())
        }
    
    def _analyze_images(self, soup: BeautifulSoup) -> Dict:
        """Analyze images for alt text"""
        images = soup.find_all('img')
        
        total_images = len(images)
        images_with_alt = len([img for img in images if img.get('alt')])
        images_with_alt_ratio = images_with_alt / total_images if total_images > 0 else 1
        
        return {
            'total_images': total_images,
            'images_with_alt': images_with_alt,
            'alt_text_ratio': images_with_alt_ratio
        }
    
    def _analyze_links(self, soup: BeautifulSoup) -> Dict:
        """Analyze internal and external links"""
        links = soup.find_all('a', href=True)
        
        internal_links = 0
        external_links = 0
        
        for link in links:
            href = link.get('href', '')
            if href.startswith('/') or href.startswith('#'):
                internal_links += 1
            elif href.startswith('http'):
                external_links += 1
        
        return {
            'total_links': len(links),
            'internal_links': internal_links,
            'external_links': external_links
        }
    
    def _check_sitemap(self, url: str) -> bool:
        """Check if sitemap exists"""
        try:
            # Try common sitemap locations
            sitemap_urls = [
                f"{url.rstrip('/')}/sitemap.xml",
                f"{url.rstrip('/')}/sitemap_index.xml",
                f"{url.rstrip('/')}/sitemap1.xml"
            ]
            
            for sitemap_url in sitemap_urls:
                response = self.session.head(sitemap_url, timeout=5)
                if response.status_code == 200:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_seo_score(self, meta: Dict, headings: Dict, images: Dict, links: Dict, sitemap: bool) -> float:
        """Calculate overall SEO score"""
        score = 0
        
        # Meta tags (30 points)
        if meta['title']: score += 10
        if meta['description']: score += 10
        if meta['viewport']: score += 5
        if meta['og_tags'] >= 3: score += 5
        
        # Headings (25 points)
        if headings['has_proper_hierarchy']: score += 15
        if headings['total_headings'] >= 5: score += 10
        
        # Images (20 points)
        if images['alt_text_ratio'] >= 0.8: score += 20
        
        # Links (15 points)
        if links['internal_links'] >= 5: score += 10
        if links['external_links'] >= 2: score += 5
        
        # Sitemap (10 points)
        if sitemap: score += 10
        
        return min(score, 100)
    
    def _get_empty_seo_data(self) -> Dict:
        """Return empty SEO data when analysis fails"""
        return {
            'meta_tags': {
                'title': False,
                'description': False,
                'keywords': False,
                'viewport': False,
                'robots': False,
                'og_tags': 0,
                'twitter_tags': 0
            },
            'headings': {
                'counts': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
                'has_proper_hierarchy': False,
                'total_headings': 0
            },
            'images': {
                'total_images': 0,
                'images_with_alt': 0,
                'alt_text_ratio': 0.0
            },
            'links': {
                'total_links': 0,
                'internal_links': 0,
                'external_links': 0
            },
            'sitemap_found': False,
            'total_score': 0.0,
            'status': 'no_data'
        }
    
    def _get_mock_seo_data(self) -> Dict:
        """Return mock SEO data for testing"""
        return {
            'meta_tags': {
                'title': True,
                'description': True,
                'keywords': False,
                'viewport': True,
                'robots': False,
                'og_tags': 4,
                'twitter_tags': 2
            },
            'headings': {
                'counts': {'h1': 1, 'h2': 3, 'h3': 5, 'h4': 2, 'h5': 0, 'h6': 0},
                'has_proper_hierarchy': True,
                'total_headings': 11
            },
            'images': {
                'total_images': 8,
                'images_with_alt': 7,
                'alt_text_ratio': 0.875
            },
            'links': {
                'total_links': 15,
                'internal_links': 10,
                'external_links': 5
            },
            'sitemap_found': True,
            'total_score': 78.5
        }
    
    def analyze_sites_from_leads(self, leads: List[Dict], test_mode: bool = False) -> List[Dict]:
        """Analyze websites from a list of leads"""
        analyzed_leads = []
        
        logger.info(f"Starting site analysis for {len(leads)} leads")
        
        for lead in leads:
            try:
                website = lead.get('website', '')
                if not website:
                    logger.warning(f"No website found for {lead.get('name', 'Unknown')}")
                    lead['site_analysis'] = None
                    analyzed_leads.append(lead)
                    continue
                
                logger.info(f"Analyzing website: {website}")
                
                # Run Lighthouse analysis
                lighthouse_data = self.run_lighthouse(website)
                
                # Run SEO analysis
                seo_data = self.analyze_seo_onpage(website)
                
                # Combine analysis results
                site_analysis = {
                    'lighthouse': lighthouse_data,
                    'seo': seo_data,
                    'overall_score': (lighthouse_data.get('performance_score', 0) + seo_data.get('total_score', 0)) / 2
                }
                
                lead['site_analysis'] = site_analysis
                analyzed_leads.append(lead)
                
                if not test_mode:
                    time.sleep(1)  # Be respectful to servers
                    
            except Exception as e:
                logger.error(f"Error analyzing {lead.get('name', 'Unknown')}: {e}")
                lead['site_analysis'] = None
                analyzed_leads.append(lead)
        
        logger.info(f"Completed site analysis for {len(analyzed_leads)} leads")
        return analyzed_leads

def analyze_site(url: str) -> Dict:
    """Main function to analyze a website's performance and SEO"""
    analyzer = SiteAnalyzer()
    
    # Run Lighthouse analysis
    lighthouse_results = analyzer.run_lighthouse(url)
    
    # Run SEO analysis
    seo_results = analyzer.analyze_seo_onpage(url)
    
    # Combine results
    analysis_results = {
        'url': url,
        'lighthouse': lighthouse_results,
        'seo': seo_results,
        'overall_score': (lighthouse_results['seo_score'] + seo_results['total_score']) / 2
    }
    
    return analysis_results

def main():
    """Main function to be called by CrewAI"""
    # Load leads data
    try:
        with open('leads_data.json', 'r') as f:
            leads = json.load(f)
    except FileNotFoundError:
        logger.error("leads_data.json not found. Run the scraper first.")
        return []
    
    analyzed_leads = []
    
    for lead in leads:
        if 'website' in lead and lead['website']:
            try:
                logger.info(f"Analyzing website: {lead['website']}")
                analysis = analyze_site(lead['website'])
                lead['analysis'] = analysis
                analyzed_leads.append(lead)
                
                # Add delay to avoid overwhelming servers
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error analyzing {lead['website']}: {e}")
                lead['analysis'] = None
                analyzed_leads.append(lead)
        else:
            lead['analysis'] = None
            analyzed_leads.append(lead)
    
    # Save analyzed data
    with open('analyzed_leads.json', 'w') as f:
        json.dump(analyzed_leads, f, indent=2)
    
    return analyzed_leads

if __name__ == "__main__":
    # Test the analyzer
    test_url = "https://example.com"
    results = analyze_site(test_url)
    print(f"Analysis results for {test_url}:")
    print(f"SEO Score: {results['seo']['total_score']}")
    print(f"Performance Score: {results['lighthouse']['performance_score']}") 