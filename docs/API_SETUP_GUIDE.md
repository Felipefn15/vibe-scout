# Guia de Configuração das APIs - Vibe Scout

## 🎯 Visão Geral

O Vibe Scout utiliza duas APIs fundamentais para seu funcionamento:

1. **Groq API** - Para geração de emails personalizados com IA
2. **SendGrid API** - Para envio de emails

## 🔑 Configuração das APIs

### 1. Groq API (🤖 IA para Geração de Emails)

#### Obtendo a Chave:
1. Acesse [console.groq.com](https://console.groq.com)
2. Faça login ou crie uma conta
3. Vá para "API Keys" no menu lateral
4. Clique em "Create API Key"
5. Copie a chave (formato: `gsk_...`)

#### Configuração:
```bash
# No arquivo .env
GROQ_API_KEY=gsk_sua_chave_aqui
GROQ_RATE_LIMIT=45
GROQ_TIME_WINDOW=60
```

#### Status Atual: ✅ FUNCIONANDO
- Chave válida e funcionando
- Rate limit configurado corretamente
- Geração de emails operacional

### 2. SendGrid API (📧 Envio de Emails)

#### Obtendo a Chave:
1. Acesse [sendgrid.com](https://sendgrid.com)
2. Faça login na sua conta
3. Vá para "Settings" > "API Keys"
4. Clique em "Create API Key"
5. Selecione "Full Access" ou "Restricted Access" (Mail Send)
6. Copie a chave (formato: `SG....`)

#### Configuração:
```bash
# No arquivo .env
SENDGRID_API_KEY=SG.sua_chave_aqui
FROM_EMAIL=seu_email@dominio.com
FROM_NAME=Seu Nome
```

#### Status Atual: ❌ PROBLEMA DETECTADO
- Erro 403 (Forbidden) - Chave provavelmente expirada
- **Ação necessária**: Gerar nova chave no SendGrid

## 🔧 Solução de Problemas

### SendGrid - Erro 403

#### Possíveis Causas:
1. **Chave expirada** - Mais comum
2. **Chave revogada** - Por questões de segurança
3. **Conta suspensa** - Por violação de termos
4. **Limite excedido** - Free tier limitado

#### Solução:
1. Acesse [SendGrid Dashboard](https://app.sendgrid.com)
2. Vá para "Settings" > "API Keys"
3. Delete a chave atual
4. Crie uma nova chave
5. Atualize o arquivo `.env`

### Verificação de Status

Execute o diagnóstico:
```bash
python scripts/diagnose_apis.py
```

### Teste Individual

```bash
# Testar Groq
python -c "
import asyncio
from llm.llm_client import ModularLLMClient
async def test():
    client = ModularLLMClient(['Groq'])
    response = await client.generate('Teste')
    print(f'Groq: {response.success}')
asyncio.run(test())
"

# Testar SendGrid
python -c "
from email_sender.sendgrid_sender import SendGridSender
sender = SendGridSender()
print(f'SendGrid: {sender.test_connection()}')
"
```

## 🚀 Sistema de Fallback

O Vibe Scout possui um sistema robusto de fallback:

### Sem Groq:
- Usa templates pré-definidos para emails
- Funcionalidade limitada mas operacional

### Sem SendGrid:
- Simula envio de emails
- Logs detalhados para debug
- Não envia emails reais

### Ambos Ausentes:
- Sistema ainda funciona para coleta de leads
- Análise de sites operacional
- Relatórios gerados normalmente

## 📊 Monitoramento

### Logs Importantes:
```bash
# Verificar logs de API
tail -f logs/vibe_scout.log | grep -E "(GROQ|SENDGRID|API)"

# Verificar status das APIs
python utils/api_validator.py
```

### Métricas:
- Taxa de sucesso das APIs
- Latência de resposta
- Uso de tokens (Groq)
- Emails enviados (SendGrid)

## 🔄 Atualização de Chaves

### Processo Seguro:
1. **Backup** da configuração atual
2. **Teste** da nova chave em ambiente isolado
3. **Atualização** gradual (uma API por vez)
4. **Verificação** completa após mudança

### Script de Atualização:
```bash
# Backup automático
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Atualizar chave
sed -i '' 's/OLD_KEY/NEW_KEY/' .env

# Testar
python scripts/diagnose_apis.py
```

## 💡 Boas Práticas

### Segurança:
- Nunca commitar chaves no Git
- Usar variáveis de ambiente
- Rotacionar chaves regularmente
- Monitorar uso das APIs

### Performance:
- Configurar rate limits adequados
- Usar cache quando possível
- Monitorar latência
- Implementar retry logic

### Monitoramento:
- Logs estruturados
- Alertas para falhas
- Métricas de uso
- Relatórios de status

## 🆘 Suporte

### Problemas Comuns:

1. **"API key not found"**
   - Verificar arquivo `.env`
   - Confirmar nome da variável

2. **"Rate limit exceeded"**
   - Ajustar `GROQ_RATE_LIMIT`
   - Implementar delays

3. **"403 Forbidden"**
   - Gerar nova chave
   - Verificar permissões

4. **"Connection timeout"**
   - Verificar internet
   - Ajustar timeouts

### Contatos:
- **Groq**: [support@groq.com](mailto:support@groq.com)
- **SendGrid**: [support@sendgrid.com](mailto:support@sendgrid.com)

## 📈 Próximos Passos

1. ✅ **Groq**: Configurado e funcionando
2. 🔄 **SendGrid**: Gerar nova chave
3. 🧪 **Testes**: Executar campanha completa
4. 📊 **Monitoramento**: Implementar alertas
5. 🚀 **Produção**: Deploy no Railway 