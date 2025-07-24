import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional

logger = logging.getLogger(__name__)

class LeadManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.contacted_file = os.path.join(data_dir, "contacted_leads.json")
        self.blacklist_file = os.path.join(data_dir, "blacklist_leads.json")
        self.contacted_leads: Set[str] = set()
        self.blacklist_leads: Set[str] = set()
        self._load_contacted_leads()
        self._load_blacklist()
    
    def _load_contacted_leads(self):
        """Load contacted leads from file"""
        try:
            if os.path.exists(self.contacted_file):
                with open(self.contacted_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.contacted_leads = set(data.get('contacted_leads', []))
                    logger.info(f"Loaded {len(self.contacted_leads)} contacted leads")
            else:
                self._create_contacted_file()
        except Exception as e:
            logger.error(f"Error loading contacted leads: {e}")
            self.contacted_leads = set()
    
    def _load_blacklist(self):
        """Load blacklisted leads from file"""
        try:
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.blacklist_leads = set(data.get('blacklist_leads', []))
                    logger.info(f"Loaded {len(self.blacklist_leads)} blacklisted leads")
            else:
                self._create_blacklist_file()
        except Exception as e:
            logger.error(f"Error loading blacklist: {e}")
            self.blacklist_leads = set()
    
    def _create_contacted_file(self):
        """Create initial contacted leads file"""
        data = {
            "contacted_leads": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_contacted": 0
        }
        with open(self.contacted_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _create_blacklist_file(self):
        """Create initial blacklist file"""
        data = {
            "blacklist_leads": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_blacklisted": 0
        }
        with open(self.blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_contacted_leads(self):
        """Save contacted leads to file"""
        try:
            data = {
                "contacted_leads": list(self.contacted_leads),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_contacted": len(self.contacted_leads)
            }
            with open(self.contacted_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving contacted leads: {e}")
    
    def _save_blacklist(self):
        """Save blacklist to file"""
        try:
            data = {
                "blacklist_leads": list(self.blacklist_leads),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_blacklisted": len(self.blacklist_leads)
            }
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving blacklist: {e}")
    
    def is_contacted(self, lead_name: str) -> bool:
        """Check if a lead has been contacted"""
        return lead_name.lower().strip() in self.contacted_leads
    
    def is_blacklisted(self, lead_name: str) -> bool:
        """Check if a lead is blacklisted"""
        return lead_name.lower().strip() in self.blacklist_leads
    
    def mark_contacted(self, lead_name: str):
        """Mark a lead as contacted"""
        lead_name_clean = lead_name.lower().strip()
        if lead_name_clean not in self.contacted_leads:
            self.contacted_leads.add(lead_name_clean)
            self._save_contacted_leads()
            logger.info(f"Marked '{lead_name}' as contacted")
    
    def mark_blacklisted(self, lead_name: str, reason: str = "Manual blacklist"):
        """Mark a lead as blacklisted"""
        lead_name_clean = lead_name.lower().strip()
        if lead_name_clean not in self.blacklist_leads:
            self.blacklist_leads.add(lead_name_clean)
            self._save_blacklist()
            logger.info(f"Blacklisted '{lead_name}' - Reason: {reason}")
    
    def filter_new_leads(self, leads: List[Dict]) -> List[Dict]:
        """Filter out already contacted or blacklisted leads"""
        new_leads = []
        filtered_count = 0
        
        for lead in leads:
            lead_name = lead.get('name', '')
            if not lead_name:
                continue
                
            if self.is_contacted(lead_name):
                filtered_count += 1
                continue
                
            if self.is_blacklisted(lead_name):
                filtered_count += 1
                continue
                
            new_leads.append(lead)
        
        logger.info(f"Filtered {filtered_count} already contacted/blacklisted leads")
        logger.info(f"Found {len(new_leads)} new leads to contact")
        
        return new_leads
    
    def get_contacted_count(self) -> int:
        """Get total number of contacted leads"""
        return len(self.contacted_leads)
    
    def get_blacklisted_count(self) -> int:
        """Get total number of blacklisted leads"""
        return len(self.blacklist_leads)
    
    def get_stats(self) -> Dict:
        """Get lead management statistics"""
        return {
            "total_contacted": len(self.contacted_leads),
            "total_blacklisted": len(self.blacklist_leads),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        } 