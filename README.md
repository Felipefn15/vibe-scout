# Vibe Scout - Sistema de Lead Generation

Sistema avançado de coleta e qualificação de leads para empresas de marketing digital e desenvolvimento web.

## 🚀 Funcionalidades

- **Web Scraping Inteligente**: Coleta leads de múltiplas fontes
- **Detecção de Problemas Web**: Identifica empresas com problemas de presença digital
- **Qualificação Automática**: Filtra e pontua leads automaticamente
- **Geração de Emails**: Cria emails personalizados com IA
- **Campanhas Automatizadas**: Execução programada de campanhas
- **Análise de SEO**: Avalia problemas de SEO das empresas

## 📁 Estrutura do Projeto

```
vibe-scout/
├── analysis/           # Análise de sites e SEO
├── config/            # Configurações do sistema
├── data/              # Dados coletados
├── docs/              # Documentação
├── email_sender/      # Sistema de envio de emails
├── llm/               # Integração com IA/LLM
├── logs/              # Logs do sistema
├── mailer/            # Sistema de email marketing
├── reports/           # Geração de relatórios
├── scraper/           # Sistema de web scraping
├── scripts/           # Scripts de execução
├── scheduler/         # Agendamento de tarefas
├── utils/             # Utilitários
├── venv/              # Ambiente virtual
├── main.py            # Arquivo principal
├── requirements.txt   # Dependências
└── README.md          # Este arquivo
```

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8+
- pip
- Git

### Configuração
```bash
# Clonar repositório
git clone <repository-url>
cd vibe-scout

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas configurações
```

## 🚀 Uso

### Execução Básica
```bash
# Executar sistema principal
python main.py

# Testar web scraper
python scripts/test_enhanced_scraper.py

# Executar campanha específica
python scripts/run_rio_janeiro_campaign.py
```

### Configuração de Campanhas
```bash
# Configurar cron para execução automática
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh
```

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# .env
SENDGRID_API_KEY=your_sendgrid_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
```

### Configurações de Filtros
Edite `config/lead_filters_improved.json` para personalizar:
- Filtros de qualidade de leads
- Palavras-chave por setor
- Indicadores de problemas web
- Limites de pontuação

## 📊 Funcionalidades Principais

### 1. Web Scraping Aprimorado
- **Múltiplas Fontes**: Google, Bing, Google Maps, diretórios locais
- **Anti-Detecção**: Rotação de user agents, rate limiting
- **Fallback Automático**: Se uma fonte falha, tenta outra
- **Detecção de Problemas Web**: Identifica empresas sem site ou com problemas

### 2. Qualificação Inteligente
- **Filtros Avançados**: Validação de nomes, endereços, telefones
- **Pontuação Automática**: Sistema de scoring baseado em múltiplos critérios
- **Deduplicação**: Remove leads duplicados automaticamente
- **Blacklist**: Evita contatar empresas já conhecidas

### 3. Geração de Emails
- **IA Integrada**: Usa Groq/OpenAI para gerar emails personalizados
- **Templates Dinâmicos**: Adapta conteúdo baseado no lead
- **A/B Testing**: Testa diferentes abordagens
- **Análise de Resposta**: Monitora taxas de abertura e resposta

### 4. Campanhas Automatizadas
- **Agendamento**: Execução programada via cron
- **Segmentação**: Campanhas por setor e região
- **Monitoramento**: Tracking de performance em tempo real
- **Relatórios**: Geração automática de relatórios

## 📈 Monitoramento

### Logs
- Logs estruturados em `logs/`
- Diferentes níveis: INFO, WARNING, ERROR
- Rotação automática de logs

### Métricas
- Leads coletados por dia
- Taxa de conversão
- Performance de campanhas
- Uso de APIs

## 🔒 Segurança

- **Rate Limiting**: Respeita limites das APIs
- **Validação de Dados**: Sanitização de inputs
- **Logs Seguros**: Não expõe informações sensíveis
- **Ambiente Isolado**: Execução em venv

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação em `docs/`
- Verifique os logs em `logs/`

## 🔄 Changelog

Veja `CHANGELOG.md` para histórico de mudanças.

---

**Vibe Scout** - Transformando leads em oportunidades de negócio! 🎯 