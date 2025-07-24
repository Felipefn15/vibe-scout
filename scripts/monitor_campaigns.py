#!/usr/bin/env python3
"""
Campaign Monitor
Monitor the status of daily campaigns and email usage
"""

import os
import sys
import json
from datetime import datetime, timedelta
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_daily_usage():
    """Load daily usage data"""
    usage_file = 'data/daily_usage.json'
    try:
        with open(usage_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"date": "", "emails_sent": 0, "sectors_processed": []}

def load_sectors():
    """Load sectors configuration"""
    sectors_file = 'config/sectors.json'
    try:
        with open(sectors_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def check_logs():
    """Check recent log entries"""
    log_file = 'logs/daily_campaign.log'
    if not os.path.exists(log_file):
        return "No log file found"
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                # Get last 10 lines
                recent_lines = lines[-10:]
                return "".join(recent_lines)
            else:
                return "Log file is empty"
    except Exception as e:
        return f"Error reading log file: {e}"

def check_cron_logs():
    """Check cron job logs"""
    log_file = 'logs/cron.log'
    if not os.path.exists(log_file):
        return "No cron log file found"
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                # Get last 5 lines
                recent_lines = lines[-5:]
                return "".join(recent_lines)
            else:
                return "Cron log file is empty"
    except Exception as e:
        return f"Error reading cron log file: {e}"

def get_campaign_status():
    """Get current campaign status"""
    usage = load_daily_usage()
    sectors = load_sectors()
    
    today = datetime.now().strftime('%Y-%m-%d')
    is_today = usage.get('date') == today
    
    status = {
        "date": usage.get('date', 'Never'),
        "is_today": is_today,
        "emails_sent": usage.get('emails_sent', 0),
        "max_emails": 100,
        "sectors_processed": usage.get('sectors_processed', []),
        "total_sectors": len(sectors),
        "remaining_emails": max(0, 100 - usage.get('emails_sent', 0)),
        "progress_percentage": (usage.get('emails_sent', 0) / 100) * 100
    }
    
    return status

def print_status(status):
    """Print formatted status"""
    print("=== Vibe Scout Campaign Status ===")
    print(f"📅 Date: {status['date']}")
    print(f"📧 Emails Sent: {status['emails_sent']}/{status['max_emails']} ({status['progress_percentage']:.1f}%)")
    print(f"📊 Remaining: {status['remaining_emails']} emails")
    print(f"🏢 Sectors Processed: {len(status['sectors_processed'])}/{status['total_sectors']}")
    
    if status['sectors_processed']:
        print(f"✅ Processed: {', '.join(status['sectors_processed'])}")
    
    if status['is_today']:
        if status['emails_sent'] >= status['max_emails']:
            print("🎯 Status: Daily limit reached")
        elif status['emails_sent'] > 0:
            print("🔄 Status: Campaign in progress")
        else:
            print("⏰ Status: Waiting for campaign")
    else:
        print("📅 Status: No campaign today")

def print_logs(log_type='campaign'):
    """Print recent logs"""
    if log_type == 'campaign':
        print("\n=== Recent Campaign Logs ===")
        logs = check_logs()
    else:
        print("\n=== Recent Cron Logs ===")
        logs = check_cron_logs()
    
    print(logs)

def main():
    parser = argparse.ArgumentParser(description='Monitor Vibe Scout campaigns')
    parser.add_argument('--logs', action='store_true', help='Show recent logs')
    parser.add_argument('--cron-logs', action='store_true', help='Show cron logs')
    parser.add_argument('--all', action='store_true', help='Show status and all logs')
    
    args = parser.parse_args()
    
    # Always show status
    status = get_campaign_status()
    print_status(status)
    
    # Show logs if requested
    if args.logs or args.all:
        print_logs('campaign')
    
    if args.cron_logs or args.all:
        print_logs('cron')
    
    # Show usage tips
    if not args.logs and not args.cron_logs and not args.all:
        print("\n💡 Usage:")
        print("  python scripts/monitor_campaigns.py --logs     # Show campaign logs")
        print("  python scripts/monitor_campaigns.py --cron-logs # Show cron logs")
        print("  python scripts/monitor_campaigns.py --all       # Show everything")

if __name__ == "__main__":
    main() 