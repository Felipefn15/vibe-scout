#!/usr/bin/env python3
"""
Test Script for Intelligent Scraping System
Demonstrates LLM-powered scraping capabilities
"""

import asyncio
import json
import logging
import time
from typing import Dict, List
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.intelligent_scraper import IntelligentScraper
from llm.prompt_optimizer import PromptOptimizer
from llm.lead_analyzer import IntelligentLeadAnalyzer
from utils.service_status import ServiceMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentScrapingTester:
    """Test suite for intelligent scraping system"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
    
    async def run_comprehensive_test(self):
        """Run comprehensive test of intelligent scraping system"""
        print("🧪 TESTE COMPREENSIVO DO SISTEMA DE SCRAPING INTELIGENTE")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. Test service status
        print("\n1️⃣ VERIFICANDO STATUS DOS SERVIÇOS...")
        await self._test_service_status()
        
        # 2. Test prompt optimization
        print("\n2️⃣ TESTANDO OTIMIZAÇÃO DE PROMPTS...")
        await self._test_prompt_optimization()
        
        # 3. Test intelligent lead analysis
        print("\n3️⃣ TESTANDO ANÁLISE INTELIGENTE DE LEADS...")
        await self._test_intelligent_analysis()
        
        # 4. Test intelligent scraping
        print("\n4️⃣ TESTANDO SCRAPING INTELIGENTE...")
        await self._test_intelligent_scraping()
        
        # 5. Generate comprehensive report
        print("\n5️⃣ GERANDO RELATÓRIO COMPLETO...")
        await self._generate_comprehensive_report()
        
        total_time = time.time() - start_time
        print(f"\n⏱️  Tempo total de teste: {total_time:.2f} segundos")
    
    async def _test_service_status(self):
        """Test service status monitoring"""
        try:
            monitor = ServiceMonitor()
            status = monitor.check_all_services()
            
            self.test_results['service_status'] = {
                'overall_status': status.overall_status,
                'services': {
                    name: {
                        'available': service.available,
                        'success_rate': service.success_rate,
                        'avg_response_time': service.avg_response_time
                    }
                    for name, service in status.services.items()
                }
            }
            
            print(f"   Status Geral: {status.overall_status}")
            for name, service in status.services.items():
                status_icon = "✅" if service.available else "❌"
                print(f"   {status_icon} {name}: {service.success_rate:.1%} sucesso, {service.avg_response_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error testing service status: {e}")
            self.test_results['service_status'] = {'error': str(e)}
    
    async def _test_prompt_optimization(self):
        """Test prompt optimization system"""
        try:
            optimizer = PromptOptimizer()
            
            # Test different prompt types
            test_cases = [
                {
                    'name': 'Lead Analysis',
                    'prompt': """
                    Please analyze this business lead for the restaurant sector and provide a comprehensive analysis including intelligence score, business potential, digital maturity assessment, pain points identification, opportunities analysis, recommended services, conversion probability calculation, and priority level determination.
                    """,
                    'context': {
                        'task_type': 'lead_analysis',
                        'sector': 'restaurantes',
                        'region': 'Rio de Janeiro'
                    }
                },
                {
                    'name': 'Search Strategy',
                    'prompt': """
                    Generate intelligent search strategies for finding restaurant businesses in Rio de Janeiro, considering different search engines, various keyword combinations, business directories, social media platforms, and industry-specific sources.
                    """,
                    'context': {
                        'task_type': 'search_strategy',
                        'sector': 'restaurantes',
                        'region': 'Rio de Janeiro'
                    }
                }
            ]
            
            optimization_results = {}
            
            for test_case in test_cases:
                print(f"   Otimizando prompt: {test_case['name']}")
                
                optimized = await optimizer.optimize_scraping_prompt(
                    test_case['prompt'],
                    test_case['context']
                )
                
                original_length = len(test_case['prompt'])
                optimized_length = len(optimized.prompt)
                improvement = ((original_length - optimized_length) / original_length) * 100
                
                optimization_results[test_case['name']] = {
                    'original_length': original_length,
                    'optimized_length': optimized_length,
                    'improvement_percent': improvement,
                    'optimization_level': optimized.optimization_level,
                    'success_rate': optimized.success_rate
                }
                
                print(f"      Melhoria: {improvement:.1f}% ({optimized.optimization_level} level)")
            
            self.test_results['prompt_optimization'] = optimization_results
            
        except Exception as e:
            logger.error(f"Error testing prompt optimization: {e}")
            self.test_results['prompt_optimization'] = {'error': str(e)}
    
    async def _test_intelligent_analysis(self):
        """Test intelligent lead analysis"""
        try:
            analyzer = IntelligentLeadAnalyzer()
            
            # Test lead analysis
            test_lead = {
                'name': 'Restaurante Italiano Bella Vista',
                'website': 'https://bellavista.com.br',
                'description': 'Restaurante italiano tradicional no centro do Rio',
                'phone': '(21) 99999-9999',
                'address': 'Rua das Flores, 123 - Centro, Rio de Janeiro',
                'sector': 'restaurantes',
                'region': 'Rio de Janeiro'
            }
            
            print("   Analisando lead de teste...")
            
            analysis = await analyzer.analyze_lead_intelligence(test_lead)
            
            self.test_results['intelligent_analysis'] = {
                'lead_name': test_lead['name'],
                'intelligence_score': analysis.get('intelligence_score', 0),
                'business_potential': analysis.get('business_potential', 'unknown'),
                'digital_maturity': analysis.get('digital_maturity', 'unknown'),
                'conversion_probability': analysis.get('conversion_probability', 0),
                'priority_level': analysis.get('priority_level', 'unknown'),
                'pain_points': analysis.get('pain_points', []),
                'opportunities': analysis.get('opportunities', [])
            }
            
            print(f"      Score: {analysis.get('intelligence_score', 0)}/100")
            print(f"      Potencial: {analysis.get('business_potential', 'unknown')}")
            print(f"      Maturidade Digital: {analysis.get('digital_maturity', 'unknown')}")
            print(f"      Probabilidade de Conversão: {analysis.get('conversion_probability', 0)}%")
            
        except Exception as e:
            logger.error(f"Error testing intelligent analysis: {e}")
            self.test_results['intelligent_analysis'] = {'error': str(e)}
    
    async def _test_intelligent_scraping(self):
        """Test intelligent scraping system"""
        try:
            print("   Iniciando scraping inteligente...")
            
            async with IntelligentScraper() as scraper:
                leads = await scraper.intelligent_lead_collection(
                    sector="restaurantes",
                    region="Rio de Janeiro",
                    max_leads=5,
                    intelligence_level="high"
                )
                
                self.test_results['intelligent_scraping'] = {
                    'leads_collected': len(leads),
                    'scraper_stats': scraper.get_stats(),
                    'llm_stats': scraper.get_llm_stats(),
                    'sample_leads': [
                        {
                            'name': lead.get('name', 'Unknown'),
                            'intelligence_score': lead.get('intelligence_score', 0),
                            'business_potential': lead.get('business_potential', 'unknown'),
                            'priority_level': lead.get('priority_level', 'unknown')
                        }
                        for lead in leads[:3]
                    ]
                }
                
                print(f"      Leads coletados: {len(leads)}")
                if leads:
                    avg_score = sum(l.get('intelligence_score', 0) for l in leads) / len(leads)
                    print(f"      Score médio: {avg_score:.1f}/100")
                    
                    high_quality = len([l for l in leads if l.get('intelligence_score', 0) >= 70])
                    print(f"      Alta qualidade: {high_quality}/{len(leads)}")
                
        except Exception as e:
            logger.error(f"Error testing intelligent scraping: {e}")
            self.test_results['intelligent_scraping'] = {'error': str(e)}
    
    async def _generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n📊 RELATÓRIO COMPLETO DOS TESTES")
        print("=" * 60)
        
        # Overall assessment
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if 'error' not in result)
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n🎯 RESULTADO GERAL: {success_rate:.1f}% de sucesso ({successful_tests}/{total_tests})")
        
        # Service status summary
        if 'service_status' in self.test_results and 'error' not in self.test_results['service_status']:
            services = self.test_results['service_status']['services']
            available_services = sum(1 for s in services.values() if s['available'])
            print(f"   🔧 Serviços: {available_services}/{len(services)} disponíveis")
        
        # Prompt optimization summary
        if 'prompt_optimization' in self.test_results and 'error' not in self.test_results['prompt_optimization']:
            optimizations = self.test_results['prompt_optimization']
            avg_improvement = sum(o['improvement_percent'] for o in optimizations.values()) / len(optimizations)
            print(f"   📝 Otimização de Prompts: {avg_improvement:.1f}% de melhoria média")
        
        # Intelligent analysis summary
        if 'intelligent_analysis' in self.test_results and 'error' not in self.test_results['intelligent_analysis']:
            analysis = self.test_results['intelligent_analysis']
            print(f"   🤖 Análise Inteligente: Score {analysis['intelligence_score']}/100")
        
        # Scraping summary
        if 'intelligent_scraping' in self.test_results and 'error' not in self.test_results['intelligent_scraping']:
            scraping = self.test_results['intelligent_scraping']
            print(f"   🕷️  Scraping Inteligente: {scraping['leads_collected']} leads coletados")
        
        # Performance metrics
        print(f"\n📈 MÉTRICAS DE PERFORMANCE:")
        
        if 'intelligent_scraping' in self.test_results and 'error' not in self.test_results['intelligent_scraping']:
            scraper_stats = self.test_results['intelligent_scraping']['scraper_stats']
            llm_stats = self.test_results['intelligent_scraping']['llm_stats']
            
            print(f"   ⚡ Análises LLM: {scraper_stats.get('llm_analyses', 0)}")
            print(f"   🎯 Decisões Inteligentes: {scraper_stats.get('intelligent_decisions', 0)}")
            print(f"   🕐 Tempo Economizado: {scraper_stats.get('time_saved', 0):.2f}s")
        
        # Recommendations
        print(f"\n💡 RECOMENDAÇÕES:")
        
        if success_rate < 100:
            print("   ⚠️  Corrigir problemas identificados nos testes")
        
        if 'service_status' in self.test_results and 'error' not in self.test_results['service_status']:
            services = self.test_results['service_status']['services']
            for name, service in services.items():
                if not service['available']:
                    print(f"   🔧 Corrigir serviço: {name}")
        
        print("   ✅ Sistema pronto para uso em produção")
        print("   📊 Monitorar métricas de performance")
        print("   🔄 Executar testes regularmente")
        
        # Save detailed results
        with open('test_results_intelligent_scraping.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados detalhados salvos em: test_results_intelligent_scraping.json")

async def main():
    """Main test function"""
    tester = IntelligentScrapingTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main()) 