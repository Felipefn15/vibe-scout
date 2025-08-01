#!/usr/bin/env python3
"""
Vibe Scout - Optimized Lead Generation Pipeline
Enhanced pipeline with LLM-powered intelligence for better lead identification and email generation
"""

import os
import sys
import logging
import json
import argparse
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/vibe_scout_optimized.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def run_optimized_pipeline(sector: str, region: str, 
                               min_intelligence_score: int = 70,
                               max_leads: int = 50,
                               include_website_analysis: bool = True,
                               include_social_analysis: bool = True,
                               test_mode: bool = False):
    """
    Run the optimized Vibe Scout pipeline with LLM-powered intelligence
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting optimized pipeline for {sector} in {region}")
        logger.info(f"Min intelligence score: {min_intelligence_score}")
        logger.info(f"Max leads: {max_leads}")
        logger.info(f"Test mode: {test_mode}")
        
        # Import optimized modules
        from scraper.enhanced_collector import EnhancedLeadCollector
        from llm.enhanced_email_generator import EnhancedEmailGenerator
        from email_sender.sendgrid_sender import SendGridSender
        
        # Initialize components
        async with EnhancedLeadCollector() as collector:
            email_generator = EnhancedEmailGenerator()
            email_sender = SendGridSender()
            
            # 1. Collect intelligent leads
            logger.info("Step 1: Collecting intelligent leads...")
            leads = await collector.collect_intelligent_leads(
                sector=sector,
                region=region,
                min_intelligence_score=min_intelligence_score,
                max_leads=max_leads,
                include_website_analysis=include_website_analysis,
                include_social_analysis=include_social_analysis
            )
            
            if not leads:
                logger.warning("No high-quality leads collected")
                return {
                    'success': False,
                    'message': 'No high-quality leads found',
                    'leads_count': 0,
                    'emails_generated': 0,
                    'emails_sent': 0
                }
            
            logger.info(f"Collected {len(leads)} high-quality leads")
            
            # 2. Generate intelligent emails
            logger.info("Step 2: Generating intelligent emails...")
            
            # Prepare data for email generation
            lead_data_list = []
            website_analyses = []
            social_analyses = []
            ai_analyses = []
            
            for lead in leads:
                lead_data_list.append(lead)
                website_analyses.append(lead.get('website_analysis', {}))
                social_analyses.append(lead.get('social_analysis', {}))
                ai_analyses.append(lead.get('ai_analysis', {}))
            
            # Generate emails
            emails = await email_generator.generate_bulk_intelligent_emails(
                lead_data_list, website_analyses, social_analyses, ai_analyses
            )
            
            logger.info(f"Generated {len(emails)} intelligent emails")
            
            # 3. Send emails (if not in test mode)
            emails_sent = 0
            if not test_mode:
                logger.info("Step 3: Sending emails...")
                
                for email in emails:
                    try:
                        # Extract email data
                        to_email = email.get('lead_email', '')
                        if not to_email:
                            logger.warning(f"No email address for {email.get('lead_name', 'Unknown')}")
                            continue
                        
                        subject = email.get('subject', 'Oportunidade de Melhoria Digital')
                        body = email.get('body', '')
                        
                        # Send email
                        success = await email_sender.send_email(
                            to_email=to_email,
                            subject=subject,
                            body=body
                        )
                        
                        if success:
                            emails_sent += 1
                            logger.info(f"Email sent to {email.get('lead_name', 'Unknown')}")
                        else:
                            logger.warning(f"Failed to send email to {email.get('lead_name', 'Unknown')}")
                    
                    except Exception as e:
                        logger.error(f"Error sending email to {email.get('lead_name', 'Unknown')}: {e}")
            else:
                logger.info("Test mode: Skipping email sending")
            
            # 4. Save results
            logger.info("Step 4: Saving results...")
            
            # Save leads with AI analysis
            with open('data/intelligent_leads.json', 'w', encoding='utf-8') as f:
                json.dump(leads, f, indent=2, ensure_ascii=False)
            
            # Save generated emails
            with open('data/intelligent_emails.json', 'w', encoding='utf-8') as f:
                json.dump(emails, f, indent=2, ensure_ascii=False)
            
            # Save statistics
            pipeline_stats = {
                'pipeline_execution_time': time.time() - start_time,
                'sector': sector,
                'region': region,
                'min_intelligence_score': min_intelligence_score,
                'max_leads': max_leads,
                'test_mode': test_mode,
                'collection_stats': collector.get_collection_stats(),
                'email_generation_stats': email_generator.get_generation_stats(),
                'llm_stats': {
                    'collector_llm': collector.get_llm_stats(),
                    'email_generator_llm': email_generator.get_llm_stats()
                },
                'results': {
                    'leads_collected': len(leads),
                    'emails_generated': len(emails),
                    'emails_sent': emails_sent,
                    'high_quality_leads': len([lead for lead in leads if lead.get('intelligence_score', 0) >= 80]),
                    'average_intelligence_score': sum(lead.get('intelligence_score', 0) for lead in leads) / len(leads) if leads else 0,
                    'average_personalization_score': email_generator.get_generation_stats().get('average_personalization_score', 0)
                }
            }
            
            with open('data/pipeline_stats.json', 'w', encoding='utf-8') as f:
                json.dump(pipeline_stats, f, indent=2, ensure_ascii=False)
            
            # 5. Generate report
            logger.info("Step 5: Generating report...")
            report = generate_optimized_report(pipeline_stats, leads, emails)
            
            with open('data/optimized_pipeline_report.md', 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info("Optimized pipeline completed successfully!")
            logger.info(f"Pipeline statistics: {json.dumps(pipeline_stats['results'], indent=2)}")
            
            return {
                'success': True,
                'leads_count': len(leads),
                'emails_generated': len(emails),
                'emails_sent': emails_sent,
                'pipeline_stats': pipeline_stats
            }
            
    except Exception as e:
        logger.error(f"Error in optimized pipeline: {e}")
        return {
            'success': False,
            'error': str(e),
            'leads_count': 0,
            'emails_generated': 0,
            'emails_sent': 0
        }

def generate_optimized_report(pipeline_stats: dict, leads: list, emails: list) -> str:
    """Generate comprehensive report for the optimized pipeline"""
    
    report = f"""# Vibe Scout - Relatório de Pipeline Otimizado

