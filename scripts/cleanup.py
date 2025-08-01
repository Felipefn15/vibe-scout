#!/usr/bin/env python3
"""
Script de Limpeza do Vibe Scout
Remove arquivos temporários e organiza o projeto
"""

import os
import shutil
import glob
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectCleaner:
    """Classe para limpeza e organização do projeto"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
    def cleanup_pycache(self):
        """Remove diretórios __pycache__"""
        logger.info("Removendo diretórios __pycache__...")
        
        for pycache_dir in self.project_root.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache_dir)
                logger.info(f"Removido: {pycache_dir}")
            except Exception as e:
                logger.error(f"Erro ao remover {pycache_dir}: {e}")
    
    def cleanup_logs(self, days_old: int = 7):
        """Remove logs antigos"""
        logger.info(f"Removendo logs mais antigos que {days_old} dias...")
        
        logs_dir = self.project_root / "logs"
        if not logs_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for log_file in logs_dir.glob("*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    logger.info(f"Removido log antigo: {log_file}")
            except Exception as e:
                logger.error(f"Erro ao processar {log_file}: {e}")
    
    def cleanup_temp_files(self):
        """Remove arquivos temporários"""
        logger.info("Removendo arquivos temporários...")
        
        # Padrões de arquivos temporários
        temp_patterns = [
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                try:
                    temp_file.unlink()
                    logger.info(f"Removido arquivo temporário: {temp_file}")
                except Exception as e:
                    logger.error(f"Erro ao remover {temp_file}: {e}")
    
    def cleanup_screenshots(self, days_old: int = 1):
        """Remove screenshots antigos"""
        logger.info(f"Removendo screenshots mais antigos que {days_old} dias...")
        
        screenshots_dir = self.project_root / "debug_screenshots"
        if not screenshots_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for screenshot in screenshots_dir.glob("*.png"):
            try:
                file_time = datetime.fromtimestamp(screenshot.stat().st_mtime)
                if file_time < cutoff_date:
                    screenshot.unlink()
                    logger.info(f"Removido screenshot antigo: {screenshot}")
            except Exception as e:
                logger.error(f"Erro ao processar {screenshot}: {e}")
    
    def cleanup_data_backups(self, keep_days: int = 30):
        """Remove backups de dados antigos"""
        logger.info(f"Mantendo apenas backups dos últimos {keep_days} dias...")
        
        data_dir = self.project_root / "data"
        if not data_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Padrão para arquivos de backup com timestamp
        backup_pattern = "*_backup_*.json"
        
        for backup_file in data_dir.glob(backup_pattern):
            try:
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Removido backup antigo: {backup_file}")
            except Exception as e:
                logger.error(f"Erro ao processar {backup_file}: {e}")
    
    def organize_data_files(self):
        """Organiza arquivos de dados por data"""
        logger.info("Organizando arquivos de dados...")
        
        data_dir = self.project_root / "data"
        if not data_dir.exists():
            return
        
        # Criar diretórios por mês
        for data_file in data_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(data_file.stat().st_mtime)
                month_dir = data_dir / f"{file_time.year:04d}_{file_time.month:02d}"
                month_dir.mkdir(exist_ok=True)
                
                # Mover arquivo para diretório do mês
                if data_file.parent != month_dir:
                    shutil.move(str(data_file), str(month_dir / data_file.name))
                    logger.info(f"Movido: {data_file} -> {month_dir}")
            except Exception as e:
                logger.error(f"Erro ao organizar {data_file}: {e}")
    
    def cleanup_empty_dirs(self):
        """Remove diretórios vazios"""
        logger.info("Removendo diretórios vazios...")
        
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        logger.info(f"Removido diretório vazio: {dir_path}")
                except Exception as e:
                    logger.error(f"Erro ao remover diretório {dir_path}: {e}")
    
    def create_backup(self):
        """Cria backup dos dados importantes"""
        logger.info("Criando backup dos dados...")
        
        data_dir = self.project_root / "data"
        if not data_dir.exists():
            return
        
        backup_dir = self.project_root / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"data_backup_{timestamp}"
        backup_path = backup_dir / backup_name
        
        try:
            shutil.copytree(data_dir, backup_path)
            logger.info(f"Backup criado: {backup_path}")
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
    
    def run_full_cleanup(self, backup: bool = True):
        """Executa limpeza completa do projeto"""
        logger.info("Iniciando limpeza completa do projeto...")
        
        if backup:
            self.create_backup()
        
        self.cleanup_pycache()
        self.cleanup_logs()
        self.cleanup_temp_files()
        self.cleanup_screenshots()
        self.cleanup_data_backups()
        self.organize_data_files()
        self.cleanup_empty_dirs()
        
        logger.info("Limpeza completa finalizada!")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Limpeza do projeto Vibe Scout")
    parser.add_argument("--backup", action="store_true", help="Criar backup antes da limpeza")
    parser.add_argument("--logs-days", type=int, default=7, help="Dias para manter logs")
    parser.add_argument("--screenshots-days", type=int, default=1, help="Dias para manter screenshots")
    parser.add_argument("--backup-days", type=int, default=30, help="Dias para manter backups")
    
    args = parser.parse_args()
    
    cleaner = ProjectCleaner()
    
    # Executar limpeza
    cleaner.run_full_cleanup(backup=args.backup)
    
    logger.info("Limpeza concluída com sucesso!")

if __name__ == "__main__":
    main() 