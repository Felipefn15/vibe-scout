import json
import logging
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from llm.llm_client import ModularLLMClient, LLMResponse

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailGenerator:
    def __init__(self, providers: List[str] = None):
        """
        Initialize email generator with modular LLM client
        
        Args:
            providers: List of LLM providers to use (in order of preference)
        """
        self.llm_client = ModularLLMClient(providers)
        self.default_model = "llama3-8b-8192"  # Default model for email generation
    
    def generate_email(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> Dict:
        """Generate a personalized email based on lead analysis (alias for generate_personalized_email)"""
        return self.generate_personalized_email(lead_data, analysis_data, social_data)
    
    async def generate_personalized_email_async(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> Dict:
        """Generate a personalized email using async LLM client"""
        try:
            logger.info(f"Generating personalized email for: {lead_data['name']}")
            
            # Prepare context for the LLM
            context = self._prepare_context(lead_data, analysis_data, social_data)
            
            # Generate email using modular LLM client
            llm_response = await self.llm_client.generate(
                context, 
                model=self.default_model,
                max_tokens=500,
                temperature=0.7
            )
            
            if llm_response.success:
                # Try to parse JSON response
                try:
                    email_content = json.loads(llm_response.content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, use the raw content as body
                    email_content = {
                        'subject': 'Oportunidade de Melhoria Digital',
                        'body': llm_response.content,
                        'personalization_score': 75
                    }
                
                return {
                    'lead_name': lead_data['name'],
                    'subject': email_content.get('subject', 'Oportunidade de Melhoria Digital'),
                    'body': email_content.get('body', ''),
                    'personalization_score': email_content.get('personalization_score', 85),
                    'generation_status': 'success',
                    'llm_provider': llm_response.provider,
                    'llm_model': llm_response.model,
                    'latency': llm_response.latency
                }
            else:
                logger.warning(f"LLM generation failed: {llm_response.error_message}")
                return self._generate_fallback_email(lead_data, analysis_data, social_data)
            
        except Exception as e:
            logger.error(f"Error generating email for {lead_data['name']}: {e}")
            return self._generate_fallback_email(lead_data, analysis_data, social_data)
    
    def generate_personalized_email(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> Dict:
        """Generate a personalized email based on lead analysis (synchronous wrapper)"""
        import asyncio
        
        # Run async method in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.generate_personalized_email_async(lead_data, analysis_data, social_data)
        )
    
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
    
    def _generate_fallback_email(self, lead_data: Dict, analysis_data: Dict, social_data: Dict) -> Dict:
        """Generate a fallback email when LLM fails"""
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
            'generation_status': 'fallback',
            'llm_provider': 'fallback',
            'llm_model': 'template',
            'latency': None
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
            'generation_status': 'no_api',
            'llm_provider': 'none',
            'llm_model': 'none',
            'latency': None
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
            'generation_status': 'mock',
            'llm_provider': 'mock',
            'llm_model': 'mock-model',
            'latency': None
        }
    
    async def generate_bulk_emails_async(self, leads_data: List[Dict], test_mode: bool = False) -> List[Dict]:
        """Generate personalized emails for all leads with async processing"""
        emails = []
        batch_size = 10  # Process in batches to avoid overwhelming the API
        
        for i, lead in enumerate(leads_data):
            try:
                # Extract analysis data
                analysis_data = lead.get('site_analysis', {})
                social_data = lead.get('social_analysis', {})
                
                # Generate email
                email = await self.generate_personalized_email_async(lead, analysis_data, social_data)
                
                # Add lead information
                email['lead_id'] = lead.get('name', 'Unknown')
                email['website'] = lead.get('website', '')
                email['source'] = lead.get('source', '')
                
                emails.append(email)
                
                logger.info(f"Generated email for {lead['name']} ({i+1}/{len(leads_data)}) using {email.get('llm_provider', 'unknown')}")
                
                # Add delay between batches to respect rate limits
                if (i + 1) % batch_size == 0 and i < len(leads_data) - 1:
                    await asyncio.sleep(2)  # 2 second delay between batches
                
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
                    'error_message': str(e),
                    'llm_provider': 'error',
                    'llm_model': 'error',
                    'latency': None
                }
                emails.append(error_email)
        
        return emails
    
    def generate_bulk_emails(self, leads_data: List[Dict], test_mode: bool = False) -> List[Dict]:
        """Generate personalized emails for all leads (synchronous wrapper)"""
        import asyncio
        
        # Run async method in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.generate_bulk_emails_async(leads_data, test_mode)
        )
    
    def get_llm_stats(self) -> Dict:
        """Get LLM usage statistics"""
        return self.llm_client.get_stats()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return self.llm_client.get_available_providers()

def generate_emails_for_leads(leads_data: List[Dict]) -> List[Dict]:
    """Main function to generate emails for all leads"""
    generator = EmailGenerator()
    emails = generator.generate_bulk_emails(leads_data)
    
    # Save generated emails
    with open('generated_emails.json', 'w') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
    
    # Save LLM statistics
    stats = generator.get_llm_stats()
    with open('llm_stats.json', 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
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
    print(f"LLM Provider: {email.get('llm_provider', 'unknown')}")
    print(f"LLM Model: {email.get('llm_model', 'unknown')}")
    print(f"Body: {email['body'][:100]}...")
    
    # Print LLM statistics
    print("\nLLM Statistics:")
    stats = generator.get_llm_stats()
    print(json.dumps(stats, indent=2)) 