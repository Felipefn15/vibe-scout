#!/usr/bin/env python3
"""
Monitor do Sistema no Railway
Monitora o status e logs do Vibe Scout no Railway
"""

import subprocess
import json
import time
from datetime import datetime
import sys

def get_railway_status():
    """Obtém o status do serviço no Railway"""
    try:
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Erro: {result.stderr}"
    except Exception as e:
        return f"Erro: {e}"

def get_railway_logs(lines: int = 50):
    """Obtém os logs do Railway"""
    try:
        result = subprocess.run(['railway', 'logs', '--lines', str(lines)], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Erro ao obter logs: {result.stderr}"
    except Exception as e:
        return f"Erro: {e}"

def get_service_url():
    """Obtém a URL do serviço"""
    try:
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception:
        return None

def parse_logs_for_events(logs: str):
    """Analisa logs para extrair eventos importantes"""
    events = {
        'campaigns': [],
        'emails_sent': 0,
        'errors': [],
        'warnings': []
    }
    
    lines = logs.split('\n')
    for line in lines:
        if 'campaign_start' in line:
            events['campaigns'].append({
                'type': 'start',
                'line': line
            })
        elif 'campaign_complete' in line:
            events['campaigns'].append({
                'type': 'complete',
                'line': line
            })
        elif 'email_sent' in line:
            events['emails_sent'] += 1
        elif 'ERROR' in line:
            events['errors'].append(line)
        elif 'WARNING' in line:
            events['warnings'].append(line)
    
    return events

def display_status():
    """Exibe o status do sistema"""
    print("🚂 Status do Railway")
    print("=" * 50)
    
    # Status do serviço
    status = get_railway_status()
    print("📊 Status do Serviço:")
    print(status)
    
    # URL do serviço
    url = get_service_url()
    if url:
        print(f"🌐 URL: {url}")
    
    print()

def display_logs(lines: int = 20):
    """Exibe os logs recentes"""
    print(f"📋 Logs Recentes (últimas {lines} linhas)")
    print("=" * 50)
    
    logs = get_railway_logs(lines)
    print(logs)
    print()

def display_events():
    """Exibe eventos importantes dos logs"""
    print("📈 Eventos Importantes")
    print("=" * 50)
    
    logs = get_railway_logs(100)
    events = parse_logs_for_events(logs)
    
    # Campanhas
    if events['campaigns']:
        print("🎯 Campanhas:")
        for campaign in events['campaigns'][-5:]:  # Últimas 5 campanhas
            print(f"  - {campaign['type']}: {campaign['line'][:100]}...")
    
    # Emails enviados
    if events['emails_sent'] > 0:
        print(f"📧 Emails enviados: {events['emails_sent']}")
    
    # Erros
    if events['errors']:
        print(f"❌ Erros ({len(events['errors'])}):")
        for error in events['errors'][-3:]:  # Últimos 3 erros
            print(f"  - {error[:100]}...")
    
    # Avisos
    if events['warnings']:
        print(f"⚠️ Avisos ({len(events['warnings'])}):")
        for warning in events['warnings'][-3:]:  # Últimos 3 avisos
            print(f"  - {warning[:100]}...")
    
    print()

def monitor_realtime():
    """Monitora em tempo real"""
    print("🔍 Monitoramento em Tempo Real")
    print("=" * 50)
    print("Pressione Ctrl+C para parar")
    print()
    
    try:
        while True:
            # Limpa a tela
            print("\033[2J\033[H")
            
            # Exibe timestamp
            print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Status
            display_status()
            
            # Logs recentes
            display_logs(10)
            
            # Aguarda 30 segundos
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoramento interrompido")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("🚂 Monitor do Vibe Scout no Railway")
        print("=" * 50)
        print("Uso:")
        print("  python scripts/monitor_railway.py status    # Status do serviço")
        print("  python scripts/monitor_railway.py logs      # Logs recentes")
        print("  python scripts/monitor_railway.py events    # Eventos importantes")
        print("  python scripts/monitor_railway.py realtime  # Monitoramento em tempo real")
        print("  python scripts/monitor_railway.py all       # Tudo")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        display_status()
    elif command == 'logs':
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        display_logs(lines)
    elif command == 'events':
        display_events()
    elif command == 'realtime':
        monitor_realtime()
    elif command == 'all':
        display_status()
        display_logs(30)
        display_events()
    else:
        print(f"❌ Comando desconhecido: {command}")

if __name__ == "__main__":
    main() 