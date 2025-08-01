#!/usr/bin/env python3
"""
Enhanced Email Generator with LLM Integration
Advanced email generation with intelligent personalization and optimization
"""

import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from llm.llm_client import ModularLLMClient, LLMResponse

logger = logging.getLogger(__name__)

class EnhancedEmailGenerator:
    """Enhanced email generator with LLM-powered personalization"""
    
    def __init__(self, providers: List[str] = None):
        """
        Initialize enhanced email generator
        
        Args:
            providers: List of LLM providers to use (in order of preference)
        """
        self.llm_client = ModularLLMClient(providers)
        self.default_model = "llama3-8b-8192"
        
        # Email templates and strategies
        self.email_strategies = {
            'high_intelligence': {
                'tone': 'professional_consultative',
                'focus': 'digital_transformation',
                'urgency': 'high',
                'personalization_level': 'maximum'
            },
            'medium_intelligence': {
                'tone': 'friendly_professional',
                'focus': 'improvement_opportunities',
                'urgency': 'medium',
                'personalization_level': 'high'
            },
            'low_intelligence': {
                'tone': 'informative',
                'focus': 'basic_digital_presence',
                'urgency': 'low',
                'personalization_level': 'medium'
            }
        }
        
        # Performance tracking
        self.generation_stats = {
            'total_emails_generated': 0,
            'high_quality_emails': 0,
            'average_personalization_score': 0,
            'generation_time': 0,
            'llm_calls': 0,
            'fallback_emails': 0
        }
        
    async def generate_intelligent_email(self, lead_data: Dict, 
                                       website_analysis: Dict = None,
                                       social_analysis: Dict = None,
                                       ai_analysis: Dict = None) -> Dict:
        """
        Generate intelligent email using LLM with advanced personalization
        
        Args:
            lead_data: Lead information
            website_analysis: Website analysis data
            social_analysis: Social media analysis data
            ai_analysis: AI analysis data
            
        Returns:
            Generated email with metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Generating intelligent email for: {lead_data.get('name', 'Unknown')}")
            
            # Determine email strategy based on intelligence score
            intelligence_score = ai_analysis.get('intelligence_score', 0) if ai_analysis else 50
            strategy = self._determine_email_strategy(intelligence_score)
            
            # Prepare comprehensive context
            context = self._prepare_intelligent_context(lead_data, website_analysis, social_analysis, ai_analysis, strategy)
            
            # Generate email using LLM
            llm_response = await self.llm_client.generate(
                context,
                model=self.default_model,
                max_tokens=600,
                temperature=0.4
            )
            
            self.generation_stats['llm_calls'] += 1
            
            if llm_response.success:
                try:
                    email_content = json.loads(llm_response.content)
                except json.JSONDecodeError:
                    # Fallback to structured generation
                    email_content = self._generate_structured_email(lead_data, website_analysis, social_analysis, ai_analysis, strategy)
                
                # Create email result
                email_result = {
                    'lead_name': lead_data.get('name', ''),
                    'lead_website': lead_data.get('website', ''),
                    'lead_sector': lead_data.get('sector', ''),
                    'subject': email_content.get('subject', 'Oportunidade de Melhoria Digital'),
                    'body': email_content.get('body', ''),
                    'personalization_score': email_content.get('personalization_score', 75),
                    'strategy_used': strategy['tone'],
                    'intelligence_score': intelligence_score,
                    'generation_status': 'success',
                    'llm_provider': llm_response.provider,
                    'llm_model': llm_response.model,
                    'latency': llm_response.latency,
                    'generation_time': time.time() - start_time,
                    'email_metadata': {
                        'focus_area': strategy['focus'],
                        'urgency_level': strategy['urgency'],
                        'personalization_level': strategy['personalization_level'],
                        'pain_points_addressed': email_content.get('pain_points_addressed', []),
                        'opportunities_highlighted': email_content.get('opportunities_highlighted', []),
                        'call_to_action': email_content.get('call_to_action', ''),
                        'value_proposition': email_content.get('value_proposition', '')
                    }
                }
                
                # Update statistics
                self._update_generation_stats(email_result)
                
                return email_result
            else:
                logger.warning(f"LLM generation failed: {llm_response.error_message}")
                return self._generate_fallback_email(lead_data, website_analysis, social_analysis, ai_analysis, strategy)
                
        except Exception as e:
            logger.error(f"Error generating intelligent email: {e}")
            return self._generate_fallback_email(lead_data, website_analysis, social_analysis, ai_analysis, self.email_strategies['medium_intelligence'])
    
    def _determine_email_strategy(self, intelligence_score: int) -> Dict:
        """Determine email strategy based on intelligence score"""
        if intelligence_score >= 80:
            return self.email_strategies['high_intelligence']
        elif intelligence_score >= 60:
            return self.email_strategies['medium_intelligence']
        else:
            return self.email_strategies['low_intelligence']
    
    def _prepare_intelligent_context(self, lead_data: Dict, website_analysis: Dict = None,
                                   social_analysis: Dict = None, ai_analysis: Dict = None,
                                   strategy: Dict = None) -> str:
        """Prepare comprehensive context for intelligent email generation"""
        
        # Basic lead information
        business_name = lead_data.get('name', '')
        website = lead_data.get('website', '')
        sector = lead_data.get('sector', '')
        region = lead_data.get('region', '')
        
        # AI analysis information
        ai_info = ""
        if ai_analysis:
            intelligence_score = ai_analysis.get('intelligence_score', 0)
            digital_maturity = ai_analysis.get('digital_maturity', 'unknown')
            pain_points = ai_analysis.get('pain_points', [])
            opportunities = ai_analysis.get('opportunities', [])
            priority_level = ai_analysis.get('priority_level', 'medium')
            conversion_probability = ai_analysis.get('conversion_probability', 0)
            
            ai_info = f"""
            AI Analysis:
            - Intelligence Score: {intelligence_score}/100
            - Digital Maturity: {digital_maturity}
            - Priority Level: {priority_level}
            - Conversion Probability: {conversion_probability}%
            - Pain Points: {', '.join(pain_points) if pain_points else 'None identified'}
            - Opportunities: {', '.join(opportunities) if opportunities else 'None identified'}
            """
        
        # Website analysis information
        website_info = ""
        if website_analysis:
            tech_stack = website_analysis.get('tech_stack', [])
            it_needs_score = website_analysis.get('it_needs_score', 0)
            digital_maturity = website_analysis.get('digital_maturity', 'low')
            recommendations = website_analysis.get('recommendations', [])
            
            website_info = f"""
            Website Analysis:
            - Tech Stack: {', '.join(tech_stack) if tech_stack else 'Not detected'}
            - IT Needs Score: {it_needs_score}/100
            - Digital Maturity: {digital_maturity}
            - Recommendations: {', '.join(recommendations) if recommendations else 'None'}
            """
        
        # Social media analysis information
        social_info = ""
        if social_analysis:
            platforms = social_analysis.get('platforms', {})
            overall_score = social_analysis.get('overall_social_score', 0)
            digital_maturity_score = social_analysis.get('digital_maturity_score', 0)
            
            social_info = f"""
            Social Media Analysis:
            - Platforms: {', '.join(platforms.keys()) if platforms else 'None detected'}
            - Overall Score: {overall_score}/100
            - Digital Maturity Score: {digital_maturity_score}/100
            """
        
        # Strategy information
        strategy_info = f"""
        Email Strategy:
        - Tone: {strategy.get('tone', 'professional')}
        - Focus: {strategy.get('focus', 'general')}
        - Urgency: {strategy.get('urgency', 'medium')}
        - Personalization Level: {strategy.get('personalization_level', 'medium')}
        """
        
        context = f"""
        Generate a highly personalized email for this business lead:
        
        Business Information:
        - Name: {business_name}
        - Website: {website}
        - Sector: {sector}
        - Region: {region}
        
        {ai_info}
        
        {website_info}
        
        {social_info}
        
        {strategy_info}
        
        Requirements:
        1. Use the specified tone and strategy
        2. Address specific pain points and opportunities identified
        3. Include relevant value propositions based on the business sector
        4. Create a compelling call-to-action
        5. Keep the email under 250 words
        6. Make it highly personalized and relevant
        7. Focus on the identified focus area
        8. Use appropriate urgency level
        
        Format the response as JSON with:
        {{
            "subject": "Compelling subject line",
            "body": "Email body text",
            "personalization_score": <0-100 score>,
            "pain_points_addressed": ["list", "of", "addressed", "pain", "points"],
            "opportunities_highlighted": ["list", "of", "highlighted", "opportunities"],
            "call_to_action": "Specific call to action",
            "value_proposition": "Main value proposition"
        }}
        """
        
        return context
    
    def _generate_structured_email(self, lead_data: Dict, website_analysis: Dict = None,
                                 social_analysis: Dict = None, ai_analysis: Dict = None,
                                 strategy: Dict = None) -> Dict:
        """Generate structured email when LLM fails"""
        
        business_name = lead_data.get('name', '')
        sector = lead_data.get('sector', '')
        
        # Determine focus based on strategy
        focus = strategy.get('focus', 'general') if strategy else 'general'
        
        # Generate subject line
        if focus == 'digital_transformation':
            subject = f"Transformação Digital para {business_name}"
        elif focus == 'improvement_opportunities':
            subject = f"Oportunidades de Melhoria para {business_name}"
        else:
            subject = f"Melhorias Digitais para {business_name}"
        
        # Generate body based on focus and analysis
        body = self._generate_structured_body(lead_data, website_analysis, social_analysis, ai_analysis, strategy)
        
        # Identify pain points and opportunities
        pain_points = []
        opportunities = []
        
        if ai_analysis:
            pain_points = ai_analysis.get('pain_points', [])
            opportunities = ai_analysis.get('opportunities', [])
        
        return {
            "subject": subject,
            "body": body,
            "personalization_score": 75,
            "pain_points_addressed": pain_points[:3],  # Top 3
            "opportunities_highlighted": opportunities[:3],  # Top 3
            "call_to_action": "Gostaria de agendar uma conversa gratuita para discutir como podemos impulsionar sua presença digital?",
            "value_proposition": "Especialistas em desenvolvimento de software e transformação digital"
        }
    
    def _generate_structured_body(self, lead_data: Dict, website_analysis: Dict = None,
                                social_analysis: Dict = None, ai_analysis: Dict = None,
                                strategy: Dict = None) -> str:
        """Generate structured email body"""
        
        business_name = lead_data.get('name', '')
        sector = lead_data.get('sector', '')
        
        # Determine tone
        tone = strategy.get('tone', 'professional') if strategy else 'professional'
        
        # Generate personalized opening
        if tone == 'professional_consultative':
            opening = f"Olá {business_name}!"
        elif tone == 'friendly_professional':
            opening = f"Oi {business_name}!"
        else:
            opening = f"Olá {business_name}!"
        
        # Generate main content based on analysis
        main_content = self._generate_main_content(lead_data, website_analysis, social_analysis, ai_analysis)
        
        # Generate call to action
        cta = self._generate_call_to_action(strategy)
        
        # Generate signature
        signature = """Atenciosamente,

