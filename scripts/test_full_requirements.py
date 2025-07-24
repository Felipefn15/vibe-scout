#!/usr/bin/env python3
"""
Script para testar todas as dependências do requirements_railway.txt
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

def test_full_requirements():
    """Testa a instalação completa do requirements_railway.txt"""
    print("\n📦 Testando Instalação Completa do Requirements")
    print("=" * 60)
    
    # Limpar venv anterior se existir
    run_command("rm -rf /tmp/test_venv", "Limpando venv anterior")
    
    # Criar novo venv
    if not run_command("python3 -m venv /tmp/test_venv", "Criando ambiente virtual"):
        return False
    
    # Atualizar pip
    if not run_command("source /tmp/test_venv/bin/activate && pip install --upgrade pip", "Atualizando pip"):
        return False
    
    # Instalar requirements completos
    if not run_command("source /tmp/test_venv/bin/activate && pip install -r requirements_railway.txt", "Instalando requirements completos"):
        return False
    
    # Instalar Playwright
    if not run_command("source /tmp/test_venv/bin/activate && playwright install chromium", "Instalando Chromium"):
        return False
    
    return True

def test_all_imports():
    """Testa todos os imports das dependências"""
    print("\n📚 Testando Todos os Imports")
    print("=" * 60)
    
    imports = [
        "import requests",
        "import bs4",
        "import pandas",
        "import openpyxl",
        "import dotenv",
        "import selenium",
        "import webdriver_manager",
        "import fake_useragent",
        "import playwright",
        "import schedule",
        "import psutil",
        "import groq",
        "import sendgrid",
        "import urllib3",
        "import lxml",
    ]
    
    all_success = True
    for imp in imports:
        cmd = f"source /tmp/test_venv/bin/activate && python -c '{imp}; print(\"OK\")'"
        if not run_command(cmd, f"Testando {imp}"):
            all_success = False
    
    return all_success

def test_playwright_functionality():
    """Testa se o Playwright funciona corretamente"""
    print("\n🎭 Testando Funcionalidade do Playwright")
    print("=" * 60)
    
    test_script = '''
import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        await browser.close()
        print(f"Title: {title}")

asyncio.run(test_playwright())
'''
    
    # Salvar script temporário
    with open("/tmp/test_playwright.py", "w") as f:
        f.write(test_script)
    
    success = run_command(
        "source /tmp/test_venv/bin/activate && python /tmp/test_playwright.py",
        "Testando funcionalidade do Playwright"
    )
    
    # Limpar arquivo temporário
    run_command("rm -f /tmp/test_playwright.py", "Limpando arquivo temporário")
    
    return success

def cleanup():
    """Limpa o ambiente de teste"""
    print("\n🧹 Limpando Ambiente de Teste")
    print("=" * 60)
    
    run_command("rm -rf /tmp/test_venv", "Removendo venv de teste")

def main():
    """Função principal"""
    print("🧪 Teste Completo das Dependências do Railway")
    print("=" * 80)
    print("Testando todas as dependências que serão instaladas no Railway")
    print("=" * 80)
    
    try:
        # Testar instalação completa
        if not test_full_requirements():
            print("\n❌ Teste falhou na instalação das dependências")
            return False
        
        # Testar todos os imports
        if not test_all_imports():
            print("\n❌ Teste falhou nos imports")
            return False
        
        # Testar funcionalidade do Playwright
        if not test_playwright_functionality():
            print("\n❌ Teste falhou na funcionalidade do Playwright")
            return False
        
        print("\n" + "=" * 80)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O Railway deve conseguir instalar e executar todas as dependências")
        print("✅ O Playwright está funcionando corretamente")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        return False
    
    finally:
        cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 