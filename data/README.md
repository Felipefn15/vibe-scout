# Dados do Vibe Scout

Este diretório contém os arquivos de dados do sistema.

## Arquivos de Dados

### `leads.json`
- Leads coletados pelo sistema
- Dados estruturados de empresas
- Informações de contato e negócio

### `emails.json`
- Histórico de emails enviados
- Templates e conteúdo
- Métricas de entrega

### `campaign_results.json`
- Resultados de campanhas executadas
- Métricas de performance
- Estatísticas de conversão

### `daily_usage.json`
- Uso diário do sistema
- Limites de API
- Controle de rate limiting

### `blacklist_leads.json`
- Leads bloqueados/blacklist
- Empresas não elegíveis
- Filtros de exclusão

### `contacted_leads.json`
- Leads já contactados
- Histórico de interações
- Evita duplicação de contato

## Estrutura dos Dados

### Formato JSON
Todos os arquivos seguem formato JSON estruturado:
```json
{
  "timestamp": "2025-08-01T10:00:00Z",
  "data": [...],
  "metadata": {
    "version": "1.0",
    "source": "enhanced_scraper"
  }
}
```

### Validação
- Dados são validados antes de salvar
- Estrutura consistente entre arquivos
- Backup automático de dados importantes

## Backup e Manutenção

### Backup Automático
- Dados são salvos com timestamp
- Versões anteriores mantidas
- Recuperação em caso de erro

### Limpeza
- Arquivos antigos são removidos automaticamente
- Dados duplicados são consolidados
- Logs de erro são mantidos para debug

## Uso no Sistema

```python
import json
from pathlib import Path

# Carregar dados
with open('data/leads.json', 'r') as f:
    leads = json.load(f)

# Salvar dados
with open('data/leads.json', 'w') as f:
    json.dump(leads, f, indent=2)
``` 