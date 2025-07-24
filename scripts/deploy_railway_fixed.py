#!/usr/bin/env python3
"""
Script de Deploy Corrigido para Railway
Solução para o problema de ambiente gerenciado externamente
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def check_railway_cli():
    """Verifica se o Railway CLI está instalado"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI encontrado")
            return True
        else:
            print("❌ Railway CLI não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI não instalado")
        return False

def check_railway_login():
    """Verifica se está logado no Railway"""
    try:
        result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Logado no Railway como: {result.stdout.strip()}")
            return True
        else:
            print("❌ Não logado no Railway")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar login: {e}")
        return False

def check_env_file():
    """Verifica se o arquivo .env existe e tem as variáveis necessárias"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    required_vars = [
        'RAILWAY_API_KEY',
        'SENDGRID_API_KEY',
        'GROQ_API_KEY'
    ]
    
    missing_vars = []
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis faltando no .env: {', '.join(missing_vars)}")
        return False
    
    print("✅ Arquivo .env configurado")
    return True

def explain_solution():
    """Explica a solução implementada"""
    print("\n🔧 SOLUÇÃO IMPLEMENTADA")
    print("=" * 50)
    print("❌ PROBLEMA: Ambiente Nix gerenciado externamente")
    print("   - Não permite instalação via pip diretamente")
    print("   - Erro: 'externally-managed-environment'")
    print()
    print("✅ SOLUÇÃO: Ambiente Virtual Python")
    print("   - Criamos um venv em /opt/venv")
    print("   - Instalamos todas as dependências no venv")
    print("   - Executamos tudo dentro do venv")
    print()
    print("📋 CONFIGURAÇÃO ATUAL:")
    print("   - nixpacks.toml usa python3Packages.venv")
    print("   - Instala dependências via pip no venv")
    print("   - Playwright instalado no venv")
    print("   - Todas as verificações dentro do venv")
    print("=" * 50)

def create_railway_project():
    """Cria um novo projeto no Railway se não existir"""
    try:
        # Verifica se já existe um projeto
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Projeto Railway já configurado")
            return True
        
        # Cria novo projeto
        print("🚀 Criando novo projeto no Railway...")
        result = subprocess.run(['railway', 'init'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Projeto criado com sucesso")
            return True
        else:
            print(f"❌ Erro ao criar projeto: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar projeto: {e}")
        return False

def deploy_to_railway():
    """Faz o deploy para o Railway"""
    try:
        print("🚀 Iniciando deploy no Railway...")
        print("🔧 Usando solução com ambiente virtual")
        
        # Deploy
        result = subprocess.run(['railway', 'deploy'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Deploy realizado com sucesso!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro no deploy: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante deploy: {e}")
        return False

def get_service_url():
    """Obtém a URL do serviço no Railway"""
    try:
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"🌐 URL do serviço: {url}")
            return url
        else:
            print("❌ Não foi possível obter a URL do serviço")
            return None
    except Exception as e:
        print(f"❌ Erro ao obter URL: {e}")
        return None

def check_logs():
    """Verifica os logs do serviço"""
    try:
        print("📋 Verificando logs do Railway...")
        result = subprocess.run(['railway', 'logs'], capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 Últimos logs:")
            print(result.stdout[-1000:])  # Últimos 1000 caracteres
        else:
            print(f"❌ Erro ao obter logs: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro ao verificar logs: {e}")

def main():
    """Função principal"""
    print("🚀 Deploy Corrigido do Vibe Scout para Railway")
    print("=" * 60)
    print("🔧 Solução para ambiente gerenciado externamente")
    print("=" * 60)
    
    # Explicar a solução
    explain_solution()
    
    # Verificações iniciais
    if not check_railway_cli():
        print("\n📦 Instale o Railway CLI:")
        print("npm install -g @railway/cli")
        return False
    
    if not check_railway_login():
        print("\n🔐 Faça login no Railway:")
        print("railway login")
        return False
    
    if not check_env_file():
        print("\n⚙️ Configure o arquivo .env com as variáveis necessárias")
        return False
    
    # Criar projeto se necessário
    if not create_railway_project():
        return False
    
    # Deploy
    if not deploy_to_railway():
        return False
    
    # Obter URL
    url = get_service_url()
    
    # Verificar logs
    check_logs()
    
    print("\n" + "=" * 60)
    print("🎉 Deploy corrigido concluído!")
    if url:
        print(f"🌐 Acesse: {url}")
    print("\n📊 Para monitorar:")
    print("railway logs")
    print("railway status")
    print("\n💡 Próximos passos:")
    print("1. Verificar se o serviço está rodando")
    print("2. Configurar cron schedule: 0 8 * * *")
    print("3. Monitorar logs para verificar funcionamento")
    print("4. Verificar se as campanhas diárias estão executando")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 