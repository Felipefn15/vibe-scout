# Sistema de Campanhas Diárias - Vibe Scout

## 📋 Visão Geral

O sistema de campanhas diárias automatiza o processo de coleta de leads e envio de emails, rodando diariamente às 8:00 da manhã. O sistema escolhe 5 setores aleatórios e envia até 100 emails por dia (limite do SendGrid gratuito).

## 🎯 Funcionalidades

### ✅ Automatização Completa
- **Execução diária**: Roda automaticamente às 8:00 AM
- **Seleção inteligente**: Escolhe 5 setores aleatórios por dia
- **Rotação de regiões**: Trabalha com 3 regiões diferentes por campanha
- **Controle de limite**: Respeita o limite de 100 emails/dia do SendGrid

### 📊 Monitoramento
- **Tracking de uso**: Registra emails enviados e setores processados
- **Logs detalhados**: Registra todas as atividades
- **Status em tempo real**: Monitoramento do progresso das campanhas

### 🔄 Rotação Inteligente
- **Setores variados**: 15 setores diferentes disponíveis
- **Sem repetição**: Evita processar o mesmo setor no mesmo dia
- **Distribuição equilibrada**: Garante cobertura de todos os setores

## 🏗️ Arquitetura

### Componentes Principais

```
scheduler/
├── daily_campaign.py      # Sistema principal de campanhas
└── monitor_campaigns.py   # Monitoramento e status

config/
├── sectors.json          # Configuração dos setores
└── lead_filters.json     # Filtros de leads

scripts/
├── setup_cron.sh         # Configuração automática do cron
└── monitor_campaigns.py  # Script de monitoramento

logs/
├── daily_campaign.log    # Logs das campanhas
└── cron.log             # Logs do cron job
```

## 🚀 Configuração

### 1. Instalação das Dependências

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install schedule
```

### 2. Configuração do Cron Job

```bash
# Executar script de configuração
./scripts/setup_cron.sh
```

O script irá:
- Verificar o ambiente virtual
- Criar o cron job para 8:00 AM
- Configurar logs automáticos

### 3. Verificação da Configuração

```bash
# Verificar cron jobs ativos
crontab -l

# Testar execução manual
python scheduler/daily_campaign.py --run-now
```

## 📈 Monitoramento

### Status das Campanhas

```bash
# Ver status atual
python scripts/monitor_campaigns.py

# Ver logs recentes
python scripts/monitor_campaigns.py --logs

# Ver logs do cron
python scripts/monitor_campaigns.py --cron-logs

# Ver tudo
python scripts/monitor_campaigns.py --all
```

### Exemplo de Saída

```
=== Vibe Scout Campaign Status ===
📅 Date: 2024-01-15
📧 Emails Sent: 45/100 (45.0%)
📊 Remaining: 55 emails
🏢 Sectors Processed: 2/15
✅ Processed: Advocacia, Restaurantes
🔄 Status: Campaign in progress
```

## 🎛️ Configuração de Setores

### Setores Disponíveis

O sistema inclui 15 setores configuráveis em `config/sectors.json`:

1. **Advocacia** - Escritórios de advocacia
2. **Restaurantes** - Restaurantes e gastronomia
3. **Farmácias** - Farmácias e drogarias
4. **Clínicas** - Clínicas médicas
5. **Academias** - Academias e fitness
6. **Salões de Beleza** - Estética e beleza
7. **Imobiliárias** - Imóveis e corretores
8. **Consultorias** - Consultoria empresarial
9. **Padarias** - Padarias e confeitarias
10. **Lojas** - Comércio varejista
11. **Escolas** - Instituições de ensino
12. **Oficinas** - Mecânicas e auto centers
13. **Pet Shops** - Pet shops e veterinários
14. **Lavanderias** - Lavanderias e limpeza
15. **Fotógrafos** - Fotógrafos e estúdios

### Adicionando Novos Setores

Para adicionar um novo setor, edite `config/sectors.json`:

```json
{
  "name": "Novo Setor",
  "keywords": ["palavra1", "palavra2", "palavra3"],
  "description": "Descrição do setor"
}
```

## 📊 Controle de Limites

### Limites Diários
- **Máximo de emails**: 100 por dia (limite SendGrid gratuito)
- **Setores por dia**: 5 setores aleatórios
- **Regiões por campanha**: 3 regiões diferentes
- **Leads por setor**: Máximo 20 leads por setor

### Reset Automático
- **Contador diário**: Reset automático à meia-noite
- **Setores processados**: Reset quando todos os setores foram processados
- **Logs**: Mantidos para histórico

## 🔧 Manutenção

### Logs e Monitoramento

```bash
# Ver logs das campanhas
tail -f logs/daily_campaign.log

# Ver logs do cron
tail -f logs/cron.log

# Ver uso diário
cat data/daily_usage.json
```

### Troubleshooting

#### Problema: Cron não está executando
```bash
# Verificar cron jobs
crontab -l

# Verificar logs do sistema
sudo tail -f /var/log/syslog | grep CRON

# Testar execução manual
python scheduler/daily_campaign.py --run-now
```

#### Problema: Limite de emails atingido
```bash
# Verificar uso atual
python scripts/monitor_campaigns.py

# Aguardar reset automático à meia-noite
# Ou reset manual (não recomendado)
```

#### Problema: Setores não estão sendo processados
```bash
# Verificar configuração de setores
cat config/sectors.json

# Verificar filtros de leads
cat config/lead_filters.json
```

## 📝 Comandos Úteis

### Execução Manual
```bash
# Executar campanha agora
python scheduler/daily_campaign.py --run-now

# Executar com scheduler (modo contínuo)
python scheduler/daily_campaign.py
```

### Monitoramento
```bash
# Status básico
python scripts/monitor_campaigns.py

# Status completo
python scripts/monitor_campaigns.py --all

# Apenas logs
python scripts/monitor_campaigns.py --logs
```

### Configuração
```bash
# Configurar cron job
./scripts/setup_cron.sh

# Ver cron jobs ativos
crontab -l

# Editar cron jobs
crontab -e
```

## 🎯 Benefícios

### ✅ Vantagens do Sistema
- **Automatização completa**: Zero intervenção manual
- **Distribuição inteligente**: Cobertura equilibrada de setores
- **Controle de custos**: Respeita limites do SendGrid gratuito
- **Monitoramento**: Acompanhamento em tempo real
- **Escalabilidade**: Fácil adição de novos setores

### 📈 Resultados Esperados
- **100 emails/dia**: Máximo aproveitamento do plano gratuito
- **5 setores/dia**: Variedade de oportunidades
- **Rotação completa**: Todos os setores processados em 3 dias
- **Qualidade**: Apenas leads válidos e empresas reais

## 🔮 Próximos Passos

### Melhorias Futuras
- **Dashboard web**: Interface gráfica para monitoramento
- **Notificações**: Alertas por email/Slack
- **Métricas avançadas**: Taxa de resposta, conversões
- **Segmentação**: Campanhas específicas por região/setor
- **A/B testing**: Teste de diferentes abordagens de email 