## Resumo Executivo

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Setor:** {pipeline_stats['sector']}
**Região:** {pipeline_stats['region']}
**Modo de Teste:** {'Sim' if pipeline_stats['test_mode'] else 'Não'}

## Métricas Principais

- **Leads Coletados:** {pipeline_stats['results']['leads_collected']}
- **Emails Gerados:** {pipeline_stats['results']['emails_generated']}
- **Emails Enviados:** {pipeline_stats['results']['emails_sent']}
- **Leads de Alta Qualidade:** {pipeline_stats['results']['high_quality_leads']}
- **Score Médio de Inteligência:** {pipeline_stats['results']['average_intelligence_score']:.1f}/100
- **Score Médio de Personalização:** {pipeline_stats['results']['average_personalization_score']:.1f}/100

## Performance do Pipeline

- **Tempo Total de Execução:** {pipeline_stats['pipeline_execution_time']:.2f} segundos
- **Tempo de Coleta:** {pipeline_stats['collection_stats']['collection_time']:.2f} segundos
- **Tempo de Análise LLM:** {pipeline_stats['collection_stats']['llm_analysis_time']:.2f} segundos
- **Tempo de Geração de Emails:** {pipeline_stats['email_generation_stats']['generation_time']:.2f} segundos

## Análise de Leads

### Distribuição por Score de Inteligência

"""
    
    # Analyze intelligence score distribution
    score_ranges = {
        'Alta (80-100)': 0,
        'Média-Alta (70-79)': 0,
        'Média (60-69)': 0,
        'Baixa (0-59)': 0
    }
    
    for lead in leads:
        score = lead.get('intelligence_score', 0)
        if score >= 80:
            score_ranges['Alta (80-100)'] += 1
        elif score >= 70:
            score_ranges['Média-Alta (70-79)'] += 1
        elif score >= 60:
            score_ranges['Média (60-69)'] += 1
        else:
            score_ranges['Baixa (0-59)'] += 1
    
    for range_name, count in score_ranges.items():
        percentage = (count / len(leads) * 100) if leads else 0
        report += f"- **{range_name}:** {count} leads ({percentage:.1f}%)\n"
    
    report += f"""
### Top 10 Leads por Score de Inteligência

"""
    
    # Sort leads by intelligence score
    sorted_leads = sorted(leads, key=lambda x: x.get('intelligence_score', 0), reverse=True)
    
    for i, lead in enumerate(sorted_leads[:10]):
        name = lead.get('name', 'Unknown')
        score = lead.get('intelligence_score', 0)
        sector = lead.get('sector', 'Unknown')
        website = lead.get('website', 'N/A')
        
        report += f"{i+1}. **{name}** - Score: {score}/100 - Setor: {sector} - Website: {website}\n"
    
    report += f"""
## Análise de Emails

### Distribuição por Score de Personalização

"""
    
    # Analyze personalization score distribution
    personalization_ranges = {
        'Excelente (90-100)': 0,
        'Muito Boa (80-89)': 0,
        'Boa (70-79)': 0,
        'Média (60-69)': 0,
        'Baixa (0-59)': 0
    }
    
    for email in emails:
        score = email.get('personalization_score', 0)
        if score >= 90:
            personalization_ranges['Excelente (90-100)'] += 1
        elif score >= 80:
            personalization_ranges['Muito Boa (80-89)'] += 1
        elif score >= 70:
            personalization_ranges['Boa (70-79)'] += 1
        elif score >= 60:
            personalization_ranges['Média (60-69)'] += 1
        else:
            personalization_ranges['Baixa (0-59)'] += 1
    
    for range_name, count in personalization_ranges.items():
        percentage = (count / len(emails) * 100) if emails else 0
        report += f"- **{range_name}:** {count} emails ({percentage:.1f}%)\n"
    
    report += f"""
