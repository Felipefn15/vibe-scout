#!/usr/bin/env python3
"""
Test script for email tagging and organization
"""

import json
import logging
from mailer.send_emails import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_email_headers():
    """Test email header generation"""
    logger.info("Testing email header generation...")
    
    sender = EmailSender()
    
    # Test campaign ID generation
    campaign_id = sender._generate_campaign_id("restaurantes", "Rio de Janeiro")
    logger.info(f"Generated campaign ID: {campaign_id}")
    
    # Test with different industries
    test_cases = [
        ("advocacias", "São Paulo"),
        ("farmacias", "Belo Horizonte"),
        ("clinicas", "Salvador"),
        ("academias", "Brasília")
    ]
    
    for industry, region in test_cases:
        campaign_id = sender._generate_campaign_id(industry, region)
        logger.info(f"{industry} in {region}: {campaign_id}")

def test_lead_outreach_email():
    """Test lead outreach email with headers"""
    logger.info("Testing lead outreach email...")
    
    sender = EmailSender()
    
    test_email_data = {
        'lead_id': 'Restaurante Teste',
        'subject': 'Melhorias Digitais para seu Negócio',
        'body': 'Olá! Identificamos oportunidades de melhoria...',
        'industry': 'restaurantes',
        'region': 'Rio de Janeiro',
        'personalization_score': 85
    }
    
    # This will test the header generation (won't actually send in test mode)
    result = sender.send_personalized_email(test_email_data, "test@example.com")
    logger.info(f"Email result: {result}")

def test_campaign_summary_email():
    """Test campaign summary email with headers"""
    logger.info("Testing campaign summary email...")
    
    sender = EmailSender()
    
    test_campaign_results = {
        'total_emails': 5,
        'sent_count': 4,
        'failed_count': 1,
        'sent_emails': [
            {
                'lead_id': 'Restaurante 1',
                'email': 'test1@example.com',
                'subject': 'Melhorias Digitais',
                'personalization_score': 85,
                'status': 'sent'
            },
            {
                'lead_id': 'Restaurante 2',
                'email': 'test2@example.com',
                'subject': 'Oportunidade Digital',
                'personalization_score': 78,
                'status': 'sent'
            }
        ],
        'failed_emails': [
            {
                'lead_id': 'Restaurante 3',
                'error_message': 'Invalid email address'
            }
        ],
        'industry': 'restaurantes',
        'region': 'Rio de Janeiro',
        'campaign_date': '2025-01-23 14:30:00'
    }
    
    # This will test the header generation (won't actually send in test mode)
    result = sender.send_summary_to_consultant(test_campaign_results, test_mode=True)
    logger.info(f"Summary email result: {result}")

def test_email_organization_rules():
    """Test email organization rules"""
    logger.info("Testing email organization rules...")
    
    # Define organization rules based on headers
    organization_rules = {
        "campaign_summary": {
            "folder": "Vibe Scout/Reports",
            "priority": "high",
            "tags": ["vibe-scout", "report", "campaign-summary"],
            "auto_archive": False
        },
        "lead_outreach": {
            "folder": "Vibe Scout/Prospecting",
            "priority": "normal",
            "tags": ["vibe-scout", "prospecting", "lead-outreach"],
            "auto_archive": True
        }
    }
    
    # Test different email types
    email_types = ["campaign_summary", "lead_outreach"]
    
    for email_type in email_types:
        rules = organization_rules[email_type]
        logger.info(f"\nEmail Type: {email_type}")
        logger.info(f"  Folder: {rules['folder']}")
        logger.info(f"  Priority: {rules['priority']}")
        logger.info(f"  Tags: {', '.join(rules['tags'])}")
        logger.info(f"  Auto Archive: {rules['auto_archive']}")

if __name__ == "__main__":
    logger.info("Starting email tagging tests...")
    
    try:
        # Test header generation
        test_email_headers()
        
        # Test lead outreach email
        test_lead_outreach_email()
        
        # Test campaign summary email
        test_campaign_summary_email()
        
        # Test organization rules
        test_email_organization_rules()
        
        logger.info("\n" + "="*50)
        logger.info("EMAIL ORGANIZATION GUIDE")
        logger.info("="*50)
        logger.info("""
Para configurar filtros automáticos no seu email:

1. **Gmail/Google Workspace:**
   - Criar filtro baseado em "X-Campaign-Type: campaign_summary"
   - Aplicar label "Vibe Scout/Reports"
   - Marcar como importante

2. **Outlook/Microsoft 365:**
   - Criar regra baseada em "X-Campaign-Type: campaign_summary"
   - Mover para pasta "Vibe Scout/Reports"
   - Definir prioridade alta

3. **Apple Mail:**
   - Criar regra inteligente baseada em "X-Campaign-Type: campaign_summary"
   - Mover para pasta "Vibe Scout/Reports"

4. **Headers disponíveis:**
   - X-Campaign-Type: campaign_summary | lead_outreach
   - X-Campaign-ID: VS_REST_RJ_20250123_143000
   - X-Industry: restaurantes | advocacias | farmacias
   - X-Priority: high | normal
   - X-Category: reports | prospecting
   - X-Tags: vibe-scout,report,campaign-summary
        """)
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise 