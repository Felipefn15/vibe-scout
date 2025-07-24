#!/usr/bin/env python3
"""
Script para testar e diagnosticar problemas do SendGrid
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_sendgrid_connection():
    """Testa conexão com SendGrid"""
    print("🔍 Testando conexão com SendGrid...")
    
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    if not sendgrid_key:
        print("❌ SENDGRID_API_KEY não encontrada no .env")
        return False
    
    print(f"✅ Chave SendGrid encontrada: {sendgrid_key[:10]}...")
    
    try:
        from sendgrid import SendGridAPIClient
        
        # Criar cliente
        sg = SendGridAPIClient(api_key=sendgrid_key)
        print("✅ Cliente SendGrid criado com sucesso")
        
        # Testar conexão básica
        try:
            response = sg.client.user.account.get()
            print(f"✅ Conexão SendGrid OK - Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ Erro na conexão SendGrid: {e}")
            
            # Diagnóstico específico
            if "403" in str(e):
                print("\n🔍 Diagnóstico do erro 403:")
                print("   - Chave pode estar expirada")
                print("   - Chave pode ter sido revogada")
                print("   - Conta pode estar suspensa")
                print("   - Limite de uso pode ter sido excedido")
                print("   - Chave pode não ter permissões suficientes")
            
            return False
            
    except ImportError:
        print("❌ Biblioteca SendGrid não instalada")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_sendgrid_sender():
    """Testa o SendGridSender do projeto"""
    print("\n🔍 Testando SendGridSender do projeto...")
    
    try:
        # Adicionar o diretório raiz ao path
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from email_sender.sendgrid_sender import SendGridSender
        
        sender = SendGridSender()
        print("✅ SendGridSender inicializado com sucesso")
        
        # Verificar configuração
        print(f"   - From Email: {sender.from_email}")
        print(f"   - From Name: {sender.from_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no SendGridSender: {e}")
        return False

def check_sendgrid_account():
    """Verifica informações da conta SendGrid"""
    print("\n🔍 Verificando informações da conta SendGrid...")
    
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    if not sendgrid_key:
        print("❌ SENDGRID_API_KEY não encontrada")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        
        sg = SendGridAPIClient(api_key=sendgrid_key)
        
        # Tentar obter informações da conta
        try:
            response = sg.client.user.account.get()
            if response.status_code == 200:
                account_info = response.body
                print("✅ Informações da conta SendGrid:")
                print(f"   - Email: {account_info.get('email', 'N/A')}")
                print(f"   - First Name: {account_info.get('first_name', 'N/A')}")
                print(f"   - Last Name: {account_info.get('last_name', 'N/A')}")
                print(f"   - Website: {account_info.get('website', 'N/A')}")
                return True
        except Exception as e:
            print(f"❌ Erro ao obter informações da conta: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def provide_solutions():
    """Fornece soluções para problemas do SendGrid"""
    print("\n📋 SOLUÇÕES PARA PROBLEMAS DO SENDGRID:")
    print("="*50)
    
    print("\n1. 🔑 GERAR NOVA CHAVE API:")
    print("   - Acesse: https://app.sendgrid.com/settings/api_keys")
    print("   - Clique em 'Create API Key'")
    print("   - Escolha 'Full Access' ou 'Restricted Access' (Mail Send)")
    print("   - Copie a nova chave e atualize o .env")
    
    print("\n2. 📧 VERIFICAR CONTA:")
    print("   - Acesse: https://app.sendgrid.com/settings/account")
    print("   - Verifique se a conta está ativa")
    print("   - Verifique se há limites de uso")
    
    print("\n3. 🔍 VERIFICAR DOMÍNIO:")
    print("   - Acesse: https://app.sendgrid.com/settings/sender_auth")
    print("   - Configure autenticação de domínio se necessário")
    
    print("\n4. 📊 VERIFICAR ESTATÍSTICAS:")
    print("   - Acesse: https://app.sendgrid.com/statistics")
    print("   - Verifique se há bounces ou spam reports")
    
    print("\n5. 🆘 SUPORTE:")
    print("   - SendGrid Support: https://support.sendgrid.com/")
    print("   - Status Page: https://status.sendgrid.com/")

def main():
    """Função principal"""
    print("🚀 DIAGNÓSTICO COMPLETO DO SENDGRID")
    print("="*50)
    
    # Testar conexão básica
    connection_ok = test_sendgrid_connection()
    
    # Testar SendGridSender
    sender_ok = test_sendgrid_sender()
    
    # Verificar conta
    account_ok = check_sendgrid_account()
    
    # Resumo
    print(f"\n📊 RESUMO:")
    print(f"   - Conexão: {'✅ OK' if connection_ok else '❌ FALHOU'}")
    print(f"   - SendGridSender: {'✅ OK' if sender_ok else '❌ FALHOU'}")
    print(f"   - Conta: {'✅ OK' if account_ok else '❌ FALHOU'}")
    
    if not connection_ok:
        provide_solutions()
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    if connection_ok and sender_ok:
        print("✅ SendGrid está funcionando! Pode fazer deploy.")
    else:
        print("❌ Corrija os problemas do SendGrid antes do deploy.")
        print("   Execute este script novamente após as correções.")

if __name__ == "__main__":
    main() 