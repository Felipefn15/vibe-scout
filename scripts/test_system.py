#!/usr/bin/env python3
"""
Sistema de Teste Completo - Vibe Scout
Testa todas as etapas do sistema de campanhas diárias
"""

import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all modules can be imported"""
    print("🔍 Testando imports...")
    
    try:
        from scraper.collect import LeadCollector
        print("✅ LeadCollector importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar LeadCollector: {e}")
        return False
    
    try:
        from analysis.social import SocialMediaAnalyzer
        print("✅ SocialMediaAnalyzer importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar SocialMediaAnalyzer: {e}")
        return False
    
    try:
        from analysis.site_seo import SiteSEOAnalyzer
        print("✅ SiteSEOAnalyzer importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar SiteSEOAnalyzer: {e}")
        return False
    
    try:
        from llm.generate_email import EmailGenerator
        print("✅ EmailGenerator importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar EmailGenerator: {e}")
        return False
    
    try:
        from email_sender.sendgrid_sender import SendGridSender
        print("✅ SendGridSender importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar SendGridSender: {e}")
        return False
    
    try:
        from utils.rate_limiter import RateLimiter
        print("✅ RateLimiter importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar RateLimiter: {e}")
        return False
    
    return True

def test_config_files():
    """Test if configuration files exist and are valid"""
    print("\n📋 Testando arquivos de configuração...")
    
    config_files = [
        'config/sectors.json',
        'config/lead_filters.json',
        '.env'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file} existe")
            
            # Test JSON files
            if config_file.endswith('.json'):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"✅ {config_file} é JSON válido")
                except Exception as e:
                    print(f"❌ {config_file} não é JSON válido: {e}")
                    return False
        else:
            print(f"❌ {config_file} não encontrado")
            return False
    
    return True

def test_scheduler_import():
    """Test if scheduler can be imported"""
    print("\n⏰ Testando scheduler...")
    
    try:
        from scheduler.daily_campaign import DailyCampaignScheduler
        print("✅ DailyCampaignScheduler importado com sucesso")
        
        # Test initialization
        scheduler = DailyCampaignScheduler()
        print("✅ DailyCampaignScheduler inicializado com sucesso")
        
        # Test sector loading
        sectors = scheduler._load_sectors()
        print(f"✅ {len(sectors)} setores carregados")
        
        # Test region loading
        regions = scheduler._load_regions()
        print(f"✅ {len(regions)} regiões carregadas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no scheduler: {e}")
        return False

def test_lead_collection():
    """Test lead collection with a small sample"""
    print("\n🔍 Testando coleta de leads...")
    
    try:
        from scraper.collect import LeadCollector
        collector = LeadCollector()
        
        # Test with a small sample (test mode)
        leads = collector.collect_leads(
            industry="Advocacia",
            region="Rio de Janeiro",
            test_mode=True,
            target_count=3
        )
        
        if leads:
            print(f"✅ {len(leads)} leads coletados em modo teste")
            for lead in leads[:2]:  # Show first 2 leads
                print(f"   - {lead.get('name', 'N/A')}")
            return True
        else:
            print("⚠️  Nenhum lead coletado (pode ser normal em modo teste)")
            return True
            
    except Exception as e:
        print(f"❌ Erro na coleta de leads: {e}")
        return False

def test_analysis_modules():
    """Test analysis modules"""
    print("\n📊 Testando módulos de análise...")
    
    try:
        from analysis.social import SocialMediaAnalyzer
        from analysis.site_seo import SiteSEOAnalyzer
        
        social_analyzer = SocialMediaAnalyzer()
        site_analyzer = SiteSEOAnalyzer()
        
        # Test social analysis
        social_data = social_analyzer.analyze_social_presence("Test Company")
        print("✅ Análise social funcionando")
        
        # Test site analysis
        site_data = site_analyzer.analyze_website("https://example.com")
        print("✅ Análise de site funcionando")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos módulos de análise: {e}")
        return False

def test_email_generation():
    """Test email generation"""
    print("\n📧 Testando geração de emails...")
    
    try:
        from llm.generate_email import EmailGenerator
        
        email_gen = EmailGenerator()
        
        # Test data
        test_lead = {
            'name': 'Test Company',
            'website': 'https://example.com',
            'email': 'test@example.com'
        }
        
        test_analysis = {
            'lighthouse': {'performance_score': 75.0},
            'seo': {'meta_tags': {'title': True}}
        }
        
        test_social = {
            'overall_social_score': 65.0
        }
        
        # Generate email
        email_data = email_gen.generate_email(test_lead, test_analysis, test_social)
        
        if email_data and email_data.get('body'):
            print("✅ Geração de email funcionando")
            print(f"   Assunto: {email_data.get('subject', 'N/A')}")
            print(f"   Corpo: {len(email_data.get('body', ''))} caracteres")
            return True
        else:
            print("❌ Email não foi gerado corretamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração de email: {e}")
        return False

def test_sendgrid_config():
    """Test SendGrid configuration"""
    print("\n📤 Testando configuração do SendGrid...")
    
    try:
        from email_sender.sendgrid_sender import SendGridSender
        
        sender = SendGridSender()
        
        # Check if API key is configured
        if hasattr(sender, 'api_key') and sender.api_key:
            print("✅ API key do SendGrid configurada")
            return True
        else:
            print("⚠️  API key do SendGrid não configurada (normal para testes)")
            return True
            
    except Exception as e:
        print(f"❌ Erro na configuração do SendGrid: {e}")
        return False

def test_monitoring():
    """Test monitoring system"""
    print("\n📈 Testando sistema de monitoramento...")
    
    try:
        from scripts.monitor_campaigns import get_campaign_status
        
        status = get_campaign_status()
        print("✅ Sistema de monitoramento funcionando")
        print(f"   Status: {status.get('emails_sent', 0)}/{status.get('max_emails', 100)} emails")
        
        return True
    except Exception as e:
        print(f"❌ Erro no sistema de monitoramento: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testando diretórios...")
    
    required_dirs = [
        'logs',
        'data',
        'config',
        'scheduler',
        'scripts'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ existe")
        else:
            print(f"❌ {directory}/ não existe")
            return False
    
    return True

def run_complete_test():
    """Run all tests"""
    print("🚀 Iniciando teste completo do sistema Vibe Scout")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Arquivos de Configuração", test_config_files),
        ("Scheduler", test_scheduler_import),
        ("Coleta de Leads", test_lead_collection),
        ("Módulos de Análise", test_analysis_modules),
        ("Geração de Emails", test_email_generation),
        ("Configuração SendGrid", test_sendgrid_config),
        ("Sistema de Monitoramento", test_monitoring),
        ("Diretórios", test_directories)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema pronto para uso.")
        print("\n💡 Próximos passos:")
        print("   1. Configure o cron job: ./scripts/setup_cron.sh")
        print("   2. Monitore as campanhas: python scripts/monitor_campaigns.py")
        print("   3. Execute manualmente: python scheduler/daily_campaign.py --run-now")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        print("\n🔧 Para resolver problemas:")
        print("   1. Verifique as dependências: pip install -r requirements.txt")
        print("   2. Configure o arquivo .env com suas chaves de API")
        print("   3. Execute os testes individuais para identificar problemas")
    
    return passed == total

if __name__ == "__main__":
    success = run_complete_test()
    sys.exit(0 if success else 1) 