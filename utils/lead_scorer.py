#!/usr/bin/env python3
"""
Lead Scoring System for Traditional Business Digitalization
Advanced lead scoring for IT consulting targeting traditional businesses
"""

import json
import re
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class LeadScorer:
    """Advanced lead scoring system for traditional business digitalization"""
    
    def __init__(self, config_path: str = "config/sectors.json"):
        """Initialize lead scorer with sector configuration"""
        self.sectors = self._load_sectors(config_path)
        self.digitalization_indicators = self._load_digitalization_indicators()
        self.region_scores = self._load_region_scores()
        
    def _load_sectors(self, config_path: str) -> Dict:
        """Load sector configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                sectors = json.load(f)
            
            # Create lookup dictionary
            sector_lookup = {}
            for sector in sectors:
                sector_lookup[sector['name'].lower()] = {
                    'priority': sector.get('priority', 'low'),
                    'target_score': sector.get('target_score', 30),
                    'keywords': sector.get('keywords', []),
                    'digitalization_opportunities': sector.get('digitalization_opportunities', [])
                }
            
            return sector_lookup
        except Exception as e:
            logger.error(f"Error loading sectors: {e}")
            return {}
    
    def _load_digitalization_indicators(self) -> Dict[str, int]:
        """Load digitalization opportunity indicators with scores"""
        return {
            # High-value digitalization indicators
            'legacy': 30,
            'sistema antigo': 35,
            'planilha excel': 25,
            'processo manual': 30,
            'papel': 20,
            'digitalização': 25,
            'automação': 35,
            'integração': 30,
            'migração': 35,
            'cloud': 30,
            'nuvem': 30,
            'segurança': 25,
            'backup': 20,
            'erp': 35,
            'crm': 30,
            'saas': 35,
            'api': 30,
            'software': 25,
            'desenvolvimento': 30,
            'programação': 25,
            'codificação': 25,
            'banco de dados': 25,
            'database': 25,
            'web': 20,
            'mobile': 25,
            'app': 20,
            'aplicativo': 20,
            'sistema': 25,
            'plataforma': 25,
            'portal': 20,
            'dashboard': 25,
            'relatório': 20,
            'analytics': 30,
            'business intelligence': 35,
            'bi': 30,
            'machine learning': 35,
            'ai': 30,
            'inteligência artificial': 35,
            'blockchain': 30,
            'iot': 30,
            'internet das coisas': 30,
            'cybersecurity': 30,
            'cibersegurança': 30,
            'transformação digital': 40,
            'inovação': 25,
            'startup': 30,
            'scale-up': 35,
            'growth': 25,
            'expansão': 25,
            'novos mercados': 30,
            'investimento': 25,
            
            # Traditional business pain points
            'sistema lento': 30,
            'erro humano': 25,
            'falta de integração': 30,
            'segurança vulnerável': 30,
            'custo alto': 25,
            'escalabilidade limitada': 30,
            'duplicação': 20,
            'inconsistência': 25,
            'falta de automação': 30,
            'processo burocrático': 25,
            'tempo perdido': 20,
            'ineficiência': 25,
            'falta de controle': 25,
            'dados desatualizados': 25,
            'falta de relatórios': 20,
            'difícil acesso': 20,
            'falta de backup': 25,
            'sistema offline': 30,
            'falta de mobile': 25,
            'sem integração': 30,
            
            # Digitalization opportunities
            'e-commerce': 30,
            'marketplace': 30,
            'omnichannel': 35,
            'telemedicina': 35,
            'prontuário eletrônico': 35,
            'agendamento online': 25,
            'pagamento digital': 25,
            'assinatura digital': 25,
            'gestão online': 30,
            'monitoramento remoto': 30,
            'análise preditiva': 35,
            'automação de vendas': 30,
            'gestão de estoque': 30,
            'rastreamento': 25,
            'logística inteligente': 30,
            'gestão de clientes': 30,
            'fidelização': 25,
            'marketing digital': 25,
            'redes sociais': 20,
            'website profissional': 25,
            'presença digital': 25,
            
            # Traditional business indicators (positive for targeting)
            'indústria': 30,
            'manufatura': 35,
            'fábrica': 35,
            'varejo': 30,
            'comércio': 30,
            'hospital': 35,
            'clínica': 30,
            'escola': 30,
            'universidade': 30,
            'banco': 35,
            'advocacia': 30,
            'imobiliária': 25,
            'logística': 30,
            'transporte': 30,
            'restaurante': 25,
            'salão': 20,
            'academia': 20,
            'concessionária': 25,
            'agricultura': 30,
            'fazenda': 30,
            
            # Technology companies (negative for targeting - these are competitors, not clients)
            'software': -20,
            'desenvolvimento': -20,
            'programação': -20,
            'tecnologia': -25,
            'ti': -25,
            'startup tech': -30,
            'fintech': -20,
            'edtech': -20,
            'healthtech': -20,
            'proptech': -20,
            'logtech': -20,
            'agtech': -20,
            'consultoria em ti': -30,
            'empresa de software': -25,
            'desenvolvedor': -20,
            'programador': -20,
            'analista de sistemas': -20,
            'arquiteto de software': -20,
            'engenheiro de software': -20,
            'cientista de dados': -20
        }
    
    def _load_region_scores(self) -> Dict[str, int]:
        """Load region-based scoring"""
        return {
            'são paulo': 25,
            'rio de janeiro': 20,
            'minas gerais': 15,
            'rio grande do sul': 15,
            'paraná': 15,
            'santa catarina': 15,
            'goiás': 10,
            'bahia': 10,
            'pernambuco': 10,
            'ceará': 10,
            'pará': 5,
            'amazonas': 5,
            'brasil': 15
        }
    
    def score_lead(self, lead: Dict) -> int:
        """Score a lead for digitalization potential"""
        score_breakdown = self.calculate_lead_score(lead)
        return score_breakdown['total_score']
    
    def calculate_lead_score(self, lead: Dict) -> Dict:
        """Calculate comprehensive lead score for digitalization potential"""
        
        # Initialize score breakdown
        score_breakdown = {
            'total_score': 0,
            'sector_score': 0,
            'size_score': 0,
            'digital_presence_score': 0,
            'region_score': 0,
            'digitalization_indicators_score': 0,
            'contact_quality_score': 0,
            'website_analysis_score': 0,
            'social_media_score': 0,
            'recommendations': []
        }
        
        try:
            # 1. Sector Score (25% weight)
            sector_score = self._calculate_sector_score(lead)
            score_breakdown['sector_score'] = sector_score
            
            # 2. Company Size Score (15% weight)
            size_score = self._calculate_size_score(lead)
            score_breakdown['size_score'] = size_score
            
            # 3. Digital Presence Score (20% weight)
            digital_presence_score = self._calculate_digital_presence_score(lead)
            score_breakdown['digital_presence_score'] = digital_presence_score
            
            # 4. Region Score (10% weight)
            region_score = self._calculate_region_score(lead)
            score_breakdown['region_score'] = region_score
            
            # 5. Digitalization Indicators Score (20% weight)
            indicators_score = self._calculate_digitalization_indicators_score(lead)
            score_breakdown['digitalization_indicators_score'] = indicators_score
            
            # 6. Contact Quality Score (10% weight)
            contact_score = self._calculate_contact_quality_score(lead)
            score_breakdown['contact_quality_score'] = contact_score
            
            # Calculate weighted total
            total_score = (
                sector_score * 0.25 +
                size_score * 0.15 +
                digital_presence_score * 0.20 +
                region_score * 0.10 +
                indicators_score * 0.20 +
                contact_score * 0.10
            )
            
            score_breakdown['total_score'] = int(total_score)
            
            # Generate recommendations
            score_breakdown['recommendations'] = self._generate_recommendations(score_breakdown, lead)
            
        except Exception as e:
            logger.error(f"Error calculating lead score: {e}")
            score_breakdown['total_score'] = 0
            
        return score_breakdown
    
    def _calculate_sector_score(self, lead: Dict) -> int:
        """Calculate sector-based score"""
        sector = lead.get('sector', '').lower()
        company_name = lead.get('name', '').lower()
        description = lead.get('description', '').lower()
        
        # Check if it's a technology company (negative score)
        tech_indicators = ['software', 'desenvolvimento', 'programação', 'tecnologia', 'ti', 'startup tech']
        if any(indicator in company_name or indicator in description for indicator in tech_indicators):
            return -30  # Negative score for tech companies
        
        # Check sector configuration
        if sector in self.sectors:
            return self.sectors[sector]['target_score']
        
        # Check keywords in company name/description
        for sector_name, sector_data in self.sectors.items():
            for keyword in sector_data['keywords']:
                if keyword.lower() in company_name or keyword.lower() in description:
                    return sector_data['target_score']
        
        return 30  # Default score for unknown sectors
    
    def _calculate_size_score(self, lead: Dict) -> int:
        """Calculate company size score"""
        size = lead.get('size', '').lower()
        employees = lead.get('employees', 0)
        
        if isinstance(employees, int) and employees > 0:
            if employees >= 500:
                return 40  # Large company - high potential
            elif employees >= 100:
                return 35  # Medium-large company
            elif employees >= 50:
                return 30  # Medium company
            elif employees >= 10:
                return 25  # Small-medium company
            else:
                return 20  # Small company
        
        # Fallback to size text
        if any(word in size for word in ['grande', 'large', '500+', '1000+']):
            return 40
        elif any(word in size for word in ['médio', 'medium', '100+', '500']):
            return 30
        elif any(word in size for word in ['pequeno', 'small', '10+', '50']):
            return 20
        else:
            return 25  # Default
    
    def _calculate_digital_presence_score(self, lead: Dict) -> int:
        """Calculate digital presence score"""
        website = lead.get('website', '')
        social_media = lead.get('social_media', {})
        website_analysis = lead.get('website_analysis', {})
        
        score = 0
        
        # Website quality
        if website:
            if self._is_modern_website(website):
                score += 20
            else:
                score += 10
        
        # Social media presence
        if social_media:
            platforms = len(social_media.keys())
            score += min(platforms * 5, 20)
        
        # Website analysis
        if website_analysis:
            tech_stack = website_analysis.get('tech_stack', [])
            it_needs_score = website_analysis.get('it_needs_score', 0)
            digital_maturity = website_analysis.get('digital_maturity', 'low')
            
            # Higher IT needs = higher potential for digitalization
            score += min(it_needs_score // 10, 20)
            
            if digital_maturity == 'low':
                score += 15  # High potential for improvement
            elif digital_maturity == 'medium':
                score += 10
            else:
                score += 5
        
        return min(score, 50)
    
    def _calculate_region_score(self, lead: Dict) -> int:
        """Calculate region-based score"""
        region = lead.get('region', '').lower()
        location = lead.get('location', '').lower()
        
        for region_name, score in self.region_scores.items():
            if region_name in region or region_name in location:
                return score
        
        return 10  # Default score
    
    def _calculate_digitalization_indicators_score(self, lead: Dict) -> int:
        """Calculate score based on digitalization indicators"""
        text_fields = [
            lead.get('name', ''),
            lead.get('description', ''),
            lead.get('website', ''),
            lead.get('notes', '')
        ]
        
        # Add website analysis text
        website_analysis = lead.get('website_analysis', {})
        if website_analysis:
            text_fields.extend([
                ' '.join(website_analysis.get('tech_stack', [])),
                ' '.join(website_analysis.get('pain_points', [])),
                ' '.join(website_analysis.get('opportunities', []))
            ])
        
        # Add social media text
        social_media = lead.get('social_media', {})
        if social_media:
            text_fields.extend([
                ' '.join(social_media.get('it_indicators', [])),
                ' '.join(social_media.get('growth_indicators', []))
            ])
        
        combined_text = ' '.join(text_fields).lower()
        
        score = 0
        for indicator, points in self.digitalization_indicators.items():
            if indicator.lower() in combined_text:
                score += points
        
        return min(score, 50)  # Cap at 50 points
    
    def _calculate_contact_quality_score(self, lead: Dict) -> int:
        """Calculate contact information quality score"""
        score = 0
        
        # Email
        if lead.get('email'):
            email = lead['email']
            if '@' in email and '.' in email:
                if not any(domain in email for domain in ['gmail.com', 'hotmail.com', 'yahoo.com']):
                    score += 15  # Business email
                else:
                    score += 5   # Personal email
        
        # Phone
        if lead.get('phone'):
            phone = str(lead['phone'])
            if len(phone) >= 10:
                score += 10
        
        # Website
        if lead.get('website'):
            score += 10
        
        # Address
        if lead.get('address'):
            score += 5
        
        return min(score, 30)
    
    def _is_modern_website(self, website: str) -> bool:
        """Check if website appears modern"""
        modern_indicators = ['https', 'www', '.com', '.com.br', '.org', '.net']
        return any(indicator in website.lower() for indicator in modern_indicators)
    
    def _classify_lead_quality(self, score: int) -> str:
        """Classify lead quality based on score"""
        if score >= 80:
            return "Alta Qualidade - Prioridade Máxima"
        elif score >= 60:
            return "Média Qualidade - Promissor"
        elif score >= 40:
            return "Baixa Qualidade - Acompanhamento"
        else:
            return "Muito Baixa Qualidade - Não Priorizar"
    
    def _generate_recommendations(self, score_breakdown: Dict, lead: Dict) -> List[str]:
        """Generate digitalization recommendations"""
        recommendations = []
        sector = lead.get('sector', '').lower()
        
        # Sector-specific recommendations
        if sector in self.sectors:
            opportunities = self.sectors[sector].get('digitalization_opportunities', [])
            recommendations.extend(opportunities[:3])  # Top 3 opportunities
        
        # General recommendations based on score
        if score_breakdown['digital_presence_score'] < 20:
            recommendations.append("Desenvolver presença digital profissional")
        
        if score_breakdown['digitalization_indicators_score'] > 30:
            recommendations.append("Implementar automação de processos")
        
        if score_breakdown['contact_quality_score'] < 15:
            recommendations.append("Melhorar informações de contato")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def filter_leads_by_score(self, leads: List[Dict], min_score: int = 60) -> List[Dict]:
        """Filter leads by minimum score"""
        filtered_leads = []
        
        for lead in leads:
            score = self.score_lead(lead)
            if score >= min_score:
                lead['score'] = score
                lead['quality_classification'] = self._classify_lead_quality(score)
                filtered_leads.append(lead)
        
        # Sort by score (highest first)
        filtered_leads.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return filtered_leads
    
    def get_scoring_stats(self, leads: List[Dict]) -> Dict:
        """Get statistics about lead scoring"""
        if not leads:
            return {
                'total_leads': 0,
                'average_score': 0,
                'score_distribution': {},
                'quality_distribution': {}
            }
        
        scores = [lead.get('score', {}).get('total_score', 0) for lead in leads]
        qualities = [lead.get('score', {}).get('quality', 'unknown') for lead in leads]
        
        return {
            'total_leads': len(leads),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'score_distribution': {
                'high': len([s for s in scores if s >= 80]),
                'medium': len([s for s in scores if 60 <= s < 80]),
                'low': len([s for s in scores if s < 60])
            },
            'quality_distribution': {
                'excellent': qualities.count('excellent'),
                'good': qualities.count('good'),
                'fair': qualities.count('fair'),
                'poor': qualities.count('poor')
            }
        }

    async def enrich_lead_data(self, lead: Dict) -> Dict:
        """Enrich lead data with additional information"""
        try:
            enriched_lead = lead.copy()
            
            # Add basic enrichment
            enriched_lead['enriched'] = True
            enriched_lead['enrichment_timestamp'] = asyncio.get_event_loop().time()
            
            # Add sector information if not present
            if 'sector' not in enriched_lead:
                enriched_lead['sector'] = self._infer_sector_from_lead(lead)
            
            # Add size estimation if not present
            if 'size' not in enriched_lead:
                enriched_lead['size'] = self._estimate_company_size(lead)
            
            # Add digital maturity indicators
            enriched_lead['digital_indicators'] = self._extract_digital_indicators(lead)
            
            # Add contact quality assessment
            enriched_lead['contact_quality'] = self._assess_contact_quality(lead)
            
            return enriched_lead
            
        except Exception as e:
            logger.error(f"Error enriching lead data: {e}")
            return lead

    def _infer_sector_from_lead(self, lead: Dict) -> str:
        """Infer sector from lead information"""
        text = f"{lead.get('name', '')} {lead.get('description', '')}".lower()
        
        for sector_name, sector_info in self.sectors.items():
            for keyword in sector_info.get('keywords', []):
                if keyword.lower() in text:
                    return sector_name
        
        return 'unknown'

    def _estimate_company_size(self, lead: Dict) -> str:
        """Estimate company size based on available information"""
        # This is a simple estimation - in a real scenario, you'd use more sophisticated logic
        name = lead.get('name', '').lower()
        description = lead.get('description', '').lower()
        
        # Look for size indicators
        if any(word in name or word in description for word in ['micro', 'pequena', 'small']):
            return 'micro'
        elif any(word in name or word in description for word in ['média', 'medium']):
            return 'medium'
        elif any(word in name or word in description for word in ['grande', 'large', 'corporação']):
            return 'large'
        
        return 'unknown'

    def _extract_digital_indicators(self, lead: Dict) -> List[str]:
        """Extract digital maturity indicators from lead"""
        text = f"{lead.get('name', '')} {lead.get('description', '')}".lower()
        indicators = []
        
        for indicator, score in self.digitalization_indicators.items():
            if indicator.lower() in text:
                indicators.append(indicator)
        
        return indicators

    def _assess_contact_quality(self, lead: Dict) -> str:
        """Assess the quality of contact information"""
        has_website = bool(lead.get('website'))
        has_phone = bool(lead.get('phone'))
        has_email = bool(lead.get('email'))
        
        if has_website and has_phone and has_email:
            return 'excellent'
        elif has_website and (has_phone or has_email):
            return 'good'
        elif has_phone or has_email:
            return 'fair'
        else:
            return 'poor' 