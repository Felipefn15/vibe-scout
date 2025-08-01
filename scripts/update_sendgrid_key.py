#!/usr/bin/env python3
"""
Script para atualizar a chave do SendGrid
Facilita o processo de renovação da chave API
"""

import os
import re
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def backup_env_file():
    """Faz backup do arquivo .env"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'.env.backup.{timestamp}'
    
    if os.path.exists('.env'):
        shutil.copy2('.env', backup_name)
        print(f"✅ Backup criado: {backup_name}")
        return backup_name
    else:
        print("❌ Arquivo .env não encontrado")
        return None

def get_current_sendgrid_key():
    """Obtém a chave atual do SendGrid"""
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        match = re.search(r'SENDGRID_API_KEY=([^\n]+)', content)
        if match:
            return match.group(1).strip("'\"")
        else:
            return None
    except Exception as e:
        print(f"❌ Erro ao ler chave atual: {e}")
        return None

def update_sendgrid_key(new_key):
    """Atualiza a chave do SendGrid no arquivo .env"""
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Verificar se a chave já existe
        if 'SENDGRID_API_KEY=' in content:
            # Substituir chave existente
            old_pattern = r'SENDGRID_API_KEY=[^\n]+'
            new_line = f'SENDGRID_API_KEY={new_key}'
            new_content = re.sub(old_pattern, new_line, content)
        else:
            # Adicionar nova linha
            new_content = content + f'\nSENDGRID_API_KEY={new_key}\n'
        
        # Fazer backup antes de alterar
        backup_env_file()
        
        # Escrever novo conteúdo
        with open('.env', 'w') as f:
            f.write(new_content)
        
        print("✅ Chave do SendGrid atualizada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar chave: {e}")
        return False

def validate_sendgrid_key(key):
    """Valida o formato da chave do SendGrid"""
    if not key:
        return False, "Chave vazia"
    
    if not key.startswith('SG.'):
        return False, "Chave deve começar com 'SG.'"
    
    if len(key) < 50:
        return False, "Chave muito curta"
    
    return True, "Formato válido"

def test_sendgrid_connection():
    """Testa a conexão com o SendGrid"""
    try:
        from email_sender.sendgrid_sender import SendGridSender
        sender = SendGridSender()
        success = sender.test_connection()
        
        if success:
            print("✅ Conexão com SendGrid testada com sucesso")
            return True
        else:
            print("❌ Falha na conexão com SendGrid")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

def main():
    """Função principal"""
    print("🔄 ATUALIZADOR DE CHAVE SENDGRID")
    print("=" * 40)
    
    # Mostrar chave atual
    current_key = get_current_sendgrid_key()
    if current_key:
        print(f"\n📋 Chave atual: {current_key[:10]}...{current_key[-10:]}")
    else:
        print("\n📋 Nenhuma chave encontrada")
    
    # Solicitar nova chave
    print("\n🔑 Digite a nova chave do SendGrid:")
    print("   (Formato: SG.xxxxxxxxxxxxxxxxxxxxx)")
    new_key = input("   Nova chave: ").strip()
    
    # Validar formato
    is_valid, message = validate_sendgrid_key(new_key)
    if not is_valid:
        print(f"❌ Chave inválida: {message}")
        return
    
    print(f"✅ {message}")
    
    # Confirmar atualização
    print(f"\n⚠️  ATENÇÃO: Esta ação irá:")
    print("   • Fazer backup do arquivo .env atual")
    print("   • Substituir a chave do SendGrid")
    print("   • Testar a nova conexão")
    
    confirm = input("\n🤔 Confirmar atualização? (s/N): ").strip().lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Atualização cancelada")
        return
    
    # Atualizar chave
    print("\n🔄 Atualizando chave...")
    if update_sendgrid_key(new_key):
        print("✅ Chave atualizada no arquivo .env")
        
        # Testar conexão
        print("\n🧪 Testando nova conexão...")
        if test_sendgrid_connection():
            print("\n🎉 SUCESSO! SendGrid configurado corretamente")
            print("\n📋 Próximos passos:")
            print("   1. Executar: python utils/service_status.py")
            print("   2. Executar: python scripts/diagnose_apis.py")
            print("   3. Se tudo OK, executar campanha de teste")
        else:
            print("\n⚠️  ATENÇÃO: Conexão falhou")
            print("   • Verificar se a chave está correta")
            print("   • Verificar se a conta SendGrid está ativa")
            print("   • Verificar limites da conta")
    else:
        print("❌ Falha ao atualizar chave")

def interactive_mode():
    """Modo interativo para obter a chave"""
    print("\n🔧 MODO INTERATIVO")
    print("=" * 20)
    print("Para obter uma nova chave do SendGrid:")
    print("1. Acesse: https://app.sendgrid.com")
    print("2. Faça login na sua conta")
    print("3. Vá para: Settings > API Keys")
    print("4. Clique em: Create API Key")
    print("5. Selecione: Full Access ou Restricted Access (Mail Send)")
    print("6. Copie a chave gerada")
    print("7. Cole aqui quando solicitado")
    
    input("\nPressione ENTER quando estiver pronto...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Uso: python scripts/update_sendgrid_key.py [--help]")
        print("\nOpções:")
        print("  --help     Mostra este help")
        print("\nExemplo:")
        print("  python scripts/update_sendgrid_key.py")
        sys.exit(0)
    
    # Mostrar modo interativo se solicitado
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    
    main() 