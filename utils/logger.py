#!/usr/bin/env python3
"""
Sistema de Logs Centralizado - Vibe Scout
Logs estruturados para monitoramento no Railway
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class VibeScoutLogger:
    def __init__(self, name: str = "vibe_scout"):
        self.name = name
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger com múltiplos handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Evita duplicação de handlers
        if logger.handlers:
            return logger
        
        # Formato estruturado para Railway
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para console (Railway logs)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para arquivo de logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "vibe_scout.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log de informação com dados extras"""
        if extra:
            message = f"{message} | {json.dumps(extra, ensure_ascii=False)}"
        self.logger.info(message)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log de aviso com dados extras"""
        if extra:
            message = f"{message} | {json.dumps(extra, ensure_ascii=False)}"
        self.logger.warning(message)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log de erro com dados extras"""
        if extra:
            message = f"{message} | {json.dumps(extra, ensure_ascii=False)}"
        self.logger.error(message)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log de debug com dados extras"""
        if extra:
            message = f"{message} | {json.dumps(extra, ensure_ascii=False)}"
        self.logger.debug(message)
    
    def campaign_start(self, sectors: list, regions: list, max_emails: int):
        """Log de início de campanha"""
        self.info("🚀 Campanha iniciada", {
            "event": "campaign_start",
            "sectors": sectors,
            "regions": regions,
            "max_emails": max_emails,
            "timestamp": datetime.now().isoformat()
        })
    
    def campaign_complete(self, total_emails: int, sectors_processed: list, duration: float):
        """Log de conclusão de campanha"""
        self.info("✅ Campanha concluída", {
            "event": "campaign_complete",
            "total_emails": total_emails,
            "sectors_processed": sectors_processed,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now().isoformat()
        })
    
    def sector_start(self, sector: str, region: str):
        """Log de início de processamento de setor"""
        self.info(f"🏢 Processando setor: {sector} - {region}", {
            "event": "sector_start",
            "sector": sector,
            "region": region,
            "timestamp": datetime.now().isoformat()
        })
    
    def sector_complete(self, sector: str, region: str, leads_found: int, emails_sent: int):
        """Log de conclusão de setor"""
        self.info(f"✅ Setor concluído: {sector} - {region}", {
            "event": "sector_complete",
            "sector": sector,
            "region": region,
            "leads_found": leads_found,
            "emails_sent": emails_sent,
            "timestamp": datetime.now().isoformat()
        })
    
    def lead_collected(self, lead_name: str, sector: str, region: str):
        """Log de lead coletado"""
        self.info(f"🎯 Lead coletado: {lead_name}", {
            "event": "lead_collected",
            "lead_name": lead_name,
            "sector": sector,
            "region": region,
            "timestamp": datetime.now().isoformat()
        })
    
    def email_sent(self, lead_name: str, email: str, sector: str):
        """Log de email enviado"""
        self.info(f"📧 Email enviado: {lead_name}", {
            "event": "email_sent",
            "lead_name": lead_name,
            "email": email,
            "sector": sector,
            "timestamp": datetime.now().isoformat()
        })
    
    def email_failed(self, lead_name: str, email: str, error: str):
        """Log de falha no envio de email"""
        self.error(f"❌ Falha no envio: {lead_name}", {
            "event": "email_failed",
            "lead_name": lead_name,
            "email": email,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def api_limit_reached(self, service: str, limit: int):
        """Log de limite de API atingido"""
        self.warning(f"⚠️ Limite atingido: {service}", {
            "event": "api_limit_reached",
            "service": service,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        })
    
    def system_health(self, memory_usage: float, cpu_usage: float, disk_usage: float):
        """Log de saúde do sistema"""
        self.info("💚 Saúde do sistema", {
            "event": "system_health",
            "memory_usage_mb": round(memory_usage, 2),
            "cpu_usage_percent": round(cpu_usage, 2),
            "disk_usage_percent": round(disk_usage, 2),
            "timestamp": datetime.now().isoformat()
        })

# Instância global do logger
vibe_logger = VibeScoutLogger()

def get_logger(name: str = None) -> VibeScoutLogger:
    """Retorna uma instância do logger"""
    if name:
        return VibeScoutLogger(name)
    return vibe_logger 