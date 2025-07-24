#!/usr/bin/env python3
"""
Script para testar todas as dependências do projeto
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Testa se um módulo pode ser importado"""
    try:
        if package_name:
            module = importlib.import_module(package_name)
        else:
            module = importlib.import_module(module_name)
        print(f"✅ {module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - FAILED: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - WARNING: {e}")
        return True

def main():
    """Testa todas as dependências"""
    print("🧪 Testando Dependências do Vibe Scout")
    print("=" * 50)
    
    # Lista de dependências para testar
    dependencies = [
        # Core dependencies
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("python-dotenv", "dotenv"),
        
        # Web automation
        ("selenium", "selenium"),
        ("webdriver-manager", "webdriver_manager"),
        ("fake-useragent", "fake_useragent"),
        ("playwright", "playwright"),
        
        # Scheduler
        ("schedule", "schedule"),
        
        # System monitoring
        ("psutil", "psutil"),
        
        # LLM integration
        ("groq-sdk", "groq"),
        
        # Email sending
        ("sendgrid", "sendgrid"),
        
        # Additional utilities
        ("urllib3", "urllib3"),
        ("lxml", "lxml"),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for dep_name, import_name in dependencies:
        if test_import(dep_name, import_name):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado: {success_count}/{total_count} dependências OK")
    
    if success_count == total_count:
        print("🎉 Todas as dependências estão funcionando!")
        return True
    else:
        print("⚠️  Algumas dependências falharam. Verifique a instalação.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 