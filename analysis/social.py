import requests
import json
import logging
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.request_delay = int(os.getenv('REQUEST_DELAY', 2))
    
    def analyze_instagram_profile(self, username: str) -> Dict:
        """Analyze Instagram profile for engagement metrics"""
        try:
            logger.info(f"Analyzing Instagram profile: {username}")
            
            # Clean username (remove @ if present)
            username = username.replace('@', '')
            
            # Instagram profile URL
            profile_url = f"https://www.instagram.com/{username}/"
            
            # Note: Instagram has strict anti-scraping measures
            # In production, you would need to use Instagram's API or other methods
            # For demo purposes, we'll return mock data
            
            return self._get_mock_instagram_data(username)
            
        except Exception as e:
            logger.error(f"Error analyzing Instagram profile {username}: {e}")
            return self._get_mock_instagram_data(username)
    
    def _get_mock_instagram_data(self, username: str) -> Dict:
        """Return mock Instagram data for testing"""
        import random
        
        # Generate realistic mock data
        followers = random.randint(500, 50000)
        following = random.randint(50, 2000)
        posts_count = random.randint(10, 500)
        
        # Calculate engagement rate (realistic range: 1-5%)
        engagement_rate = random.uniform(1.0, 5.0)
        
        # Calculate average likes per post
        avg_likes = int(followers * engagement_rate / 100)
        
        # Determine posting frequency
        if posts_count > 100:
            posting_frequency = "High (daily posts)"
        elif posts_count > 50:
            posting_frequency = "Medium (2-3 posts/week)"
        else:
            posting_frequency = "Low (weekly posts)"
        
        return {
            'username': username,
            'followers': followers,
            'following': following,
            'posts_count': posts_count,
            'engagement_rate': round(engagement_rate, 2),
            'avg_likes_per_post': avg_likes,
            'posting_frequency': posting_frequency,
            'profile_quality_score': self._calculate_profile_score(followers, engagement_rate, posts_count),
            'last_post_date': '2024-01-15',  # Mock date
            'bio_length': random.randint(50, 200),
            'has_website_link': random.choice([True, False]),
            'has_business_category': random.choice([True, False])
        }
    
    def _calculate_profile_score(self, followers: int, engagement_rate: float, posts_count: int) -> float:
        """Calculate overall profile quality score"""
        score = 0
        
        # Follower count (40 points)
        if followers >= 10000:
            score += 40
        elif followers >= 5000:
            score += 30
        elif followers >= 1000:
            score += 20
        elif followers >= 500:
            score += 10
        
        # Engagement rate (40 points)
        if engagement_rate >= 4.0:
            score += 40
        elif engagement_rate >= 2.5:
            score += 30
        elif engagement_rate >= 1.5:
            score += 20
        elif engagement_rate >= 1.0:
            score += 10
        
        # Posting consistency (20 points)
        if posts_count >= 100:
            score += 20
        elif posts_count >= 50:
            score += 15
        elif posts_count >= 20:
            score += 10
        elif posts_count >= 10:
            score += 5
        
        return min(score, 100)
    
    def analyze_facebook_page(self, page_name: str) -> Dict:
        """Analyze Facebook page metrics"""
        try:
            logger.info(f"Analyzing Facebook page: {page_name}")
            
            # Facebook page analysis simulation
            # Note: Facebook also has strict API policies
            # In production, you would use Facebook Graph API
            
            return self._get_mock_facebook_data(page_name)
            
        except Exception as e:
            logger.error(f"Error analyzing Facebook page {page_name}: {e}")
            return self._get_mock_facebook_data(page_name)
    
    def _get_mock_facebook_data(self, page_name: str) -> Dict:
        """Return mock Facebook data for testing"""
        import random
        
        followers = random.randint(1000, 100000)
        likes = random.randint(800, int(followers * 0.9))
        posts_count = random.randint(50, 1000)
        
        # Calculate engagement rate
        engagement_rate = random.uniform(0.5, 3.0)
        
        return {
            'page_name': page_name,
            'followers': followers,
            'likes': likes,
            'posts_count': posts_count,
            'engagement_rate': round(engagement_rate, 2),
            'posting_frequency': random.choice(['Daily', '2-3 times/week', 'Weekly']),
            'page_quality_score': self._calculate_facebook_score(followers, engagement_rate, posts_count),
            'has_website': random.choice([True, False]),
            'has_contact_info': random.choice([True, False]),
            'response_rate': random.uniform(50, 95)
        }
    
    def _calculate_facebook_score(self, followers: int, engagement_rate: float, posts_count: int) -> float:
        """Calculate Facebook page quality score"""
        score = 0
        
        # Follower count (35 points)
        if followers >= 50000:
            score += 35
        elif followers >= 20000:
            score += 25
        elif followers >= 10000:
            score += 20
        elif followers >= 5000:
            score += 15
        elif followers >= 1000:
            score += 10
        
        # Engagement rate (35 points)
        if engagement_rate >= 2.5:
            score += 35
        elif engagement_rate >= 1.5:
            score += 25
        elif engagement_rate >= 1.0:
            score += 20
        elif engagement_rate >= 0.5:
            score += 10
        
        # Posting activity (30 points)
        if posts_count >= 500:
            score += 30
        elif posts_count >= 200:
            score += 25
        elif posts_count >= 100:
            score += 20
        elif posts_count >= 50:
            score += 15
        
        return min(score, 100)
    
    def analyze_linkedin_company(self, company_name: str) -> Dict:
        """Analyze LinkedIn company page"""
        try:
            logger.info(f"Analyzing LinkedIn company: {company_name}")
            
            # LinkedIn company analysis simulation
            return self._get_mock_linkedin_data(company_name)
            
        except Exception as e:
            logger.error(f"Error analyzing LinkedIn company {company_name}: {e}")
            return self._get_linkedin_data(company_name)
    
    def _get_mock_linkedin_data(self, company_name: str) -> Dict:
        """Return mock LinkedIn data for testing"""
        import random
        
        followers = random.randint(500, 50000)
        employees = random.randint(10, 1000)
        posts_count = random.randint(20, 500)
        
        return {
            'company_name': company_name,
            'followers': followers,
            'employees': employees,
            'posts_count': posts_count,
            'posting_frequency': random.choice(['Weekly', '2-3 times/week', 'Monthly']),
            'company_size': self._get_company_size(employees),
            'industry': random.choice(['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing']),
            'has_website': random.choice([True, False]),
            'has_job_postings': random.choice([True, False]),
            'profile_completeness': random.uniform(60, 100)
        }
    
    def _get_company_size(self, employees: int) -> str:
        """Determine company size based on employee count"""
        if employees <= 10:
            return "1-10 employees"
        elif employees <= 50:
            return "11-50 employees"
        elif employees <= 200:
            return "51-200 employees"
        elif employees <= 500:
            return "201-500 employees"
        else:
            return "500+ employees"
    
    def analyze_social_presence(self, business_name: str, social_handles: Dict = None) -> Dict:
        """Analyze overall social media presence"""
        try:
            logger.info(f"Analyzing social presence for: {business_name}")
            
            # Default social handles if not provided
            if not social_handles:
                social_handles = {
                    'instagram': f"@{business_name.lower().replace(' ', '')}",
                    'facebook': business_name,
                    'linkedin': business_name
                }
            
            analysis_results = {
                'business_name': business_name,
                'platforms': {}
            }
            
            # Analyze each platform
            if 'instagram' in social_handles:
                analysis_results['platforms']['instagram'] = self.analyze_instagram_profile(
                    social_handles['instagram']
                )
            
            if 'facebook' in social_handles:
                analysis_results['platforms']['facebook'] = self.analyze_facebook_page(
                    social_handles['facebook']
                )
            
            if 'linkedin' in social_handles:
                analysis_results['platforms']['linkedin'] = self.analyze_linkedin_company(
                    social_handles['linkedin']
                )
            
            # Calculate overall social media score
            analysis_results['overall_social_score'] = self._calculate_overall_social_score(
                analysis_results['platforms']
            )
            
            # Determine social media maturity level
            analysis_results['maturity_level'] = self._determine_maturity_level(
                analysis_results['overall_social_score']
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing social presence for {business_name}: {e}")
            return self._get_mock_social_presence(business_name)
    
    def _calculate_overall_social_score(self, platforms: Dict) -> float:
        """Calculate overall social media presence score"""
        if not platforms:
            return 0
        
        total_score = 0
        platform_count = 0
        
        for platform, data in platforms.items():
            if platform == 'instagram' and 'profile_quality_score' in data:
                total_score += data['profile_quality_score']
                platform_count += 1
            elif platform == 'facebook' and 'page_quality_score' in data:
                total_score += data['page_quality_score']
                platform_count += 1
            elif platform == 'linkedin':
                # LinkedIn doesn't have a quality score, use profile completeness
                total_score += data.get('profile_completeness', 50)
                platform_count += 1
        
        return round(total_score / platform_count, 2) if platform_count > 0 else 0
    
    def _determine_maturity_level(self, score: float) -> str:
        """Determine social media maturity level based on score"""
        if score >= 80:
            return "Advanced"
        elif score >= 60:
            return "Intermediate"
        elif score >= 40:
            return "Basic"
        else:
            return "Beginner"
    
    def _get_mock_social_presence(self, business_name: str) -> Dict:
        """Return mock social presence data for testing"""
        return {
            'business_name': business_name,
            'platforms': {
                'instagram': self._get_mock_instagram_data(f"@{business_name.lower().replace(' ', '')}"),
                'facebook': self._get_mock_facebook_data(business_name),
                'linkedin': self._get_mock_linkedin_data(business_name)
            },
            'overall_social_score': 65.5,
            'maturity_level': 'Intermediate'
        }
    
    def analyze_social_media_for_leads(self, leads: List[Dict], test_mode: bool = False) -> List[Dict]:
        """Analyze social media presence for a list of leads"""
        analyzed_leads = []
        
        logger.info(f"Starting social media analysis for {len(leads)} leads")
        
        for lead in leads:
            try:
                business_name = lead.get('name', 'Unknown Business')
                logger.info(f"Analyzing social media for: {business_name}")
                
                # Analyze social media presence
                social_analysis = self.analyze_social_presence(business_name)
                
                # Add social analysis to lead data
                lead['social_analysis'] = social_analysis
                analyzed_leads.append(lead)
                
                if not test_mode:
                    time.sleep(1)  # Be respectful to APIs
                    
            except Exception as e:
                logger.error(f"Error analyzing social media for {lead.get('name', 'Unknown')}: {e}")
                lead['social_analysis'] = None
                analyzed_leads.append(lead)
        
        logger.info(f"Completed social media analysis for {len(analyzed_leads)} leads")
        return analyzed_leads

def analyze_social_media(leads_data: List[Dict]) -> List[Dict]:
    """Main function to analyze social media presence for all leads"""
    analyzer = SocialMediaAnalyzer()
    analyzed_leads = []
    
    for lead in leads_data:
        try:
            logger.info(f"Analyzing social media for: {lead['name']}")
            
            # Extract social handles from lead data
            social_handles = {}
            
            # Check if lead has Instagram data
            if 'instagram_handle' in lead:
                social_handles['instagram'] = lead['instagram_handle']
            
            # Analyze social presence
            social_analysis = analyzer.analyze_social_presence(lead['name'], social_handles)
            
            # Add social analysis to lead data
            lead['social_analysis'] = social_analysis
            analyzed_leads.append(lead)
            
            # Add delay to avoid overwhelming APIs
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error analyzing social media for {lead['name']}: {e}")
            lead['social_analysis'] = None
            analyzed_leads.append(lead)
    
    return analyzed_leads

def main():
    """Main function to be called by CrewAI"""
    # Load analyzed leads data
    try:
        with open('analyzed_leads.json', 'r') as f:
            leads = json.load(f)
    except FileNotFoundError:
        logger.error("analyzed_leads.json not found. Run the site analysis first.")
        return []
    
    # Analyze social media presence
    leads_with_social = analyze_social_media(leads)
    
    # Save results
    with open('leads_with_social.json', 'w') as f:
        json.dump(leads_with_social, f, indent=2)
    
    return leads_with_social

if __name__ == "__main__":
    # Test the social media analyzer
    test_lead = {
        'name': 'Test Restaurant',
        'instagram_handle': '@testrestaurant'
    }
    
    analyzer = SocialMediaAnalyzer()
    results = analyzer.analyze_social_presence('Test Restaurant', {'instagram': '@testrestaurant'})
    
    print(f"Social media analysis for Test Restaurant:")
    print(f"Overall Score: {results['overall_social_score']}")
    print(f"Maturity Level: {results['maturity_level']}")
    print(f"Instagram Followers: {results['platforms']['instagram']['followers']}") 