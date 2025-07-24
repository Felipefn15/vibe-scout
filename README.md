# Vibe Scout - Sistema de Prospecção e Análise Digital

Sistema automatizado de prospecção de leads, análise de performance digital e outreach personalizado usando CrewAI.

## 🚀 Visão Geral

O Vibe Scout é um pipeline completo de marketing digital que:

1. **Coleta leads** de Google Search, Maps e Instagram
2. **Analisa performance** de sites usando Lighthouse e SEO
3. **Avalia presença** nas redes sociais
4. **Gera emails personalizados** usando LLM (Groq)
5. **Executa campanhas** de email via SendGrid
6. **Gera relatórios** completos em Excel

## 📋 Pré-requisitos

- Python 3.8+
- Contas gratuitas nas APIs:
  - [Groq](https://console.groq.com/) (LLM)
  - [SendGrid](https://sendgrid.com/) (Email)
  - [Lighthouse CLI](https://developers.google.com/web/tools/lighthouse) (Opcional)

## 🛠️ Instalação

### 1. Clone o repositório
```bash
cd /Users/felipe/Desktop
git clone <repository-url> vibe-scout
cd vibe-scout
```

### 2. Crie ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente
```bash
cp env.example .env
```

Edite o arquivo `.env` com suas chaves de API:
```env
# API Keys (Free tier)
GROQ_API_KEY=your_groq_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Email Configuration
FROM_EMAIL=your_email@domain.com
CONSULTANT_EMAIL=consultant@domain.com

# Scraping Configuration
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
REQUEST_DELAY=2

# Analysis Configuration
LIGHTHOUSE_TIMEOUT=30000
SEO_SCORE_THRESHOLD=70

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/vibe_scout.log
```

### 5. Instale Lighthouse CLI (Opcional)
```bash
npm install -g lighthouse
```

## 🎯 Como Usar

### Execução Completa do Pipeline

```bash
python main.py --industry "restaurant" --region "São Paulo"
```

### Parâmetros Disponíveis

- `--industry`: Setor/indústria alvo (padrão: "restaurant")
- `--region`: Região/estado alvo (padrão: "São Paulo")
- `--test`: Modo de teste com dados mock

### Exemplos de Uso

```bash
# Análise de restaurantes em São Paulo
python main.py --industry "restaurant" --region "São Paulo"

# Análise de lojas de roupas no Rio de Janeiro
python main.py --industry "clothing store" --region "Rio de Janeiro"

# Modo de teste
python main.py --industry "coffee shop" --region "Belo Horizonte" --test
```

## 📁 Estrutura do Projeto

```
vibe-scout/
├── scraper/              # Coleta de leads
│   └── collect.py
├── analysis/             # Análise de sites e redes sociais
│   ├── site_seo.py
│   └── social.py
├── llm/                  # Geração de emails com IA
│   └── generate_email.py
├── mailer/               # Envio de emails
│   └── send_emails.py
├── reports/              # Geração de relatórios
│   └── build_report.py
├── main.py               # Pipeline principal com CrewAI
├── requirements.txt      # Dependências
├── env.example          # Exemplo de configuração
└── README.md            # Este arquivo
```

## 🔄 Fluxo do Pipeline

1. **Coleta de Leads** (`scraper/collect.py`)
   - Busca no Google Search
   - Busca no Google Maps
   - Busca no Instagram
   - Remove duplicatas
   - Salva em `leads_data.json`

2. **Análise de Sites** (`analysis/site_seo.py`)
   - Executa Lighthouse CLI
   - Análise SEO on-page
   - Métricas de performance
   - Salva em `analyzed_leads.json`

3. **Análise de Redes Sociais** (`analysis/social.py`)
   - Análise de Instagram
   - Análise de Facebook
   - Análise de LinkedIn
   - Salva em `leads_with_social.json`

4. **Geração de Emails** (`llm/generate_email.py`)
   - Usa Groq LLM
   - Personalização baseada em análise
   - Emails em português
   - Salva em `generated_emails.json`

5. **Envio de Emails** (`mailer/send_emails.py`)
   - Envio via SendGrid
   - Tracking de delivery
   - Relatório para consultor
   - Salva em `email_campaign_results.json`

6. **Geração de Relatório** (`reports/build_report.py`)
   - Relatório Excel completo
   - Múltiplas abas
   - Gráficos e visualizações
   - Salva como `vibe_scout_report_YYYYMMDD_HHMMSS.xlsx`

## 📊 Arquivos de Saída

- `leads_data.json`: Leads coletados
- `analyzed_leads.json`: Análise de sites
- `leads_with_social.json`: Análise de redes sociais
- `generated_emails.json`: Emails gerados
- `email_campaign_results.json`: Resultados da campanha
- `vibe_scout_report_*.xlsx`: Relatório final
- `vibe_scout.log`: Logs do sistema

## 🎛️ Configuração Avançada

### Personalização de Análise

Edite os arquivos de análise para ajustar:
- Thresholds de scores
- Métricas específicas
- Critérios de qualidade

### Personalização de Emails

Modifique `llm/generate_email.py` para:
- Ajustar tom de voz
- Incluir informações específicas
- Personalizar call-to-action

### Configuração de APIs

Para usar APIs pagas:
- Atualize as chaves no `.env`
- Modifique os endpoints nos módulos
- Ajuste rate limits conforme necessário

## 🧪 Modo de Teste

O sistema inclui dados mock para teste:

```bash
python main.py --test
```

Isso executa o pipeline completo com dados simulados, útil para:
- Testar a integração
- Verificar o fluxo
- Desenvolver novas funcionalidades

## 📈 Monitoramento

### Logs
- Logs detalhados em `vibe_scout.log`
- Níveis: INFO, WARNING, ERROR
- Timestamps e contexto

### Métricas
- Taxa de sucesso de emails
- Scores de personalização
- Performance de análise
- Tempo de execução

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**
   ```
   GROQ_API_KEY not found. Using mock email generation.
   ```
   Solução: Configure a chave no arquivo `.env`

2. **Lighthouse não encontrado**
   ```
   Lighthouse CLI not found. Using mock data.
   ```
   Solução: Instale o Lighthouse CLI ou use dados mock

3. **Erro de conexão**
   ```
   Error in Google search: Connection timeout
   ```
   Solução: Verifique a conexão de internet e aumente `REQUEST_DELAY`

### Logs de Debug

Para debug detalhado:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🆘 Suporte

Para suporte:
- Abra uma issue no GitHub
- Consulte os logs em `vibe_scout.log`
- Verifique a documentação das APIs

## 🔮 Roadmap

- [ ] Integração com mais redes sociais
- [ ] Análise de concorrência
- [ ] Dashboard web
- [ ] Integração com CRM
- [ ] Automação de follow-up
- [ ] Análise de sentimentos
- [ ] Machine Learning para scoring

---

**Vibe Scout** - Transformando dados em oportunidades de negócio! 🚀 