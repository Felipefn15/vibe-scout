#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problemas com APIs
Foca no SendGrid e Groq que são fundamentais para o serviço
"""

import os
import sys
import requests
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_validator import APIKeyValidator
from llm.llm_client import ModularLLMClient
from email_sender.sendgrid_sender import SendGridSender

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIDiagnostic:
    """Diagnóstico completo das APIs"""
    
    def __init__(self):
        self.validator = APIKeyValidator()
        self.results = {}
    
    def run_full_diagnostic(self) -> Dict:
        """Executa diagnóstico completo"""
        print("🔍 DIAGNÓSTICO COMPLETO DAS APIS")
        print("=" * 50)
        
        # 1. Validar formato das chaves
        print("\n1️⃣ VALIDANDO FORMATO DAS CHAVES...")
        format_results = self.validator.validate_all()
        self.results['format_validation'] = format_results
        
        # 2. Testar conexões
        print("\n2️⃣ TESTANDO CONEXÕES...")
        connection_results = self._test_connections()
        self.results['connection_tests'] = connection_results
        
        # 3. Testar funcionalidades específicas
        print("\n3️⃣ TESTANDO FUNCIONALIDADES...")
        functionality_results = self._test_functionality()
        self.results['functionality_tests'] = functionality_results
        
        # 4. Gerar relatório
        print("\n4️⃣ GERANDO RELATÓRIO...")
        self._generate_report()
        
        return self.results
    
    def _test_connections(self) -> Dict:
        """Testa conexões com as APIs"""
        results = {}
        
        # Testar Groq
        print("   🔗 Testando Groq...")
        try:
            client = ModularLLMClient(['Groq'])
            import asyncio
            
            async def test_groq():
                response = await client.generate("Teste de conexão", max_tokens=10)
                return response.success
            
            success = asyncio.run(test_groq())
            results['groq'] = success
            print(f"      {'✅' if success else '❌'} Groq: {'OK' if success else 'FALHOU'}")
        except Exception as e:
            results['groq'] = False
            print(f"      ❌ Groq: ERRO - {e}")
        
        # Testar SendGrid
        print("   🔗 Testando SendGrid...")
        try:
            sender = SendGridSender()
            success = sender.test_connection()
            results['sendgrid'] = success
            print(f"      {'✅' if success else '❌'} SendGrid: {'OK' if success else 'FALHOU'}")
        except Exception as e:
            results['sendgrid'] = False
            print(f"      ❌ SendGrid: ERRO - {e}")
        
        return results
    
    def _test_functionality(self) -> Dict:
        """Testa funcionalidades específicas"""
        results = {}
        
        # Testar geração de email
        print("   📧 Testando geração de email...")
        try:
            from llm.generate_email import EmailGenerator
            
            generator = EmailGenerator(['Groq'])
            test_lead = {
                'name': 'Restaurante Teste',
                'website': 'https://exemplo.com',
                'description': 'Restaurante italiano'
            }
            test_analysis = {
                'seo_score': 45,
                'performance_score': 30,
                'issues': ['Site lento', 'SEO ruim']
            }
            test_social = {
                'instagram_followers': 100,
                'facebook_likes': 50
            }
            
            email_result = generator.generate_personalized_email(test_lead, test_analysis, test_social)
            success = email_result.get('generation_status') == 'success'
            results['email_generation'] = success
            print(f"      {'✅' if success else '❌'} Geração de email: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            results['email_generation'] = False
            print(f"      ❌ Geração de email: ERRO - {e}")
        
        # Testar envio de email (simulado)
        print("   📤 Testando envio de email...")
        try:
            sender = SendGridSender()
            success = sender.send_email(
                to_email='test@example.com',
                subject='Teste Vibe Scout',
                body='Email de teste',
                lead_name='Teste'
            )
            results['email_sending'] = success
            print(f"      {'✅' if success else '❌'} Envio de email: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            results['email_sending'] = False
            print(f"      ❌ Envio de email: ERRO - {e}")
        
        return results
    
    def _generate_report(self):
        """Gera relatório final"""
        print("\n" + "=" * 50)
        print("📊 RELATÓRIO FINAL")
        print("=" * 50)
        
        # Status geral
        format_ok = all(self.results['format_validation'].values())
        connection_ok = all(self.results['connection_tests'].values())
        functionality_ok = all(self.results['functionality_tests'].values())
        
        overall_status = "✅ FUNCIONANDO" if (format_ok and connection_ok and functionality_ok) else "⚠️ PROBLEMAS DETECTADOS"
        
        print(f"\n🎯 STATUS GERAL: {overall_status}")
        
        # Detalhes por serviço
        print("\n📋 DETALHES POR SERVIÇO:")
        
        # Groq
        groq_format = self.results['format_validation'].get('groq', False)
        groq_connection = self.results['connection_tests'].get('groq', False)
        groq_status = "✅ OK" if (groq_format and groq_connection) else "❌ PROBLEMA"
        print(f"   🤖 Groq: {groq_status}")
        
        # SendGrid
        sendgrid_format = self.results['format_validation'].get('sendgrid', False)
        sendgrid_connection = self.results['connection_tests'].get('sendgrid', False)
        sendgrid_status = "✅ OK" if (sendgrid_format and sendgrid_connection) else "❌ PROBLEMA"
        print(f"   📧 SendGrid: {sendgrid_status}")
        
        # Funcionalidades
        print("\n🔧 FUNCIONALIDADES:")
        for func, status in self.results['functionality_tests'].items():
            status_icon = "✅" if status else "❌"
            func_name = func.replace('_', ' ').title()
            print(f"   {status_icon} {func_name}: {'OK' if status else 'FALHOU'}")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        if not groq_format or not groq_connection:
            print("   🔑 Groq: Verificar GROQ_API_KEY no arquivo .env")
        
        if not sendgrid_format or not sendgrid_connection:
            print("   🔑 SendGrid: Verificar SENDGRID_API_KEY no arquivo .env")
            print("   🔄 SendGrid: Considerar gerar nova chave se erro 403 persistir")
        
        if not self.results['format_validation'].get('email_config', False):
            print("   📧 Email: Verificar FROM_EMAIL e FROM_NAME no arquivo .env")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Corrigir problemas identificados acima")
        print("   2. Executar este script novamente para verificar")
        print("   3. Se tudo OK, executar: python main.py")

def main():
    """Função principal"""
    diagnostic = APIDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # Salvar resultados em arquivo
    with open('api_diagnostic_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados salvos em: api_diagnostic_results.json")

if __name__ == "__main__":
    main() 