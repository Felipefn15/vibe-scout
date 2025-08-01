#!/usr/bin/env python3
"""
Teste específico para verificar configuração do SendGrid
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar variáveis de ambiente
load_dotenv()

def test_sendgrid_configuration():
    """Testa a configuração do SendGrid passo a passo"""
    
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO SENDGRID")
    print("=" * 50)
    
    # 1. Verificar se o arquivo .env está sendo carregado
    print("\n1️⃣ Verificando carregamento do .env...")
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        print(f"✅ Arquivo .env encontrado: {env_file}")
    else:
        print(f"❌ Arquivo .env não encontrado em: {env_file}")
        return False
    
    # 2. Verificar se a variável SENDGRID_API_KEY está definida
    print("\n2️⃣ Verificando variável SENDGRID_API_KEY...")
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    if sendgrid_key:
        print(f"✅ SENDGRID_API_KEY encontrada: {sendgrid_key[:10]}...{sendgrid_key[-10:]}")
    else:
        print("❌ SENDGRID_API_KEY não encontrada")
        return False
    
    # 3. Verificar formato da chave
    print("\n3️⃣ Verificando formato da chave...")
    if sendgrid_key.startswith('SG.'):
        print("✅ Formato da chave parece correto (começa com 'SG.')")
    else:
        print("⚠️ Formato da chave pode estar incorreto (deveria começar com 'SG.')")
    
    # 4. Verificar outras variáveis de email
    print("\n4️⃣ Verificando outras variáveis de email...")
    from_email = os.getenv('FROM_EMAIL')
    from_name = os.getenv('FROM_NAME')
    consultant_email = os.getenv('CONSULTANT_EMAIL')
    
    print(f"   - FROM_EMAIL: {from_email}")
    print(f"   - FROM_NAME: {from_name}")
    print(f"   - CONSULTANT_EMAIL: {consultant_email}")
    
    # 5. Testar importação do SendGrid
    print("\n5️⃣ Testando importação do SendGrid...")
    try:
        import sendgrid
        print("✅ Biblioteca SendGrid importada com sucesso")
    except ImportError as e:
        print(f"❌ Erro na importação do SendGrid: {e}")
        print("   Execute: pip install sendgrid")
        return False
    
    # 6. Testar criação do cliente
    print("\n6️⃣ Testando criação do cliente SendGrid...")
    try:
        from sendgrid import SendGridAPIClient
        client = SendGridAPIClient(api_key=sendgrid_key)
        print("✅ Cliente SendGrid criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar cliente SendGrid: {e}")
        return False
    
    # 7. Testar conexão com a API
    print("\n7️⃣ Testando conexão com a API SendGrid...")
    try:
        # Testar endpoint de usuário
        response = client.client.user.account.get()
        print(f"   - Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Conexão com API SendGrid bem-sucedida!")
            account_info = response.body
            print(f"   - Email verificado: {account_info.get('email', 'N/A')}")
            print(f"   - Primeiro nome: {account_info.get('first_name', 'N/A')}")
            print(f"   - Último nome: {account_info.get('last_name', 'N/A')}")
        elif response.status_code == 401:
            print("❌ Erro 401: API key inválida ou expirada")
            return False
        elif response.status_code == 403:
            print("❌ Erro 403: Sem permissão para acessar este recurso")
            return False
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False
    
    # 8. Testar envio de email
    print("\n8️⃣ Testando envio de email...")
    try:
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        # Criar email de teste
        from_email_obj = Email(from_email, from_name)
        to_email_obj = To(consultant_email or from_email)
        subject = "Teste de Configuração - Vibe Scout"
        content = Content("text/plain", "Este é um email de teste para verificar a configuração do SendGrid no Vibe Scout.")
        mail = Mail(from_email_obj, to_email_obj, subject, content)
        
        # Enviar email
        response = client.send(mail)
        
        if response.status_code in [200, 201, 202]:
            print("✅ Email de teste enviado com sucesso!")
            print(f"   - Status code: {response.status_code}")
        else:
            print(f"❌ Falha no envio do email: {response.status_code}")
            print(f"   - Headers: {response.headers}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar email de teste: {e}")
        return False
    
    print("\n✅ CONFIGURAÇÃO DO SENDGRID VERIFICADA COM SUCESSO!")
    return True

def test_sendgrid_quota():
    """Testa a quota do SendGrid"""
    
    print("\n📊 VERIFICANDO QUOTA DO SENDGRID")
    print("=" * 40)
    
    try:
        sendgrid_key = os.getenv('SENDGRID_API_KEY')
        from sendgrid import SendGridAPIClient
        client = SendGridAPIClient(api_key=sendgrid_key)
        
        # Verificar estatísticas de envio
        response = client.client.user.account.get()
        if response.status_code == 200:
            account_info = response.body
            
            print(f"   - Email: {account_info.get('email', 'N/A')}")
            print(f"   - Tipo de conta: {account_info.get('type', 'N/A')}")
            
            # Tentar obter estatísticas (pode não estar disponível em contas gratuitas)
            try:
                stats_response = client.client.stats.get()
                if stats_response.status_code == 200:
                    stats = stats_response.body
                    print(f"   - Estatísticas disponíveis: {len(stats)} registros")
                else:
                    print("   - Estatísticas não disponíveis nesta conta")
            except:
                print("   - Estatísticas não disponíveis nesta conta")
                
    except Exception as e:
        print(f"❌ Erro ao verificar quota: {e}")

def main():
    """Função principal"""
    print("🚀 INICIANDO TESTE DE CONFIGURAÇÃO DO SENDGRID")
    print("=" * 60)
    
    # Teste básico de configuração
    success = test_sendgrid_configuration()
    
    if success:
        # Teste de quota
        test_sendgrid_quota()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
    else:
        print("\n💥 TESTES FALHARAM - VERIFIQUE A CONFIGURAÇÃO")

if __name__ == "__main__":
    main() 