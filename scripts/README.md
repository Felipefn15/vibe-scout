# Scripts do Vibe Scout

Este diretório contém os scripts essenciais para execução e teste do sistema.

## Scripts Principais

### `test_enhanced_scraper.py`
- Testa o sistema de web scraping aprimorado
- Verifica funcionalidade do `EnhancedWebScraper`
- Testa detecção de problemas web
- Valida integração com `WebProblemLeadCollector`

### `run_rio_janeiro_campaign.py`
- Executa campanha específica para o Rio de Janeiro
- Coleta leads de múltiplos setores
- Aplica filtros de qualidade
- Gera relatórios de resultados

### `fix_env.py`
- Corrige problemas de ambiente
- Instala dependências faltantes
- Configura variáveis de ambiente
- Resolve conflitos de versão

### `setup_cron.sh`
- Configura tarefas agendadas
- Define execução automática de campanhas
- Configura monitoramento diário
- Script para servidor Linux/Unix

## Como Executar

### Teste do Sistema
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar teste do scraper
python scripts/test_enhanced_scraper.py

# Executar campanha
python scripts/run_rio_janeiro_campaign.py
```

### Configuração de Ambiente
```bash
# Corrigir ambiente
python scripts/fix_env.py

# Configurar cron (Linux/Unix)
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh
```

## Estrutura dos Scripts

Todos os scripts seguem padrões:
- **Logging estruturado**: Para debug e monitoramento
- **Tratamento de erros**: Graceful handling de exceções
- **Configuração flexível**: Parâmetros via argumentos
- **Documentação inline**: Comentários explicativos

## Dependências

Os scripts dependem de:
- Python 3.8+
- Ambiente virtual ativado
- Dependências instaladas (`requirements.txt`)
- Configurações válidas em `config/` 