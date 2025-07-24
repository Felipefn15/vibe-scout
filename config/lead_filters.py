#!/usr/bin/env python3
"""
Lead Filters Configuration
Loads and applies lead filtering rules from JSON configuration
"""

import json
import os
import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class LeadFilters:
    """Lead filtering system"""
    
    def __init__(self, config_path: str = "config/lead_filters.json"):
        """Initialize lead filters from configuration file"""
        self.config_path = config_path
        self.filters = self._load_filters()
        
    def _load_filters(self) -> Dict:
        """Load filters from JSON configuration"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Lead filters config not found: {self.config_path}")
                return self._get_default_filters()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                filters = json.load(f)
            
            logger.info(f"Loaded lead filters from {self.config_path}")
            return filters
            
        except Exception as e:
            logger.error(f"Error loading lead filters: {e}")
            return self._get_default_filters()
    
    def _get_default_filters(self) -> Dict:
        """Get default filters if config file is not available"""
        return {
            "invalid_keywords": [
                "wikipedia", "wiki", "youtube", "facebook", "instagram", "twitter",
                "linkedin", "google", "maps", "search", "resultado", "resultados",
                "glassdoor", "indeed", "monster", "vagas", "emprego", "carreira",
                "salário", "salario", "trabalho", "job", "career", "salary",
                "melhores empresas", "top empresas", "ranking", "lista",
                "como consultar", "passo a passo", "guia", "tutorial",
                "estácio", "universidade", "faculdade", "curso", "educação",
                "blog", "artigo", "notícia", "noticia", "reportagem"
            ],
            "invalid_domains": [
                "wikipedia.org", "wikipedia.com", "wikimedia.org",
                "youtube.com", "youtu.be", "facebook.com", "fb.com",
                "instagram.com", "twitter.com", "x.com", "linkedin.com",
                "google.com", "google.com.br", "maps.google.com",
                "glassdoor.com", "glassdoor.com.br", "indeed.com",
                "monster.com", "vagas.com", "empregos.com"
            ],
            "valid_business_patterns": [
                "advocacia", "advogados", "escritório", "escritorio",
                "restaurante", "pizzaria", "churrascaria", "padaria",
                "farmácia", "farmacia", "drogaria", "clínica", "clinica",
                "academia", "ginástica", "ginastica", "fitness",
                "salão", "salao", "beleza", "estética", "estetica",
                "imobiliária", "imobiliaria", "imóveis", "imoveis",
                "consultoria", "assessoria", "empresarial", "consultorio"
            ],
            "minimum_name_length": 3,
            "required_fields": ["name"],
            "optional_fields": ["website", "email", "phone", "address", "description"]
        }
    
    def is_valid_business(self, lead_name: str) -> bool:
        """Check if a lead name represents a valid business"""
        if not lead_name or not isinstance(lead_name, str):
            return False
        
        # Convert to lowercase for case-insensitive matching
        lead_lower = lead_name.lower().strip()
        
        # Check minimum length
        if len(lead_lower) < self.filters.get("minimum_name_length", 3):
            logger.debug(f"Lead too short: {lead_name}")
            return False
        
        # Check for invalid keywords
        invalid_keywords = self.filters.get("invalid_keywords", [])
        for keyword in invalid_keywords:
            if keyword.lower() in lead_lower:
                logger.debug(f"Lead contains invalid keyword '{keyword}': {lead_name}")
                return False
        
        # Check for valid business patterns
        valid_patterns = self.filters.get("valid_business_patterns", [])
        has_valid_pattern = False
        for pattern in valid_patterns:
            if pattern.lower() in lead_lower:
                has_valid_pattern = True
                break
        
        if not has_valid_pattern:
            logger.debug(f"Lead doesn't match valid business patterns: {lead_name}")
            return False
        
        # Additional checks for common invalid patterns
        invalid_patterns = [
            r'\b(os|as)\s+\d+\b',  # "os 10", "as 5"
            r'\b(top|melhores)\s+\d+\b',  # "top 10", "melhores 5"
            r'\b(ranking|lista|classificação)\b',  # ranking, lista
            r'\b(como|passo\s+a\s+passo|tutorial|guia)\b',  # how-to content
            r'\b(análise|estudo|pesquisa|reportagem)\b',  # analysis content
            r'\b(notícia|artigo|blog|post)\b',  # news/article content
            r'\b(fórum|comunidade|grupo|discussão)\b',  # forum content
            r'\b(avaliação|review|crítica|comparacao)\b',  # review content
            r'\b(preço|valor|custo|orçamento|salário)\b',  # price/salary content
            r'\b(vagas|emprego|carreira|trabalho|job)\b',  # job content
            r'\b(universidade|faculdade|escola|curso|educação)\b',  # education content
            r'\b(estudante|aluno|professor|acadêmico)\b'  # academic content
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, lead_lower, re.IGNORECASE):
                logger.debug(f"Lead matches invalid pattern '{pattern}': {lead_name}")
                return False
        
        logger.debug(f"Lead passed all filters: {lead_name}")
        return True
    
    def filter_leads(self, leads: List[Dict]) -> List[Dict]:
        """Filter a list of leads"""
        if not leads:
            return []
        
        filtered_leads = []
        total_leads = len(leads)
        
        for lead in leads:
            lead_name = lead.get('name', '')
            if self.is_valid_business(lead_name):
                filtered_leads.append(lead)
            else:
                logger.info(f"Filtered out invalid lead: {lead_name}")
        
        filtered_count = len(filtered_leads)
        logger.info(f"Filtered {total_leads - filtered_count}/{total_leads} leads ({filtered_count} remaining)")
        
        return filtered_leads
    
    def get_filter_stats(self) -> Dict:
        """Get statistics about the current filters"""
        return {
            "invalid_keywords_count": len(self.filters.get("invalid_keywords", [])),
            "invalid_domains_count": len(self.filters.get("invalid_domains", [])),
            "valid_patterns_count": len(self.filters.get("valid_business_patterns", [])),
            "minimum_name_length": self.filters.get("minimum_name_length", 3),
            "config_path": self.config_path
        } 