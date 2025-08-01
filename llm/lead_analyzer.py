#!/usr/bin/env python3
"""
Intelligent Lead Analyzer using LLM
Advanced lead analysis and qualification using AI
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from llm.llm_client import ModularLLMClient, LLMResponse

logger = logging.getLogger(__name__)

class IntelligentLeadAnalyzer:
    """Intelligent lead analyzer using LLM for advanced qualification"""
    
    def __init__(self, providers: List[str] = None):
        """
        Initialize intelligent lead analyzer
        
        Args:
            providers: List of LLM providers to use (in order of preference)
        """
        self.llm_client = ModularLLMClient(providers)
        self.default_model = "llama3-8b-8192"
        
    async def analyze_lead_intelligence(self, lead_data: Dict, website_analysis: Dict = None, 
                                      social_analysis: Dict = None) -> Dict:
        """
        Perform intelligent analysis of a lead using LLM
        
        Args:
            lead_data: Basic lead information
            website_analysis: Website analysis data
            social_analysis: Social media analysis data
            
        Returns:
            Enhanced lead data with AI insights
        """
        try:
            logger.info(f"Performing intelligent analysis for: {lead_data.get('name', 'Unknown')}")
            
            # Prepare comprehensive context
            context = self._prepare_analysis_context(lead_data, website_analysis, social_analysis)
            
            # Generate intelligent analysis
            llm_response = await self.llm_client.generate(
                context,
                model=self.default_model,
                max_tokens=800,
                temperature=0.3
            )
            
            if llm_response.success:
                try:
                    analysis_result = json.loads(llm_response.content)
                except json.JSONDecodeError:
                    # Fallback to structured analysis
                    analysis_result = self._generate_structured_analysis(lead_data, website_analysis, social_analysis)
                
                # Enhance lead data with AI insights
                enhanced_lead = lead_data.copy()
                enhanced_lead.update({
                    'ai_analysis': analysis_result,
                    'intelligence_score': analysis_result.get('intelligence_score', 0),
                    'digital_maturity_assessment': analysis_result.get('digital_maturity', 'unknown'),
                    'pain_points_identified': analysis_result.get('pain_points', []),
                    'opportunities_identified': analysis_result.get('opportunities', []),
                    'recommendations': analysis_result.get('recommendations', []),
                    'priority_level': analysis_result.get('priority_level', 'medium'),
                    'conversion_probability': analysis_result.get('conversion_probability', 0),
                    'llm_analysis_provider': llm_response.provider,
                    'llm_analysis_model': llm_response.model
                })
                
                return enhanced_lead
            else:
                logger.warning(f"LLM analysis failed: {llm_response.error_message}")
                return self._generate_fallback_analysis(lead_data, website_analysis, social_analysis)
                
        except Exception as e:
            logger.error(f"Error in intelligent lead analysis: {e}")
            return self._generate_fallback_analysis(lead_data, website_analysis, social_analysis)
    
    def _prepare_analysis_context(self, lead_data: Dict, website_analysis: Dict = None, 
                                social_analysis: Dict = None) -> str:
        """Prepare comprehensive context for LLM analysis"""
        
        # Basic lead information
        business_name = lead_data.get('name', '')
        website = lead_data.get('website', '')
        description = lead_data.get('description', '')
        sector = lead_data.get('sector', '')
        region = lead_data.get('region', '')
        
        # Website analysis information
        website_info = ""
        if website_analysis:
            tech_stack = website_analysis.get('tech_stack', [])
            pain_points = website_analysis.get('pain_points', [])
            opportunities = website_analysis.get('opportunities', [])
            it_needs_score = website_analysis.get('it_needs_score', 0)
            digital_maturity = website_analysis.get('digital_maturity', 'unknown')
            
            website_info = f"""
            Website Analysis:
            - Tech Stack: {', '.join(tech_stack) if tech_stack else 'Not detected'}
            - Pain Points: {', '.join(pain_points) if pain_points else 'None identified'}
            - Opportunities: {', '.join(opportunities) if opportunities else 'None identified'}
            - IT Needs Score: {it_needs_score}/100
            - Digital Maturity: {digital_maturity}
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
            - Overall Social Score: {overall_score}/100
            - Digital Maturity Score: {digital_maturity_score}/100
            """
        
        context = f"""
        Analyze this business lead for IT consulting opportunities:
        
        Business Information:
        - Name: {business_name}
        - Website: {website}
        - Description: {description}
        - Sector: {sector}
        - Region: {region}
        
        {website_info}
        
        {social_info}
        
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "intelligence_score": <0-100 score indicating lead quality>,
            "digital_maturity": "<low|medium|high>",
            "pain_points": ["list", "of", "identified", "pain", "points"],
            "opportunities": ["list", "of", "growth", "opportunities"],
            "recommendations": ["list", "of", "IT", "consulting", "recommendations"],
            "priority_level": "<low|medium|high>",
            "conversion_probability": <0-100 probability of conversion>,
            "business_size_assessment": "<small|medium|large>",
            "budget_potential": "<low|medium|high>",
            "decision_maker_identified": <true|false>,
            "urgency_indicators": ["list", "of", "urgency", "signals"],
            "risk_factors": ["list", "of", "potential", "risks"],
            "competitive_advantages": ["list", "of", "competitive", "advantages"],
            "timeline_assessment": "<immediate|short_term|long_term>",
            "service_recommendations": ["list", "of", "specific", "services", "to", "offer"]
        }}
        
        Focus on identifying businesses that would benefit from:
        - Digital transformation
        - System modernization
        - Process automation
        - Website optimization
        - E-commerce development
        - Mobile app development
        - Cloud migration
        - Data analytics implementation
        - Cybersecurity improvements
        """
        
        return context
    
    def _generate_structured_analysis(self, lead_data: Dict, website_analysis: Dict = None, 
                                    social_analysis: Dict = None) -> Dict:
        """Generate structured analysis when LLM fails"""
        
        # Calculate basic intelligence score
        intelligence_score = self._calculate_basic_intelligence_score(lead_data, website_analysis, social_analysis)
        
        # Determine digital maturity
        digital_maturity = self._assess_digital_maturity(website_analysis, social_analysis)
        
        # Identify pain points
        pain_points = self._identify_pain_points(lead_data, website_analysis, social_analysis)
        
        # Identify opportunities
        opportunities = self._identify_opportunities(lead_data, website_analysis, social_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(lead_data, website_analysis, social_analysis)
        
        # Determine priority level
        priority_level = self._determine_priority_level(intelligence_score, digital_maturity)
        
        # Calculate conversion probability
        conversion_probability = self._calculate_conversion_probability(lead_data, intelligence_score)
        
        return {
            "intelligence_score": intelligence_score,
            "digital_maturity": digital_maturity,
            "pain_points": pain_points,
            "opportunities": opportunities,
            "recommendations": recommendations,
            "priority_level": priority_level,
            "conversion_probability": conversion_probability,
            "business_size_assessment": self._assess_business_size(lead_data),
            "budget_potential": self._assess_budget_potential(lead_data, intelligence_score),
            "decision_maker_identified": self._identify_decision_maker(lead_data),
            "urgency_indicators": self._identify_urgency_indicators(lead_data, website_analysis),
            "risk_factors": self._identify_risk_factors(lead_data),
            "competitive_advantages": self._identify_competitive_advantages(lead_data),
            "timeline_assessment": self._assess_timeline(lead_data, intelligence_score),
            "service_recommendations": self._recommend_services(lead_data, website_analysis, social_analysis)
        }
    
    def _calculate_basic_intelligence_score(self, lead_data: Dict, website_analysis: Dict = None, 
                                          social_analysis: Dict = None) -> int:
        """Calculate basic intelligence score"""
        score = 0
        
        # Base score from lead data
        if lead_data.get('website'):
            score += 20
        
        if lead_data.get('phone'):
            score += 15
        
        if lead_data.get('email'):
            score += 15
        
        # Website analysis contribution
        if website_analysis:
            it_needs_score = website_analysis.get('it_needs_score', 0)
            score += it_needs_score // 2  # Convert to 0-50 scale
            
            digital_maturity = website_analysis.get('digital_maturity', 'low')
            if digital_maturity == 'low':
                score += 20  # High potential
            elif digital_maturity == 'medium':
                score += 10
            else:
                score += 5
        
        # Social analysis contribution
        if social_analysis:
            social_score = social_analysis.get('overall_social_score', 0)
            score += social_score // 2  # Convert to 0-50 scale
        
        return min(score, 100)
    
    def _assess_digital_maturity(self, website_analysis: Dict = None, social_analysis: Dict = None) -> str:
        """Assess digital maturity level"""
        if not website_analysis and not social_analysis:
            return 'unknown'
        
        maturity_indicators = 0
        
        if website_analysis:
            tech_stack = website_analysis.get('tech_stack', [])
            modern_tech_count = len([tech for tech in tech_stack if tech.startswith('modern_')])
            legacy_tech_count = len([tech for tech in tech_stack if tech.startswith('legacy_')])
            
            if modern_tech_count > legacy_tech_count:
                maturity_indicators += 2
            elif modern_tech_count == legacy_tech_count:
                maturity_indicators += 1
            
            digital_maturity = website_analysis.get('digital_maturity', 'low')
            if digital_maturity == 'high':
                maturity_indicators += 2
            elif digital_maturity == 'medium':
                maturity_indicators += 1
        
        if social_analysis:
            social_score = social_analysis.get('overall_social_score', 0)
            if social_score > 70:
                maturity_indicators += 2
            elif social_score > 40:
                maturity_indicators += 1
        
        if maturity_indicators >= 4:
            return 'high'
        elif maturity_indicators >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_pain_points(self, lead_data: Dict, website_analysis: Dict = None, 
                            social_analysis: Dict = None) -> List[str]:
        """Identify pain points"""
        pain_points = []
        
        if website_analysis:
            pain_points.extend(website_analysis.get('pain_points', []))
        
        if social_analysis:
            pain_points.extend(social_analysis.get('pain_points', []))
        
        # Add sector-specific pain points
        sector = lead_data.get('sector', '').lower()
        if 'restaurante' in sector:
            pain_points.extend(['gestão manual de pedidos', 'falta de sistema de delivery'])
        elif 'varejo' in sector:
            pain_points.extend(['gestão manual de estoque', 'falta de e-commerce'])
        elif 'saúde' in sector:
            pain_points.extend(['prontuário em papel', 'falta de agendamento online'])
        
        return list(set(pain_points))  # Remove duplicates
    
    def _identify_opportunities(self, lead_data: Dict, website_analysis: Dict = None, 
                              social_analysis: Dict = None) -> List[str]:
        """Identify growth opportunities"""
        opportunities = []
        
        if website_analysis:
            opportunities.extend(website_analysis.get('opportunities', []))
        
        if social_analysis:
            opportunities.extend(social_analysis.get('opportunities', []))
        
        # Add sector-specific opportunities
        sector = lead_data.get('sector', '').lower()
        if 'restaurante' in sector:
            opportunities.extend(['sistema de delivery online', 'app de pedidos'])
        elif 'varejo' in sector:
            opportunities.extend(['e-commerce', 'sistema de gestão integrado'])
        elif 'saúde' in sector:
            opportunities.extend(['prontuário eletrônico', 'agendamento online'])
        
        return list(set(opportunities))  # Remove duplicates
    
    def _generate_recommendations(self, lead_data: Dict, website_analysis: Dict = None, 
                                social_analysis: Dict = None) -> List[str]:
        """Generate IT consulting recommendations"""
        recommendations = []
        
        if website_analysis:
            recommendations.extend(website_analysis.get('recommendations', []))
        
        # Add general recommendations
        recommendations.extend([
            'Auditoria de sistemas atuais',
            'Planejamento de transformação digital',
            'Desenvolvimento de soluções customizadas'
        ])
        
        return list(set(recommendations))[:5]  # Limit to 5 recommendations
    
    def _determine_priority_level(self, intelligence_score: int, digital_maturity: str) -> str:
        """Determine priority level"""
        if intelligence_score >= 80:
            return 'high'
        elif intelligence_score >= 60:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_conversion_probability(self, lead_data: Dict, intelligence_score: int) -> int:
        """Calculate conversion probability"""
        base_probability = intelligence_score
        
        # Adjust based on contact quality
        if lead_data.get('email') and '@' in lead_data['email']:
            base_probability += 10
        
        if lead_data.get('phone'):
            base_probability += 10
        
        if lead_data.get('website'):
            base_probability += 5
        
        return min(base_probability, 100)
    
    def _assess_business_size(self, lead_data: Dict) -> str:
        """Assess business size"""
        employees = lead_data.get('employees', 0)
        
        if isinstance(employees, int):
            if employees >= 500:
                return 'large'
            elif employees >= 100:
                return 'medium'
            else:
                return 'small'
        
        return 'unknown'
    
    def _assess_budget_potential(self, lead_data: Dict, intelligence_score: int) -> str:
        """Assess budget potential"""
        if intelligence_score >= 80:
            return 'high'
        elif intelligence_score >= 60:
            return 'medium'
        else:
            return 'low'
    
    def _identify_decision_maker(self, lead_data: Dict) -> bool:
        """Identify if decision maker information is available"""
        # This would require more sophisticated analysis
        # For now, return True if we have good contact information
        return bool(lead_data.get('email') or lead_data.get('phone'))
    
    def _identify_urgency_indicators(self, lead_data: Dict, website_analysis: Dict = None) -> List[str]:
        """Identify urgency indicators"""
        indicators = []
        
        if website_analysis:
            pain_points = website_analysis.get('pain_points', [])
            if 'sistema lento' in pain_points or 'sistema antigo' in pain_points:
                indicators.append('Sistema legado crítico')
            
            if 'segurança vulnerável' in pain_points:
                indicators.append('Problemas de segurança')
        
        return indicators
    
    def _identify_risk_factors(self, lead_data: Dict) -> List[str]:
        """Identify risk factors"""
        risks = []
        
        # Check for technology company indicators (competitors)
        name = lead_data.get('name', '').lower()
        description = lead_data.get('description', '').lower()
        
        tech_indicators = ['software', 'desenvolvimento', 'programação', 'tecnologia', 'ti']
        if any(indicator in name or indicator in description for indicator in tech_indicators):
            risks.append('Empresa de tecnologia (competidor)')
        
        return risks
    
    def _identify_competitive_advantages(self, lead_data: Dict) -> List[str]:
        """Identify competitive advantages"""
        advantages = []
        
        # Add sector-specific advantages
        sector = lead_data.get('sector', '').lower()
        if 'restaurante' in sector:
            advantages.append('Especialização em soluções para restaurantes')
        elif 'varejo' in sector:
            advantages.append('Experiência em e-commerce e sistemas de varejo')
        elif 'saúde' in sector:
            advantages.append('Conhecimento em sistemas de saúde')
        
        return advantages
    
    def _assess_timeline(self, lead_data: Dict, intelligence_score: int) -> str:
        """Assess timeline for engagement"""
        if intelligence_score >= 80:
            return 'immediate'
        elif intelligence_score >= 60:
            return 'short_term'
        else:
            return 'long_term'
    
    def _recommend_services(self, lead_data: Dict, website_analysis: Dict = None, 
                          social_analysis: Dict = None) -> List[str]:
        """Recommend specific services"""
        services = []
        
        if website_analysis:
            tech_stack = website_analysis.get('tech_stack', [])
            if any('legacy_' in tech for tech in tech_stack):
                services.append('Migração de sistemas legados')
            
            if website_analysis.get('digital_maturity') == 'low':
                services.append('Desenvolvimento de website moderno')
        
        if social_analysis:
            social_score = social_analysis.get('overall_social_score', 0)
            if social_score < 50:
                services.append('Estratégia de marketing digital')
        
        # Add sector-specific services
        sector = lead_data.get('sector', '').lower()
        if 'restaurante' in sector:
            services.append('Sistema de delivery e pedidos online')
        elif 'varejo' in sector:
            services.append('E-commerce e sistema de gestão')
        elif 'saúde' in sector:
            services.append('Sistema de agendamento e prontuário eletrônico')
        
        return list(set(services))[:5]  # Limit to 5 services
    
    def _generate_fallback_analysis(self, lead_data: Dict, website_analysis: Dict = None, 
                                  social_analysis: Dict = None) -> Dict:
        """Generate fallback analysis when LLM fails"""
        enhanced_lead = lead_data.copy()
        
        # Use structured analysis as fallback
        analysis_result = self._generate_structured_analysis(lead_data, website_analysis, social_analysis)
        
        enhanced_lead.update({
            'ai_analysis': analysis_result,
            'intelligence_score': analysis_result.get('intelligence_score', 0),
            'digital_maturity_assessment': analysis_result.get('digital_maturity', 'unknown'),
            'pain_points_identified': analysis_result.get('pain_points', []),
            'opportunities_identified': analysis_result.get('opportunities', []),
            'recommendations': analysis_result.get('recommendations', []),
            'priority_level': analysis_result.get('priority_level', 'medium'),
            'conversion_probability': analysis_result.get('conversion_probability', 0),
            'llm_analysis_provider': 'fallback',
            'llm_analysis_model': 'structured_analysis'
        })
        
        return enhanced_lead
    
    async def analyze_bulk_leads(self, leads_data: List[Dict], website_analyses: List[Dict] = None, 
                               social_analyses: List[Dict] = None) -> List[Dict]:
        """Analyze multiple leads with intelligent analysis"""
        enhanced_leads = []
        
        # Ensure we have the same number of analyses as leads
        if website_analyses is None:
            website_analyses = [{}] * len(leads_data)
        if social_analyses is None:
            social_analyses = [{}] * len(leads_data)
        
        for i, lead in enumerate(leads_data):
            try:
                website_analysis = website_analyses[i] if i < len(website_analyses) else {}
                social_analysis = social_analyses[i] if i < len(social_analyses) else {}
                
                enhanced_lead = await self.analyze_lead_intelligence(lead, website_analysis, social_analysis)
                enhanced_leads.append(enhanced_lead)
                
                logger.info(f"Analyzed lead {i+1}/{len(leads_data)}: {lead.get('name', 'Unknown')}")
                
                # Add delay between analyses to respect rate limits
                if i < len(leads_data) - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error analyzing lead {lead.get('name', 'Unknown')}: {e}")
                # Add lead with fallback analysis
                fallback_lead = self._generate_fallback_analysis(lead, {}, {})
                enhanced_leads.append(fallback_lead)
        
        return enhanced_leads
    
    def get_analysis_stats(self, enhanced_leads: List[Dict]) -> Dict:
        """Get statistics about lead analysis"""
        if not enhanced_leads:
            return {}
        
        intelligence_scores = [lead.get('intelligence_score', 0) for lead in enhanced_leads]
        priority_levels = [lead.get('priority_level', 'medium') for lead in enhanced_leads]
        conversion_probabilities = [lead.get('conversion_probability', 0) for lead in enhanced_leads]
        
        return {
            'total_leads_analyzed': len(enhanced_leads),
            'average_intelligence_score': sum(intelligence_scores) / len(intelligence_scores),
            'high_priority_count': priority_levels.count('high'),
            'medium_priority_count': priority_levels.count('medium'),
            'low_priority_count': priority_levels.count('low'),
            'average_conversion_probability': sum(conversion_probabilities) / len(conversion_probabilities),
            'high_intelligence_leads': len([s for s in intelligence_scores if s >= 80]),
            'medium_intelligence_leads': len([s for s in intelligence_scores if 60 <= s < 80]),
            'low_intelligence_leads': len([s for s in intelligence_scores if s < 60])
        }
    
    def get_llm_stats(self) -> Dict:
        """Get LLM usage statistics"""
        return self.llm_client.get_stats() 