Felipe França
Desenvolvedor Full Stack
TECHNOLOGIE FELIPE FRANCA
Transformando Negócios Digitais"""
        
        return f"{opening}\n\n{main_content}\n\n{cta}\n\n{signature}"
    
    def _generate_main_content(self, lead_data: Dict, website_analysis: Dict = None,
                             social_analysis: Dict = None, ai_analysis: Dict = None) -> str:
        """Generate main email content"""
        
        sector = lead_data.get('sector', '')
        
        # Base content
        content = "Identificamos que seu negócio tem potencial para melhorias significativas em sua presença digital."
        
        # Add sector-specific content
        if 'restaurante' in sector.lower():
            content += " Como especialistas em desenvolvimento de software, podemos ajudar você a:\n• Implementar sistema de delivery online\n• Criar aplicativo para pedidos\n• Otimizar gestão de pedidos e estoque\n• Melhorar a experiência do cliente"
        elif 'varejo' in sector.lower():
            content += " Como especialistas em desenvolvimento de software, podemos ajudar você a:\n• Criar e-commerce profissional\n• Implementar sistema de gestão integrado\n• Otimizar processos de vendas\n• Melhorar a experiência do cliente"
        elif 'saúde' in sector.lower():
            content += " Como especialistas em desenvolvimento de software, podemos ajudar você a:\n• Implementar prontuário eletrônico\n• Criar sistema de agendamento online\n• Otimizar gestão de pacientes\n• Melhorar a eficiência operacional"
        else:
            content += " Como especialistas em desenvolvimento de software, podemos ajudar você a:\n• Melhorar a performance e velocidade do seu site\n• Desenvolver novas funcionalidades e recursos\n• Criar aplicações mobile para seu negócio\n• Otimizar e modernizar seus sistemas"
        
        return content
    
    def _generate_call_to_action(self, strategy: Dict = None) -> str:
        """Generate call to action based on strategy"""
        
        urgency = strategy.get('urgency', 'medium') if strategy else 'medium'
        
        if urgency == 'high':
            return "Gostaria de agendar uma conversa gratuita ainda esta semana para discutir como podemos impulsionar sua presença digital?"
        elif urgency == 'medium':
            return "Gostaria de agendar uma conversa gratuita para discutir como podemos impulsionar sua presença digital?"
        else:
            return "Gostaria de conhecer melhor como podemos ajudar seu negócio a crescer digitalmente?"
    
    def _generate_fallback_email(self, lead_data: Dict, website_analysis: Dict = None,
                               social_analysis: Dict = None, ai_analysis: Dict = None,
                               strategy: Dict = None) -> Dict:
        """Generate fallback email when LLM fails"""
        
        business_name = lead_data.get('name', '')
        
        return {
            'lead_name': business_name,
            'lead_website': lead_data.get('website', ''),
            'lead_sector': lead_data.get('sector', ''),
            'subject': f'Oportunidade de Melhoria Digital para {business_name}',
            'body': f"""Olá {business_name}!