### Estratégias de Email Utilizadas

"""
    
    # Analyze email strategies
    strategies = {}
    for email in emails:
        strategy = email.get('strategy_used', 'unknown')
        strategies[strategy] = strategies.get(strategy, 0) + 1
    
    for strategy, count in strategies.items():
        percentage = (count / len(emails) * 100) if emails else 0
        report += f"- **{strategy}:** {count} emails ({percentage:.1f}%)\n"
    
    report += f"""
## Estatísticas LLM

### Coletor de Leads
- **Chamadas LLM:** {pipeline_stats['llm_stats']['collector_llm'].get('total_calls', 0)}
- **Tempo Médio de Resposta:** {pipeline_stats['llm_stats']['collector_llm'].get('average_latency', 0):.2f}s
- **Taxa de Sucesso:** {pipeline_stats['llm_stats']['collector_llm'].get('success_rate', 0):.1f}%

### Gerador de Emails
- **Chamadas LLM:** {pipeline_stats['llm_stats']['email_generator_llm'].get('total_calls', 0)}
- **Tempo Médio de Resposta:** {pipeline_stats['llm_stats']['email_generator_llm'].get('average_latency', 0):.2f}s
- **Taxa de Sucesso:** {pipeline_stats['llm_stats']['email_generator_llm'].get('success_rate', 0):.1f}%

## Recomendações

### Para Melhorar a Qualidade dos Leads
"""
    
    # Generate recommendations based on results
    if pipeline_stats['results']['average_intelligence_score'] < 70:
        report += "- Considerar aumentar o score mínimo de inteligência\n"
        report += "- Refinar os critérios de filtragem de leads\n"
        report += "- Expandir as fontes de coleta de leads\n"
    
    if pipeline_stats['results']['average_personalization_score'] < 75:
        report += "- Melhorar os prompts do LLM para geração de emails\n"
        report += "- Adicionar mais contexto específico do setor\n"
        report += "- Refinar as estratégias de personalização\n"
    
    report += f"""
### Para Otimizar Performance
- Monitorar e ajustar os delays entre requisições
- Considerar processamento em lotes maiores para melhor eficiência
- Implementar cache para análises de websites repetidos

## Conclusão

O pipeline otimizado demonstrou eficácia na coleta e qualificação de leads usando inteligência artificial. 
A integração do LLM resultou em emails mais personalizados e leads de maior qualidade.

**Taxa de Sucesso Geral:** {(pipeline_stats['results']['emails_sent'] / pipeline_stats['results']['emails_generated'] * 100) if pipeline_stats['results']['emails_generated'] > 0 else 0:.1f}%
"""
    
    return report

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Vibe Scout Optimized Lead Generation Pipeline')
    parser.add_argument('--sector', type=str, default='restaurante', help='Target sector')
    parser.add_argument('--region', type=str, default='São Paulo', help='Target region')
    parser.add_argument('--min-score', type=int, default=70, help='Minimum intelligence score')
    parser.add_argument('--max-leads', type=int, default=50, help='Maximum number of leads to collect')
    parser.add_argument('--no-website-analysis', action='store_true', help='Skip website analysis')
    parser.add_argument('--no-social-analysis', action='store_true', help='Skip social media analysis')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no emails sent)')
    
    args = parser.parse_args()
    
    logger.info("Starting Vibe Scout Optimized Lead Generation Pipeline")
    logger.info(f"Sector: {args.sector}")
    logger.info(f"Region: {args.region}")
    logger.info(f"Min intelligence score: {args.min_score}")
    logger.info(f"Max leads: {args.max_leads}")
    logger.info(f"Website analysis: {not args.no_website_analysis}")
    logger.info(f"Social analysis: {not args.no_social_analysis}")
    logger.info(f"Test mode: {args.test}")
    
    # Create directories if they don't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Run optimized pipeline
    result = asyncio.run(run_optimized_pipeline(
        sector=args.sector,
        region=args.region,
        min_intelligence_score=args.min_score,
        max_leads=args.max_leads,
        include_website_analysis=not args.no_website_analysis,
        include_social_analysis=not args.no_social_analysis,
        test_mode=args.test
    ))
    
    if result['success']:
        logger.info("Optimized pipeline completed successfully!")
        logger.info(f"Results: {result['leads_count']} leads, {result['emails_generated']} emails generated, {result['emails_sent']} emails sent")
    else:
        logger.error("Optimized pipeline failed!")
        if 'error' in result:
            logger.error(f"Error: {result['error']}")

if __name__ == "__main__":
    main() 