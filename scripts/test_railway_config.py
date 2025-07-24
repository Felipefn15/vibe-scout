#!/usr/bin/env python3
"""
Script para testar a configuração do Railway localmente
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Executa um comando e retorna o resultado"""
    print(f"🔧 {description}")
    print(f"   Comando: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Sucesso")
            if result.stdout.strip():
                print(f"   📋 Saída: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Falhou")
            if result.stderr.strip():
                print(f"   📋 Erro: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        return False

def test_venv_creation():
    """Testa a criação do ambiente virtual"""
    print("\n🧪 Testando Criação do Ambiente Virtual")
    print("=" * 50)
    
    # Limpar venv anterior se existir
    run_command("rm -rf /tmp/test_venv", "Limpando venv anterior")
    
    # Criar novo venv
    success = run_command("python3 -m venv /tmp/test_venv", "Criando ambiente virtual")
    
    if success:
        print("✅ Ambiente virtual criado com sucesso")
        return True
    else:
        print("❌ Falha ao criar ambiente virtual")
        return False

def test_pip_install():
    """Testa a instalação via pip no venv"""
    print("\n📦 Testando Instalação via Pip")
    print("=" * 50)
    
    # Ativar venv e instalar dependências
    commands = [
        ("source /tmp/test_venv/bin/activate && pip install --upgrade pip", "Atualizando pip"),
        ("source /tmp/test_venv/bin/activate && pip install requests", "Instalando requests"),
        ("source /tmp/test_venv/bin/activate && pip install beautifulsoup4", "Instalando beautifulsoup4"),
        ("source /tmp/test_venv/bin/activate && pip install pandas", "Instalando pandas"),
        ("source /tmp/test_venv/bin/activate && pip install playwright", "Instalando playwright"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            all_success = False
    
    return all_success

def test_playwright_install():
    """Testa a instalação do Playwright"""
    print("\n🎭 Testando Instalação do Playwright")
    print("=" * 50)
    
    success = run_command(
        "source /tmp/test_venv/bin/activate && playwright install chromium",
        "Instalando Chromium"
    )
    
    if success:
        print("✅ Playwright instalado com sucesso")
        return True
    else:
        print("❌ Falha ao instalar Playwright")
        return False

def test_imports():
    """Testa os imports das dependências"""
    print("\n📚 Testando Imports")
    print("=" * 50)
    
    imports = [
        "import requests",
        "import bs4",
        "import pandas",
        "import playwright",
    ]
    
    all_success = True
    for imp in imports:
        cmd = f"source /tmp/test_venv/bin/activate && python -c '{imp}; print(\"OK\")'"
        if not run_command(cmd, f"Testando {imp}"):
            all_success = False
    
    return all_success

def cleanup():
    """Limpa o ambiente de teste"""
    print("\n🧹 Limpando Ambiente de Teste")
    print("=" * 50)
    
    run_command("rm -rf /tmp/test_venv", "Removendo venv de teste")

def main():
    """Função principal"""
    print("🧪 Teste da Configuração do Railway")
    print("=" * 60)
    print("Testando localmente a configuração que será usada no Railway")
    print("=" * 60)
    
    try:
        # Testar criação do venv
        if not test_venv_creation():
            print("\n❌ Teste falhou na criação do ambiente virtual")
            return False
        
        # Testar instalação via pip
        if not test_pip_install():
            print("\n❌ Teste falhou na instalação via pip")
            return False
        
        # Testar instalação do Playwright
        if not test_playwright_install():
            print("\n❌ Teste falhou na instalação do Playwright")
            return False
        
        # Testar imports
        if not test_imports():
            print("\n❌ Teste falhou nos imports")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A configuração do Railway deve funcionar")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        return False
    
    finally:
        cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 