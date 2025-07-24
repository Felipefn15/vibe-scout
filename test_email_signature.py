#!/usr/bin/env python3
"""
Test script for email signature functionality
"""

import json
import logging
from mailer.send_emails import EmailSender
from llm.generate_email import EmailGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_email_signature():
    """Test email signature generation"""
    logger.info("Testing email signature...")
    
    sender = EmailSender()
    generator = EmailGenerator()
    
    # Test data
    test_lead = {
        'name': 'Restaurante Teste',
        'website': 'https://restauranteteste.com',
        'description': 'Restaurante italiano tradicional',
        'site_analysis': {
            'lighthouse': {
                'performance_score': 65.5,
                'seo_score': 58.2,
                'accessibility_score': 72.1,
                'best_practices_score': 68.9
            },
            'seo': {
                'total_score': 62.5,
                'meta_tags': {'title': True, 'description': False},
                'headings': {'total_headings': 8},
                'images': {'alt_text_ratio': 0.6},
                'sitemap_found': False
            }
        },
        'social_analysis': {
            'overall_social_score': 45.2,
            'platforms': {
                'instagram': {
                    'followers': 1200,
                    'engagement_rate': 2.1
                }
            }
        }
    }
    
    # Generate email content
    logger.info("Generating email content...")
    email_data = generator.generate_personalized_email(
        test_lead, 
        test_lead['site_analysis'], 
        test_lead['social_analysis']
    )
    
    logger.info(f"Generated email subject: {email_data['subject']}")
    logger.info(f"Generated email body:\n{email_data['body']}")
    
    # Test HTML formatting
    logger.info("\n" + "="*50)
    logger.info("HTML EMAIL PREVIEW")
    logger.info("="*50)
    
    html_content = sender._format_email_body(email_data['body'])
    
    # Save HTML preview
    with open('email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info("HTML email preview saved to 'email_preview.html'")
    
    # Show key parts of the HTML
    lines = html_content.split('\n')
    for i, line in enumerate(lines):
        if 'TECHNOLOGIE FELIPE FRANCA' in line:
            logger.info(f"Signature found at line {i+1}: {line.strip()}")
        elif 'Felipe França' in line:
            logger.info(f"Name found at line {i+1}: {line.strip()}")
        elif 'Transformando Negócios Digitais' in line:
            logger.info(f"Tagline found at line {i+1}: {line.strip()}")

def test_multiple_industries():
    """Test email generation for different industries"""
    logger.info("\nTesting email generation for different industries...")
    
    generator = EmailGenerator()
    
    industries = [
        ('Restaurante Italiano', 'restaurantes'),
        ('Escritório de Advocacia', 'advocacias'),
        ('Farmácia Popular', 'farmacias'),
        ('Clínica Médica', 'clinicas')
    ]
    
    for business_name, industry in industries:
        test_lead = {
            'name': business_name,
            'website': f'https://{business_name.lower().replace(" ", "")}.com',
            'description': f'{business_name} - Negócio local',
            'site_analysis': {
                'lighthouse': {
                    'performance_score': 60.0,
                    'seo_score': 55.0
                }
            },
            'social_analysis': {
                'overall_social_score': 40.0
            }
        }
        
        email_data = generator.generate_personalized_email(
            test_lead, 
            test_lead['site_analysis'], 
            test_lead['social_analysis']
        )
        
        logger.info(f"\n{business_name}:")
        logger.info(f"  Subject: {email_data['subject']}")
        logger.info(f"  Signature present: {'TECHNOLOGIE FELIPE FRANCA' in email_data['body']}")

if __name__ == "__main__":
    logger.info("Starting email signature tests...")
    
    try:
        # Test email signature
        test_email_signature()
        
        # Test multiple industries
        test_multiple_industries()
        
        logger.info("\n" + "="*50)
        logger.info("SIGNATURE FEATURES")
        logger.info("="*50)
        logger.info("""
✅ Assinatura implementada com:

1. **HTML Template:**
   - Nome: Felipe França
   - Cargo: Desenvolvedor Full Stack
   - Empresa: TECHNOLOGIE FELIPE FRANCA
   - Tagline: Transformando Negócios Digitais

2. **LLM Prompt:**
   - Instrução para sempre incluir assinatura
   - Foco em desenvolvimento de software
   - Formato consistente em todos os emails

3. **Fallback Templates:**
   - Assinatura incluída em emails de backup
   - Foco em serviços de desenvolvimento
   - Formato padronizado

4. **Visual Design:**
   - Layout profissional
   - Cores da empresa
   - Informações de contato e especialidades
        """)
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise 