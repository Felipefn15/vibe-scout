import json
import logging
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from groq import Groq
from utils.rate_limiter import groq_limiter, rate_limited

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailGenerator:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY not found. Using mock email generation.")
            self.client = None
        else:
            self.client = Groq(api_key=self.groq_api_key)
        
        self.model = "llama3-8b-8192"  # Free tier model
    
    def generate_personalized_email(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> Dict:
        """Generate a personalized email based on lead analysis"""
        try:
            logger.info(f"Generating personalized email for: {lead_data['name']}")
            
            if not self.client:
                return self._generate_empty_email(lead_data, analysis_data, social_data)
            
            # Prepare context for the LLM
            context = self._prepare_context(lead_data, analysis_data, social_data)
            
            # Generate email using Groq
            email_content = self._call_groq_api(context)
            
            return {
                'lead_name': lead_data['name'],
                'subject': email_content.get('subject', 'Oportunidade de Melhoria Digital'),
                'body': email_content.get('body', ''),
                'personalization_score': email_content.get('personalization_score', 85),
                'generation_status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error generating email for {lead_data['name']}: {e}")
            return self._generate_empty_email(lead_data, analysis_data, social_data)
    
    def _prepare_context(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> str:
        """Prepare context information for the LLM"""
        
        # Extract business information
        business_name = lead_data.get('name', '')
        website = lead_data.get('website', '')
        description = lead_data.get('description', '')
        
        # Extract performance metrics
        performance_info = ""
        if analysis_data and 'lighthouse' in analysis_data:
            lighthouse = analysis_data['lighthouse']
            performance_info = f"""
            Performance Score: {lighthouse.get('performance_score', 0):.1f}/100
            SEO Score: {lighthouse.get('seo_score', 0):.1f}/100
            Accessibility Score: {lighthouse.get('accessibility_score', 0):.1f}/100
            Best Practices Score: {lighthouse.get('best_practices_score', 0):.1f}/100
            """
        
        # Extract SEO analysis
        seo_info = ""
        if analysis_data and 'seo' in analysis_data:
            seo = analysis_data['seo']
            seo_info = f"""
            SEO Analysis Score: {seo.get('total_score', 0):.1f}/100
            Meta Tags: {'✓' if seo.get('meta_tags', {}).get('title') else '✗'} Title, {'✓' if seo.get('meta_tags', {}).get('description') else '✗'} Description
            Headings: {seo.get('headings', {}).get('total_headings', 0)} total headings
            Images: {seo.get('images', {}).get('alt_text_ratio', 0):.1%} with alt text
            Sitemap: {'✓' if seo.get('sitemap_found') else '✗'} Found
            """
        
        # Extract social media information
        social_info = ""
        if social_data and 'platforms' in social_data:
            platforms = social_data['platforms']
            if 'instagram' in platforms:
                insta = platforms['instagram']
                social_info += f"""
                Instagram: {insta.get('followers', 0)} followers, {insta.get('engagement_rate', 0):.1f}% engagement
                """
            if 'facebook' in platforms:
                fb = platforms['facebook']
                social_info += f"""
                Facebook: {fb.get('followers', 0)} followers, {fb.get('engagement_rate', 0):.1f}% engagement
                """
        
        context = f"""
        Business Information:
        - Name: {business_name}
        - Website: {website}
        - Description: {description}
        
        Performance Analysis:
        {performance_info}
        
        SEO Analysis:
        {seo_info}
        
        Social Media Presence:
        {social_info}
        
        Generate a personalized email in Portuguese that:
        1. Addresses the business owner by name
        2. Mentions specific performance issues found
        3. Highlights opportunities for improvement
        4. Offers digital marketing services
        5. Includes a clear call-to-action
        6. Is professional but friendly
        7. Is under 200 words
        
        Format the response as JSON with:
        - subject: Email subject line
        - body: Email body text
        - personalization_score: Score from 0-100 indicating how personalized the email is
        """
        
        return context
    
    @rate_limited(max_requests=45, time_window=60, retries=3)
    def _call_groq_api(self, context: str) -> Dict:
        """Call Groq API to generate email content with rate limiting"""
        try:
            prompt = f"""
            You are Felipe França, a software developer and full stack specialist from TECHNOLOGIE FELIPE FRANCA, writing personalized outreach emails to business owners.
            
            {context}
            
            Focus on software development services:
            - Web development and optimization
            - Mobile app development
            - System modernization
            - Performance improvements
            - New features and functionality development
            
            Always end your emails with this signature:
            
            Atenciosamente,
            
            Felipe França
            Desenvolvedor Full Stack
            TECHNOLOGIE FELIPE FRANCA
            Transformando Negócios Digitais
            
            Respond only with valid JSON in this exact format:
            {{
                "subject": "Email subject line",
                "body": "Email body text",
                "personalization_score": 85
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional digital marketing consultant. Always respond in Portuguese and provide valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                email_data = json.loads(content)
                return email_data
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, using fallback")
                return self._generate_fallback_email()
                
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return self._generate_fallback_email()
    
    def _generate_fallback_email(self) -> Dict:
        """Generate a fallback email when API fails"""
        return {
            "subject": "Oportunidade de Melhoria Digital para seu Negócio",
            "body": """Olá!

Identificamos que seu site tem potencial para melhorias significativas em performance e funcionalidades. 

Como especialistas em desenvolvimento de software, podemos ajudar você a:
• Melhorar a velocidade e performance do seu site
• Desenvolver novas funcionalidades e recursos
• Criar aplicações mobile para seu negócio
• Otimizar e modernizar seus sistemas

Gostaria de agendar uma conversa gratuita para discutir como podemos impulsionar sua presença digital?

Aguardo seu retorno!

Atenciosamente,

Felipe França
Desenvolvedor Full Stack
TECHNOLOGIE FELIPE FRANCA
Transformando Negócios Digitais""",
            "personalization_score": 60
        }
    
    def _generate_empty_email(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> Dict:
        """Generate empty email when API is not available"""
        
        business_name = lead_data.get('name', 'Empresa')
        
        return {
            'lead_name': business_name,
            'subject': f'Oportunidade de Melhoria Digital para {business_name}',
            'body': f"""Olá {business_name}!

Identificamos que seu site tem potencial para melhorias significativas em performance e funcionalidades. 

Como especialistas em desenvolvimento de software, podemos ajudar você a:
• Melhorar a velocidade e performance do seu site
• Desenvolver novas funcionalidades e recursos
• Criar aplicações mobile para seu negócio
• Otimizar e modernizar seus sistemas

Gostaria de agendar uma conversa gratuita para discutir como podemos impulsionar sua presença digital?

Aguardo seu retorno!

Atenciosamente,

Felipe França
Desenvolvedor Full Stack
TECHNOLOGIE FELIPE FRANCA
Transformando Negócios Digitais""",
            'personalization_score': 60,
            'generation_status': 'no_api'
        }
    
    def _generate_mock_email(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> Dict:
        """Generate mock email for testing when API is not available"""
        
        business_name = lead_data.get('name', 'Empresa')
        
        # Determine issues based on analysis
        issues = []
        if analysis_data and 'lighthouse' in analysis_data:
            perf_score = analysis_data['lighthouse'].get('performance_score', 0)
            if perf_score < 70:
                issues.append("performance lenta")
            if analysis_data['lighthouse'].get('seo_score', 0) < 70:
                issues.append("otimização para SEO")
        
        if social_data and social_data.get('overall_social_score', 0) < 60:
            issues.append("presença nas redes sociais")
        
        issues_text = ", ".join(issues) if issues else "sua presença digital"
        
        return {
            'lead_name': business_name,
            'subject': f'Melhorias Digitais para {business_name}',
            'body': f"""Olá {business_name}!

Analisamos {issues_text} e identificamos oportunidades significativas de melhoria.

Como especialistas em desenvolvimento de software, podemos ajudar você a:
• Otimizar a performance e velocidade do seu site
• Desenvolver novas funcionalidades e recursos
• Criar aplicações mobile para seu negócio
• Modernizar e otimizar seus sistemas

Gostaria de agendar uma conversa gratuita para discutir como podemos impulsionar sua presença digital?

Aguardo seu contato!

Atenciosamente,

Felipe França
Desenvolvedor Full Stack
TECHNOLOGIE FELIPE FRANCA
Transformando Negócios Digitais""",
            'personalization_score': 75,
            'generation_status': 'mock'
        }
    
    def generate_bulk_emails(self, leads_data: List[Dict], test_mode: bool = False) -> List[Dict]:
        """Generate personalized emails for all leads with rate limiting"""
        emails = []
        batch_size = 10  # Process in batches to avoid overwhelming the API
        
        for i, lead in enumerate(leads_data):
            try:
                # Extract analysis data
                analysis_data = lead.get('site_analysis', {})
                social_data = lead.get('social_analysis', {})
                
                # Generate email
                email = self.generate_personalized_email(lead, analysis_data, social_data)
                
                # Add lead information
                email['lead_id'] = lead.get('name', 'Unknown')
                email['website'] = lead.get('website', '')
                email['source'] = lead.get('source', '')
                
                emails.append(email)
                
                logger.info(f"Generated email for {lead['name']} ({i+1}/{len(leads_data)})")
                
                # Add delay between batches to respect rate limits
                if (i + 1) % batch_size == 0 and i < len(leads_data) - 1:
                    groq_limiter.wait_between_batches(batch_size)
                
            except Exception as e:
                logger.error(f"Error generating email for {lead.get('name', 'Unknown')}: {e}")
                # Add error email
                error_email = {
                    'lead_id': lead.get('name', 'Unknown'),
                    'website': lead.get('website', ''),
                    'source': lead.get('source', ''),
                    'subject': 'Erro na Geração de Email',
                    'body': 'Erro técnico na geração do email personalizado.',
                    'personalization_score': 0,
                    'generation_status': 'error',
                    'error_message': str(e)
                }
                emails.append(error_email)
        
        return emails

def generate_emails_for_leads(leads_data: List[Dict]) -> List[Dict]:
    """Main function to generate emails for all leads"""
    generator = EmailGenerator()
    emails = generator.generate_bulk_emails(leads_data)
    
    # Save generated emails
    with open('generated_emails.json', 'w') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
    
    return emails

def main():
    """Main function to be called by CrewAI"""
    # Load leads with social analysis
    try:
        with open('leads_with_social.json', 'r') as f:
            leads = json.load(f)
    except FileNotFoundError:
        logger.error("leads_with_social.json not found. Run the social analysis first.")
        return []
    
    # Generate emails
    emails = generate_emails_for_leads(leads)
    
    logger.info(f"Generated {len(emails)} personalized emails")
    
    return emails

if __name__ == "__main__":
    # Test the email generator
    test_lead = {
        'name': 'Restaurante Teste',
        'website': 'https://exemplo.com',
        'description': 'Restaurante italiano tradicional',
        'analysis': {
            'lighthouse': {
                'performance_score': 65.5,
                'seo_score': 58.2,
                'accessibility_score': 72.1,
                'best_practices_score': 68.9
            },
            'seo': {
                'total_score': 62.5,
                'meta_tags': {'title': True, 'description': False},
                'headings': {'total_headings': 8},
                'images': {'alt_text_ratio': 0.6},
                'sitemap_found': False
            }
        },
        'social_analysis': {
            'overall_social_score': 45.2,
            'platforms': {
                'instagram': {
                    'followers': 1200,
                    'engagement_rate': 2.1
                }
            }
        }
    }
    
    generator = EmailGenerator()
    email = generator.generate_personalized_email(test_lead, test_lead['analysis'], test_lead['social_analysis'])
    
    print(f"Generated email for {email['lead_name']}:")
    print(f"Subject: {email['subject']}")
    print(f"Personalization Score: {email['personalization_score']}")
    print(f"Body: {email['body'][:100]}...") 