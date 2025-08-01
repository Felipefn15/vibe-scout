#!/usr/bin/env python3
"""
Intelligent Scraper with LLM Integration
Advanced web scraping system that uses AI to optimize lead collection
"""

import asyncio
import json
import logging
import re
import time
import random
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import quote, urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser

from config.lead_filters import LeadFilter
from utils.lead_scorer import LeadScorer
from llm.llm_client import ModularLLMClient, LLMResponse
from scraper.browser_simulator import BrowserSimulator
from scraper.website_analyzer import WebsiteAnalyzer

logger = logging.getLogger(__name__)

class IntelligentScraper:
    """Intelligent scraper with LLM-powered optimization"""
    
    def __init__(self, llm_providers: List[str] = None):
        """
        Initialize intelligent scraper
        
        Args:
            llm_providers: List of LLM providers to use
        """
        self.llm_client = ModularLLMClient(llm_providers or ['Groq'])
        self.lead_filter = LeadFilter()
        self.lead_scorer = LeadScorer()
        
        # Scraping components
        self.browser_simulator = None
        self.website_analyzer = None
        self.session = None
        
        # Performance tracking
        self.stats = {
            'total_requests': 0,
            'successful_scrapes': 0,
            'llm_analyses': 0,
            'intelligent_decisions': 0,
            'time_saved': 0,
            'quality_improvement': 0
        }
        
        # LLM prompts cache
        self.prompt_cache = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        self.browser_simulator = BrowserSimulator()
        await self.browser_simulator.__aenter__()
        
        self.website_analyzer = WebsiteAnalyzer()
        await self.website_analyzer.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        
        if self.browser_simulator:
            await self.browser_simulator.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.website_analyzer:
            await self.website_analyzer.__aexit__(exc_type, exc_val, exc_tb)
    
    async def intelligent_lead_collection(self, sector: str, region: str, 
                                        max_leads: int = 100,
                                        intelligence_level: str = 'high') -> List[Dict]:
        """
        Perform intelligent lead collection with LLM optimization
        
        Args:
            sector: Business sector to target
            region: Geographic region
            max_leads: Maximum number of leads to collect
            intelligence_level: 'low', 'medium', 'high'
            
        Returns:
            List of intelligent leads with AI insights
        """
        start_time = time.time()
        logger.info(f"Starting intelligent lead collection for {sector} in {region}")
        
        try:
            # 1. Generate intelligent search strategies
            search_strategies = await self._generate_search_strategies(sector, region, intelligence_level)
            
            # 2. Collect leads with intelligent filtering
            raw_leads = await self._collect_with_intelligent_filtering(search_strategies, max_leads)
            
            # 3. Perform intelligent lead analysis
            analyzed_leads = await self._perform_intelligent_analysis(raw_leads, sector)
            
            # 4. Optimize lead quality with AI
            optimized_leads = await self._optimize_lead_quality(analyzed_leads, sector)
            
            # 5. Generate intelligent insights
            final_leads = await self._generate_intelligent_insights(optimized_leads, sector)
            
            # 6. Sort by intelligence score
            final_leads.sort(key=lambda x: x.get('intelligence_score', 0), reverse=True)
            
            # 7. Limit to max_leads
            final_leads = final_leads[:max_leads]
            
            # Update statistics
            self.stats['time_saved'] = time.time() - start_time
            self.stats['successful_scrapes'] = len(final_leads)
            
            logger.info(f"Intelligent collection completed: {len(final_leads)} high-quality leads")
            return final_leads
            
        except Exception as e:
            logger.error(f"Error in intelligent lead collection: {e}")
            return []
    
    async def _generate_search_strategies(self, sector: str, region: str, 
                                        intelligence_level: str) -> List[Dict]:
        """Generate intelligent search strategies using LLM"""
        try:
            prompt = f"""
            Generate intelligent search strategies for finding {sector} businesses in {region}.
            
            Intelligence Level: {intelligence_level}
            
            Consider:
            1. Different search engines and platforms
            2. Various keyword combinations
            3. Business directories and listings
            4. Social media platforms
            5. Industry-specific sources
            
            Return a JSON array with search strategies:
            [
                {{
                    "source": "search_engine_name",
                    "keywords": ["keyword1", "keyword2"],
                    "filters": {{"location": "region", "type": "business"}},
                    "priority": 1-10,
                    "expected_quality": "high/medium/low"
                }}
            ]
            """
            
            response = await self.llm_client.generate(
                prompt,
                max_tokens=600,
                temperature=0.3
            )
            
            if response.success:
                try:
                    strategies = json.loads(response.content)
                    logger.info(f"Generated {len(strategies)} search strategies")
                    return strategies
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM response, using fallback strategies")
            
            # Fallback strategies
            return self._generate_fallback_strategies(sector, region)
            
        except Exception as e:
            logger.error(f"Error generating search strategies: {e}")
            return self._generate_fallback_strategies(sector, region)
    
    async def _collect_with_intelligent_filtering(self, strategies: List[Dict], 
                                                max_leads: int) -> List[Dict]:
        """Collect leads with intelligent filtering"""
        all_leads = []
        
        for strategy in strategies:
            try:
                source = strategy.get('source', '')
                keywords = strategy.get('keywords', [])
                priority = strategy.get('priority', 5)
                
                # Use LLM to decide if we should pursue this strategy
                should_pursue = await self._should_pursue_strategy(strategy, len(all_leads), max_leads)
                
                if should_pursue:
                    logger.info(f"Pursuing strategy: {source} with keywords {keywords}")
                    
                    leads = await self._execute_search_strategy(strategy)
                    
                    # Intelligent filtering of results
                    filtered_leads = await self._intelligent_filter_leads(leads, strategy)
                    
                    all_leads.extend(filtered_leads)
                    
                    # Check if we have enough leads
                    if len(all_leads) >= max_leads * 1.5:  # Collect extra for filtering
                        break
                        
            except Exception as e:
                logger.error(f"Error executing strategy {strategy}: {e}")
                continue
        
        return all_leads
    
    async def _should_pursue_strategy(self, strategy: Dict, current_leads: int, 
                                    max_leads: int) -> bool:
        """Use LLM to decide if we should pursue a search strategy"""
        try:
            prompt = f"""
            Should we pursue this search strategy?
            
            Current leads: {current_leads}
            Target max leads: {max_leads}
            Strategy: {json.dumps(strategy, indent=2)}
            
            Consider:
            1. Expected quality vs effort
            2. Current lead count
            3. Strategy priority
            4. Resource efficiency
            
            Return only: "yes" or "no"
            """
            
            response = await self.llm_client.generate(
                prompt,
                max_tokens=10,
                temperature=0.1
            )
            
            if response.success:
                decision = response.content.strip().lower()
                return decision in ['yes', 'true', '1']
            
            # Fallback decision
            return strategy.get('priority', 5) >= 7 and current_leads < max_leads
            
        except Exception as e:
            logger.error(f"Error in strategy decision: {e}")
            return True  # Default to pursuing
    
    async def _execute_search_strategy(self, strategy: Dict) -> List[Dict]:
        """Execute a specific search strategy"""
        source = strategy.get('source', '')
        keywords = strategy.get('keywords', [])
        
        if 'google' in source.lower():
            return await self._search_google(keywords, strategy.get('filters', {}))
        elif 'bing' in source.lower():
            return await self._search_bing(keywords, strategy.get('filters', {}))
        elif 'maps' in source.lower():
            return await self._search_google_maps(keywords, strategy.get('filters', {}))
        elif 'linkedin' in source.lower():
            return await self._search_linkedin(keywords, strategy.get('filters', {}))
        else:
            return await self._search_generic(keywords, strategy.get('filters', {}))
    
    async def _intelligent_filter_leads(self, leads: List[Dict], strategy: Dict) -> List[Dict]:
        """Intelligently filter leads using LLM"""
        if not leads:
            return []
        
        try:
            # Prepare context for filtering
            context = f"""
            Filter these leads based on the search strategy:
            Strategy: {json.dumps(strategy, indent=2)}
            
            Leads to filter:
            {json.dumps(leads[:10], indent=2)}  # Limit to first 10 for efficiency
            
            Return a JSON array with only the high-quality leads that match the strategy.
            Include only leads that are:
            1. Relevant to the target sector
            2. Have good business potential
            3. Match the expected quality level
            """
            
            response = await self.llm_client.generate(
                context,
                max_tokens=800,
                temperature=0.2
            )
            
            if response.success:
                try:
                    filtered_leads = json.loads(response.content)
                    logger.info(f"LLM filtered {len(leads)} leads to {len(filtered_leads)}")
                    return filtered_leads
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM filtering response")
            
            # Fallback filtering
            return self._fallback_filter_leads(leads, strategy)
            
        except Exception as e:
            logger.error(f"Error in intelligent filtering: {e}")
            return self._fallback_filter_leads(leads, strategy)
    
    async def _perform_intelligent_analysis(self, leads: List[Dict], sector: str) -> List[Dict]:
        """Perform intelligent analysis of leads using LLM"""
        analyzed_leads = []
        
        for lead in leads:
            try:
                # Analyze lead with LLM
                analysis_prompt = f"""
                Analyze this business lead for {sector} sector:
                
                Lead: {json.dumps(lead, indent=2)}
                
                Provide analysis in JSON format:
                {{
                    "intelligence_score": 0-100,
                    "business_potential": "high/medium/low",
                    "digital_maturity": "advanced/intermediate/basic",
                    "pain_points": ["point1", "point2"],
                    "opportunities": ["opp1", "opp2"],
                    "recommended_services": ["service1", "service2"],
                    "conversion_probability": 0-100,
                    "priority_level": "high/medium/low"
                }}
                """
                
                response = await self.llm_client.generate(
                    analysis_prompt,
                    max_tokens=400,
                    temperature=0.3
                )
                
                if response.success:
                    try:
                        analysis = json.loads(response.content)
                        lead.update(analysis)
                        lead['llm_analyzed'] = True
                        self.stats['llm_analyses'] += 1
                    except json.JSONDecodeError:
                        lead['llm_analyzed'] = False
                        logger.warning(f"Failed to parse analysis for {lead.get('name', 'Unknown')}")
                
                analyzed_leads.append(lead)
                
            except Exception as e:
                logger.error(f"Error analyzing lead {lead.get('name', 'Unknown')}: {e}")
                analyzed_leads.append(lead)
        
        return analyzed_leads
    
    async def _optimize_lead_quality(self, leads: List[Dict], sector: str) -> List[Dict]:
        """Optimize lead quality using LLM insights"""
        try:
            # Group leads by quality for optimization
            high_quality = [l for l in leads if l.get('intelligence_score', 0) >= 70]
            medium_quality = [l for l in leads if 40 <= l.get('intelligence_score', 0) < 70]
            low_quality = [l for l in leads if l.get('intelligence_score', 0) < 40]
            
            # Optimize each group
            optimized_high = await self._optimize_high_quality_leads(high_quality, sector)
            optimized_medium = await self._optimize_medium_quality_leads(medium_quality, sector)
            
            # Combine optimized leads
            optimized_leads = optimized_high + optimized_medium
            
            logger.info(f"Optimized {len(leads)} leads to {len(optimized_leads)} high-quality leads")
            return optimized_leads
            
        except Exception as e:
            logger.error(f"Error optimizing lead quality: {e}")
            return leads
    
    async def _generate_intelligent_insights(self, leads: List[Dict], sector: str) -> List[Dict]:
        """Generate intelligent insights for leads"""
        try:
            # Generate sector-specific insights
            insights_prompt = f"""
            Generate intelligent insights for {len(leads)} {sector} business leads.
            
            Lead summary:
            - High potential: {len([l for l in leads if l.get('business_potential') == 'high'])}
            - Medium potential: {len([l for l in leads if l.get('business_potential') == 'medium'])}
            - Average intelligence score: {sum(l.get('intelligence_score', 0) for l in leads) / len(leads) if leads else 0:.1f}
            
            Provide insights in JSON format:
            {{
                "sector_trends": ["trend1", "trend2"],
                "common_pain_points": ["pain1", "pain2"],
                "service_opportunities": ["service1", "service2"],
                "conversion_strategies": ["strategy1", "strategy2"],
                "priority_recommendations": ["rec1", "rec2"]
            }}
            """
            
            response = await self.llm_client.generate(
                insights_prompt,
                max_tokens=500,
                temperature=0.4
            )
            
            if response.success:
                try:
                    insights = json.loads(response.content)
                    
                    # Apply insights to leads
                    for lead in leads:
                        lead['sector_insights'] = insights
                        lead['personalized_approach'] = self._generate_personalized_approach(lead, insights)
                    
                    self.stats['intelligent_decisions'] += 1
                    
                except json.JSONDecodeError:
                    logger.warning("Failed to parse insights response")
            
            return leads
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return leads
    
    # Helper methods for search strategies
    async def _search_google(self, keywords: List[str], filters: Dict) -> List[Dict]:
        """Search Google with intelligent approach"""
        # Implementation would use browser simulator
        return []
    
    async def _search_bing(self, keywords: List[str], filters: Dict) -> List[Dict]:
        """Search Bing with intelligent approach"""
        return []
    
    async def _search_google_maps(self, keywords: List[str], filters: Dict) -> List[Dict]:
        """Search Google Maps with intelligent approach"""
        return []
    
    async def _search_linkedin(self, keywords: List[str], filters: Dict) -> List[Dict]:
        """Search LinkedIn with intelligent approach"""
        return []
    
    async def _search_generic(self, keywords: List[str], filters: Dict) -> List[Dict]:
        """Generic search implementation"""
        return []
    
    def _generate_fallback_strategies(self, sector: str, region: str) -> List[Dict]:
        """Generate fallback search strategies"""
        return [
            {
                "source": "google_search",
                "keywords": [f"{sector} {region}", f"{sector} empresas {region}"],
                "filters": {"location": region},
                "priority": 8,
                "expected_quality": "high"
            },
            {
                "source": "google_maps",
                "keywords": [sector],
                "filters": {"location": region, "type": "business"},
                "priority": 7,
                "expected_quality": "high"
            }
        ]
    
    def _fallback_filter_leads(self, leads: List[Dict], strategy: Dict) -> List[Dict]:
        """Fallback filtering when LLM fails"""
        return [lead for lead in leads if self._basic_quality_check(lead)]
    
    def _basic_quality_check(self, lead: Dict) -> bool:
        """Basic quality check for leads"""
        return (
            lead.get('name') and 
            len(lead.get('name', '')) > 2 and
            lead.get('website') or lead.get('phone') or lead.get('email')
        )
    
    async def _optimize_high_quality_leads(self, leads: List[Dict], sector: str) -> List[Dict]:
        """Optimize high-quality leads"""
        # Add additional enrichment for high-quality leads
        for lead in leads:
            lead['optimization_level'] = 'high'
            lead['enrichment_priority'] = 'immediate'
        return leads
    
    async def _optimize_medium_quality_leads(self, leads: List[Dict], sector: str) -> List[Dict]:
        """Optimize medium-quality leads"""
        # Basic optimization for medium-quality leads
        for lead in leads:
            lead['optimization_level'] = 'medium'
            lead['enrichment_priority'] = 'normal'
        return leads
    
    def _generate_personalized_approach(self, lead: Dict, insights: Dict) -> Dict:
        """Generate personalized approach for a lead"""
        return {
            'opening_line': f"Identificamos oportunidades específicas para {lead.get('name', 'sua empresa')}",
            'key_benefits': insights.get('service_opportunities', [])[:3],
            'urgency_factors': lead.get('pain_points', [])[:2],
            'custom_offer': self._generate_custom_offer(lead, insights)
        }
    
    def _generate_custom_offer(self, lead: Dict, insights: Dict) -> str:
        """Generate custom offer based on lead analysis"""
        digital_maturity = lead.get('digital_maturity', 'basic')
        
        if digital_maturity == 'basic':
            return "Pacote de transformação digital completo"
        elif digital_maturity == 'intermediate':
            return "Otimização e modernização de sistemas"
        else:
            return "Consultoria estratégica e inovação tecnológica"
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return self.stats.copy()
    
    def get_llm_stats(self) -> Dict:
        """Get LLM usage statistics"""
        return self.llm_client.get_stats()

# Convenience function
async def intelligent_scrape_leads(sector: str, region: str, max_leads: int = 100) -> List[Dict]:
    """Convenience function for intelligent lead scraping"""
    async with IntelligentScraper() as scraper:
        return await scraper.intelligent_lead_collection(sector, region, max_leads)

if __name__ == "__main__":
    async def test_intelligent_scraper():
        """Test the intelligent scraper"""
        async with IntelligentScraper() as scraper:
            leads = await scraper.intelligent_lead_collection(
                sector="restaurantes",
                region="Rio de Janeiro",
                max_leads=10,
                intelligence_level="high"
            )
            
            print(f"Collected {len(leads)} intelligent leads")
            for lead in leads[:3]:
                print(f"- {lead.get('name')}: Score {lead.get('intelligence_score', 0)}")
            
            print(f"\nStats: {scraper.get_stats()}")
    
    asyncio.run(test_intelligent_scraper()) 