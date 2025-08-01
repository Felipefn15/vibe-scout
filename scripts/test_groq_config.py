#!/usr/bin/env python3
"""
Teste específico para verificar configuração do Groq
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

async def test_groq_configuration():
    """Testa a configuração do Groq passo a passo"""
    
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO GROQ")
    print("=" * 50)
    
    # 1. Verificar se o arquivo .env está sendo carregado
    print("\n1️⃣ Verificando carregamento do .env...")
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        print(f"✅ Arquivo .env encontrado: {env_file}")
    else:
        print(f"❌ Arquivo .env não encontrado em: {env_file}")
        return False
    
    # 2. Verificar se a variável GROQ_API_KEY está definida
    print("\n2️⃣ Verificando variável GROQ_API_KEY...")
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key:
        print(f"✅ GROQ_API_KEY encontrada: {groq_key[:10]}...{groq_key[-10:]}")
    else:
        print("❌ GROQ_API_KEY não encontrada")
        return False
    
    # 3. Verificar formato da chave
    print("\n3️⃣ Verificando formato da chave...")
    if groq_key.startswith('gsk_'):
        print("✅ Formato da chave parece correto (começa com 'gsk_')")
    else:
        print("⚠️ Formato da chave pode estar incorreto (deveria começar com 'gsk_')")
    
    # 4. Testar importação do cliente LLM
    print("\n4️⃣ Testando importação do cliente LLM...")
    try:
        from llm.llm_client import ModularLLMClient, GroqProvider
        print("✅ Módulos importados com sucesso")
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
        return False
    
    # 5. Testar criação do provider
    print("\n5️⃣ Testando criação do GroqProvider...")
    try:
        provider = GroqProvider()
        print(f"✅ GroqProvider criado com sucesso")
        print(f"   - API Key configurada: {'Sim' if provider.api_key else 'Não'}")
        print(f"   - Modelos disponíveis: {provider.config.models}")
        print(f"   - Rate limit: {provider.config.rate_limit_per_minute}/min")
    except Exception as e:
        print(f"❌ Erro ao criar GroqProvider: {e}")
        return False
    
    # 6. Testar conexão com a API
    print("\n6️⃣ Testando conexão com a API Groq...")
    try:
        client = ModularLLMClient(['Groq'])
        print("✅ ModularLLMClient criado com sucesso")
        
        # Teste simples
        print("   - Enviando teste de conectividade...")
        response = await client.generate("Teste de conectividade", max_tokens=10)
        
        if response.success:
            print(f"✅ Conexão bem-sucedida!")
            print(f"   - Resposta: {response.content}")
            print(f"   - Modelo usado: {response.model}")
            print(f"   - Latência: {response.latency:.2f}s")
            print(f"   - Tokens usados: {response.tokens_used}")
        else:
            print(f"❌ Falha na conexão: {response.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False
    
    # 7. Verificar rate limiting
    print("\n7️⃣ Verificando configuração de rate limiting...")
    groq_rate_limit = os.getenv('GROQ_RATE_LIMIT', '45')
    groq_time_window = os.getenv('GROQ_TIME_WINDOW', '60')
    print(f"   - Rate limit configurado: {groq_rate_limit} requests/{groq_time_window}s")
    
    print("\n✅ CONFIGURAÇÃO DO GROQ VERIFICADA COM SUCESSO!")
    return True

async def test_groq_models():
    """Testa diferentes modelos do Groq"""
    
    print("\n🧪 TESTANDO DIFERENTES MODELOS")
    print("=" * 40)
    
    try:
        from llm.llm_client import ModularLLMClient
        
        client = ModularLLMClient(['Groq'])
        models = ["llama3-8b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"]
        
        for model in models:
            print(f"\n📝 Testando modelo: {model}")
            try:
                response = await client.generate(
                    "Responda apenas 'OK' se estiver funcionando",
                    model=model,
                    max_tokens=5
                )
                
                if response.success:
                    print(f"   ✅ {model}: {response.content.strip()}")
                else:
                    print(f"   ❌ {model}: {response.error_message}")
                    
            except Exception as e:
                print(f"   ❌ {model}: Erro - {e}")
                
    except Exception as e:
        print(f"❌ Erro ao testar modelos: {e}")

async def main():
    """Função principal"""
    print("🚀 INICIANDO TESTE DE CONFIGURAÇÃO DO GROQ")
    print("=" * 60)
    
    # Teste básico de configuração
    success = await test_groq_configuration()
    
    if success:
        # Teste de modelos
        await test_groq_models()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
    else:
        print("\n💥 TESTES FALHARAM - VERIFIQUE A CONFIGURAÇÃO")

if __name__ == "__main__":
    asyncio.run(main()) 