# Configuração do Vibe Scout

Este diretório contém todos os arquivos de configuração do sistema.

## Arquivos de Configuração

### `lead_filters_improved.json`
- Filtros avançados para validação de leads
- Configurações de qualidade e relevância
- Palavras-chave para detecção de problemas web

### `lead_filters.json`
- Filtros básicos de leads (legado)
- Mantido para compatibilidade

### `lead_filters.py`
- Implementação Python dos filtros de leads
- Classe `LeadFilter` para validação

### `markets.json`
- Configurações de mercados e regiões
- Parâmetros específicos por localização

### `rio_janeiro_campaign.json`
- Configuração específica para campanha do Rio de Janeiro
- Parâmetros de segmentação e targeting

### `sectors.json`
- Definição de setores de negócio
- Categorização de leads por setor

### `ti_filters.json`
- Filtros específicos para TI
- Configurações para empresas de tecnologia

## Como Usar

```python
from config.lead_filters import LeadFilter

# Carregar filtros
filter = LeadFilter("config/lead_filters_improved.json")

# Validar lead
is_valid = filter.is_valid_business_name("Nome da Empresa")
```

## Estrutura dos Filtros

Os filtros seguem uma estrutura JSON com:
- **business_name_filters**: Regras para nomes de empresas
- **web_problem_indicators**: Indicadores de problemas web
- **seo_problem_keywords**: Palavras-chave de problemas SEO
- **quality_thresholds**: Limites de qualidade
- **sector_keywords**: Palavras-chave por setor 