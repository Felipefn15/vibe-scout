#!/usr/bin/env python3
"""
Script para corrigir o arquivo .env adicionando FROM_NAME
"""

import os
import re

def fix_env_file():
    """Adiciona FROM_NAME ao arquivo .env se não existir"""
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ Arquivo .env não encontrado!")
        return False
    
    # Ler o arquivo atual
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se FROM_NAME já existe
    if 'FROM_NAME=' in content:
        print("✅ FROM_NAME já existe no arquivo .env")
        return True
    
    # Adicionar FROM_NAME após FROM_EMAIL
    if 'FROM_EMAIL=' in content:
        # Encontrar a linha do FROM_EMAIL
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            if line.strip().startswith('FROM_EMAIL='):
                # Adicionar FROM_NAME na próxima linha
                new_lines.append('FROM_NAME=Felipe França')
        
        # Escrever o arquivo atualizado
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ FROM_NAME adicionado ao arquivo .env")
        return True
    else:
        print("❌ FROM_EMAIL não encontrado no arquivo .env")
        return False

def check_sendgrid_key():
    """Verifica se a chave SendGrid está válida"""
    print("\n🔍 Verificando chave SendGrid...")
    
    # Verificar formato da chave
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    if not sendgrid_key:
        print("❌ SENDGRID_API_KEY não encontrada")
        return False
    
    if not sendgrid_key.startswith('SG.'):
        print("❌ Formato da chave SendGrid inválido (deve começar com 'SG.')")
        return False
    
    print("✅ Formato da chave SendGrid parece válido")
    print("⚠️  Erro 403 pode indicar:")
    print("   - Chave expirada")
    print("   - Chave revogada")
    print("   - Conta SendGrid suspensa")
    print("   - Limite de uso excedido")
    
    return True

def main():
    """Função principal"""
    print("🔧 Corrigindo configuração do .env...")
    
    # Corrigir FROM_NAME
    if fix_env_file():
        print("✅ Configuração do .env corrigida!")
    else:
        print("❌ Erro ao corrigir .env")
        return
    
    # Verificar SendGrid
    check_sendgrid_key()
    
    print("\n📋 Próximos passos:")
    print("1. Verificar se a chave SendGrid ainda é válida")
    print("2. Se necessário, gerar uma nova chave no SendGrid")
    print("3. Executar: python utils/api_validator.py")
    print("4. Se tudo OK, fazer deploy no Railway")

if __name__ == "__main__":
    main() 