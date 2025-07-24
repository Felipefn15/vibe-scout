# 🚂 Deploy no Railway - Vibe Scout

## 🎯 Visão Geral

Este guia explica como fazer o deploy do Vibe Scout no Railway para execução automática das campanhas diárias.

## 📋 Pré-requisitos

### 1. **Railway CLI**
```bash
npm install -g @railway/cli
```

### 2. **Login no Railway**
```bash
railway login
```

### 3. **Variáveis de Ambiente**
Certifique-se de que o arquivo `.env` contém:

```env
# Railway
RAILWAY_API_KEY=b2846ab5-f03a-4056-aa12-d7b8a8d3dd99

# SendGrid
SENDGRID_API_KEY=sua_chave_sendgrid
FROM_EMAIL=felipe@technologie.com.br
FROM_NAME=Felipe França

# Groq (IA)
GROQ_API_KEY=sua_chave_groq

# Outras configurações
LIGHTHOUSE_TIMEOUT=30000
SEO_SCORE_THRESHOLD=70
```

## 🚀 Deploy Automático

### Opção 1: Script Automatizado
```bash
python scripts/deploy_railway.py
```

### Opção 2: Deploy Manual
```bash
# 1. Inicializar projeto (se necessário)
railway init

# 2. Fazer deploy
railway deploy

# 3. Verificar status
railway status
```

## 📊 Monitoramento

### Script de Monitoramento
```bash
# Status do serviço
python scripts/monitor_railway.py status

# Logs recentes
python scripts/monitor_railway.py logs

# Eventos importantes
python scripts/monitor_railway.py events

# Monitoramento em tempo real
python scripts/monitor_railway.py realtime

# Tudo
python scripts/monitor_railway.py all
```

### Comandos Railway Diretos
```bash
# Status do serviço
railway status

# Logs
railway logs

# URL do serviço
railway domain

# Variáveis de ambiente
railway variables
```

## 🔧 Configuração do Railway

### Arquivos de Configuração

#### `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### `nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["python3", "python3-pip", "nodejs", "npm"]

[phases.install]
cmds = [
  "pip install -r requirements.txt",
  "npm install -g @playwright/cli",
  "playwright install chromium"
]

[start]
cmd = "python scheduler/daily_campaign.py"
```

#### `Procfile`
```
web: python scheduler/daily_campaign.py
```

## 📈 Logs Estruturados

O sistema agora usa logs estruturados para melhor monitoramento:

### Eventos Principais
- **🚀 campaign_start**: Início de campanha
- **✅ campaign_complete**: Conclusão de campanha
- **🏢 sector_start**: Início de processamento de setor
- **✅ sector_complete**: Conclusão de setor
- **🎯 lead_collected**: Lead coletado
- **📧 email_sent**: Email enviado
- **❌ email_failed**: Falha no envio
- **⚠️ api_limit_reached**: Limite de API atingido
- **💚 system_health**: Saúde do sistema

### Exemplo de Log
```
2024-01-15 08:00:01 [INFO] daily_campaign: 🚀 Campanha iniciada | {"event": "campaign_start", "sectors": ["Advocacia", "Restaurantes"], "regions": ["Rio de Janeiro", "São Paulo"], "max_emails": 100, "timestamp": "2024-01-15T08:00:01"}
```

## 🔄 Funcionamento no Railway

### 1. **Inicialização**
- O Railway baixa o código
- Instala dependências Python
- Instala Playwright e Chromium
- Inicia o scheduler

### 2. **Execução Diária**
- O sistema roda continuamente
- Às 8:00 AM executa a campanha
- Escolhe 5 setores aleatórios
- Envia até 100 emails
- Registra logs estruturados

### 3. **Monitoramento**
- Logs em tempo real no Railway
- Métricas de saúde do sistema
- Tracking de emails enviados
- Alertas de erros

## 🛠️ Troubleshooting

### Problemas Comuns

#### 1. **Deploy Falha**
```bash
# Verificar logs de build
railway logs

# Verificar variáveis de ambiente
railway variables

# Re-deploy
railway deploy
```

#### 2. **Serviço Não Inicia**
```bash
# Verificar status
railway status

# Verificar logs
railway logs

# Reiniciar serviço
railway service restart
```

#### 3. **Erros de Dependências**
```bash
# Verificar se todas as dependências estão no requirements.txt
cat requirements.txt

# Verificar se o Playwright está instalado
railway logs | grep playwright
```

#### 4. **Limites de API**
- O sistema detecta automaticamente limites
- Logs estruturados mostram quando limites são atingidos
- Sistema para automaticamente ao atingir 100 emails/dia

## 📊 Métricas e Monitoramento

### Métricas Disponíveis
- **Emails enviados por dia**
- **Setores processados**
- **Taxa de sucesso**
- **Tempo de execução**
- **Uso de recursos (CPU, RAM, Disco)**

### Alertas Automáticos
- Limite de emails atingido
- Erros de API
- Falhas de envio
- Problemas de saúde do sistema

## 🔐 Segurança

### Variáveis Sensíveis
- Todas as chaves de API são variáveis de ambiente
- Não são expostas no código
- Gerenciadas pelo Railway

### Rate Limiting
- Sistema de rate limiting integrado
- Respeita limites do SendGrid
- Evita bloqueios de API

## 🎯 Benefícios do Railway

### ✅ Vantagens
- **Zero downtime**: Serviço sempre disponível
- **Escalabilidade**: Recursos automáticos
- **Monitoramento**: Logs em tempo real
- **Segurança**: Variáveis de ambiente seguras
- **Simplicidade**: Deploy com um comando

### 📈 Resultados Esperados
- **100% de uptime** do sistema
- **Execução automática** das campanhas
- **Monitoramento completo** via logs
- **Zero intervenção manual** necessária

## 🚀 Próximos Passos

### 1. **Deploy Inicial**
```bash
python scripts/deploy_railway.py
```

### 2. **Verificar Status**
```bash
python scripts/monitor_railway.py status
```

### 3. **Monitorar Primeira Campanha**
```bash
python scripts/monitor_railway.py realtime
```

### 4. **Configurar Alertas** (Opcional)
- Configurar notificações no Railway
- Integrar com Slack/Discord
- Configurar métricas avançadas

---

## 🎉 **SISTEMA PRONTO PARA PRODUÇÃO!**

O Vibe Scout está configurado para rodar automaticamente no Railway com:

- ✅ **Deploy automatizado**
- ✅ **Logs estruturados**
- ✅ **Monitoramento completo**
- ✅ **Execução diária às 8:00 AM**
- ✅ **100 emails/dia** (limite SendGrid)
- ✅ **5 setores aleatórios** por dia
- ✅ **Zero intervenção manual**

**Execute o deploy agora:**
```bash
python scripts/deploy_railway.py
``` 