Identificamos que seu negócio tem potencial para melhorias significativas em sua presença digital.

Como especialistas em desenvolvimento de software, podemos ajudar você a:
• Melhorar a performance e velocidade do seu site
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
            'strategy_used': 'fallback',
            'intelligence_score': ai_analysis.get('intelligence_score', 0) if ai_analysis else 0,
            'generation_status': 'fallback',
            'llm_provider': 'fallback',
            'llm_model': 'template',
            'latency': None,
            'generation_time': 0,
            'email_metadata': {
                'focus_area': 'general',
                'urgency_level': 'medium',
                'personalization_level': 'low',
                'pain_points_addressed': [],
                'opportunities_highlighted': [],
                'call_to_action': 'Agendar conversa gratuita',
                'value_proposition': 'Desenvolvimento de software'
            }
        }
    
    def _update_generation_stats(self, email_result: Dict):
        """Update generation statistics"""
        self.generation_stats['total_emails_generated'] += 1
        
        personalization_score = email_result.get('personalization_score', 0)
        if personalization_score >= 80:
            self.generation_stats['high_quality_emails'] += 1
        
        # Update average personalization score
        current_avg = self.generation_stats['average_personalization_score']
        total_emails = self.generation_stats['total_emails_generated']
        self.generation_stats['average_personalization_score'] = (
            (current_avg * (total_emails - 1) + personalization_score) / total_emails
        )
        
        # Update generation time
        self.generation_stats['generation_time'] += email_result.get('generation_time', 0)
    
    async def generate_bulk_intelligent_emails(self, leads_data: List[Dict], 
                                             website_analyses: List[Dict] = None,
                                             social_analyses: List[Dict] = None,
                                             ai_analyses: List[Dict] = None) -> List[Dict]:
        """Generate intelligent emails for multiple leads"""
        
        emails = []
        
        # Ensure we have the same number of analyses as leads
        if website_analyses is None:
            website_analyses = [{}] * len(leads_data)
        if social_analyses is None:
            social_analyses = [{}] * len(leads_data)
        if ai_analyses is None:
            ai_analyses = [{}] * len(leads_data)
        
        for i, lead in enumerate(leads_data):
            try:
                website_analysis = website_analyses[i] if i < len(website_analyses) else {}
                social_analysis = social_analyses[i] if i < len(social_analyses) else {}
                ai_analysis = ai_analyses[i] if i < len(ai_analyses) else {}
                
                email = await self.generate_intelligent_email(lead, website_analysis, social_analysis, ai_analysis)
                emails.append(email)
                
                logger.info(f"Generated email for {lead.get('name', 'Unknown')} ({i+1}/{len(leads_data)})")
                
                # Add delay between generations to respect rate limits
                if i < len(leads_data) - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error generating email for {lead.get('name', 'Unknown')}: {e}")
                # Add fallback email
                fallback_email = self._generate_fallback_email(lead, {}, {}, {})
                emails.append(fallback_email)
                self.generation_stats['fallback_emails'] += 1
        
        return emails
    
    def get_generation_stats(self) -> Dict:
        """Get email generation statistics"""
        return self.generation_stats.copy()
    
    def get_llm_stats(self) -> Dict:
        """Get LLM usage statistics"""
        return self.llm_client.get_stats() 