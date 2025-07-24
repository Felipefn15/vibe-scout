#!/usr/bin/env python3
"""
Vibe Scout - Software Development Lead Generation Pipeline
Main orchestration script for prospecting and evaluating digital presence
"""

import os
import sys
import logging
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/vibe_scout.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_crewai_pipeline(industry: str, region: str, test_mode: bool = False):
    """
    Run the Vibe Scout pipeline using CrewAI orchestration
    """
    try:
        from crewai import Agent, Task, Crew, Process
        from langchain_groq import ChatGroq
        
        # Configure Groq LLM
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            logger.warning("GROQ_API_KEY not found. Using mock mode.")
            test_mode = True
        
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="mixtral-8x7b-32768"  # Fast and cost-effective model
        ) if groq_api_key else None
        
        logger.info(f"Starting CrewAI pipeline for {industry} in {region}")
        logger.info(f"Test mode: {test_mode}")
        
        # Define Agents
        lead_collector_agent = Agent(
            role='Lead Collection Specialist',
            goal='Collect high-quality leads from multiple sources including Google Search, Google Maps, and Instagram',
            backstory="""You are an expert digital marketing lead generation specialist. 
            You have years of experience finding potential clients through various online sources.
            You understand how to identify businesses that could benefit from digital marketing services.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        site_analyzer_agent = Agent(
            role='Website Performance Analyst',
            goal='Analyze website performance, SEO metrics, and technical issues to identify improvement opportunities',
            backstory="""You are a technical SEO and website performance expert.
            You can identify website issues, performance bottlenecks, and SEO opportunities.
            You understand what makes a website successful and what needs improvement.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        social_media_agent = Agent(
            role='Social Media Analyst',
            goal='Analyze social media presence and engagement to understand digital marketing maturity',
            backstory="""You are a social media marketing expert.
            You can assess a business's social media presence and identify opportunities for improvement.
            You understand engagement metrics and social media strategy.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        email_generator_agent = Agent(
            role='Email Marketing Specialist',
            goal='Generate personalized, compelling email content based on analysis data',
            backstory="""You are an expert email copywriter and digital marketing strategist.
            You know how to craft personalized emails that resonate with business owners.
            You understand pain points and can communicate value propositions effectively.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        email_sender_agent = Agent(
            role='Email Campaign Manager',
            goal='Manage and execute email campaigns with proper tracking and follow-up',
            backstory="""You are an email campaign management expert.
            You understand email deliverability, timing, and campaign optimization.
            You can track results and manage follow-up sequences.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        report_builder_agent = Agent(
            role='Data Analyst and Report Specialist',
            goal='Create comprehensive reports and insights from campaign data',
            backstory="""You are a data analyst and reporting specialist.
            You can synthesize complex data into actionable insights.
            You create professional reports that help consultants understand results.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        # Define Tasks
        collect_leads_task = Task(
            description=f"""
            Collect leads for {industry} businesses in {region}.
            
            Steps:
            1. Search Google for "{industry} {region}" businesses
            2. Search Google Maps for local businesses
            3. Search Instagram for business profiles
            4. Extract: business name, website, phone, email, location
            5. Remove duplicates and validate data
            6. Save results to 'data/leads.json'
            
            Expected output: List of lead dictionaries with business information
            """,
            agent=lead_collector_agent,
            expected_output="JSON file with collected leads data"
        )
        
        analyze_sites_task = Task(
            description="""
            Analyze website performance and SEO for collected leads.
            
            Steps:
            1. Load leads from 'data/leads.json'
            2. For each website, run Lighthouse analysis
            3. Perform on-page SEO analysis
            4. Identify technical issues and opportunities
            5. Save analysis results to 'data/site_analysis.json'
            
            Expected output: Enhanced leads data with site analysis
            """,
            agent=site_analyzer_agent,
            expected_output="JSON file with site analysis data"
        )
        
        analyze_social_task = Task(
            description="""
            Analyze social media presence for collected leads.
            
            Steps:
            1. Load leads from 'data/site_analysis.json'
            2. Search for Instagram profiles for each business
            3. Analyze follower count, engagement, post frequency
            4. Assess social media maturity level
            5. Save social analysis to 'data/social_analysis.json'
            
            Expected output: Enhanced leads data with social media analysis
            """,
            agent=social_media_agent,
            expected_output="JSON file with social media analysis data"
        )
        
        generate_emails_task = Task(
            description="""
            Generate personalized email content for each lead.
            
            Steps:
            1. Load leads from 'data/social_analysis.json'
            2. For each lead, create personalized email based on:
               - Website performance issues
               - SEO opportunities
               - Social media gaps
               - Business type and location
            3. Generate compelling subject lines
            4. Save email content to 'data/emails.json'
            
            Expected output: Email content for each lead
            """,
            agent=email_generator_agent,
            expected_output="JSON file with personalized email content"
        )
        
        send_emails_task = Task(
            description="""
            Send personalized emails to leads and track results.
            
            Steps:
            1. Load email content from 'data/emails.json'
            2. Send emails using SendGrid API
            3. Track delivery status and opens
            4. Handle bounces and errors
            5. Save campaign results to 'data/campaign_results.json'
            
            Expected output: Campaign results and statistics
            """,
            agent=email_sender_agent,
            expected_output="JSON file with campaign results"
        )
        
        build_report_task = Task(
            description="""
            Create comprehensive campaign report and send to consultant.
            
            Steps:
            1. Load all data: leads, analysis, emails, campaign results
            2. Create Excel report with multiple sheets:
               - Summary dashboard
               - Lead details
               - Performance analysis
               - Social media insights
               - Email campaign results
               - Opportunities and recommendations
            3. Generate charts and visualizations
            4. Send report to consultant via email
            5. Save report as 'reports/vibe_scout_report.xlsx'
            
            Expected output: Professional Excel report and email notification
            """,
            agent=report_builder_agent,
            expected_output="Excel report file and email confirmation"
        )
        
        # Create Crew
        crew = Crew(
            agents=[
                lead_collector_agent,
                site_analyzer_agent,
                social_media_agent,
                email_generator_agent,
                email_sender_agent,
                report_builder_agent
            ],
            tasks=[
                collect_leads_task,
                analyze_sites_task,
                analyze_social_task,
                generate_emails_task,
                send_emails_task,
                build_report_task
            ],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute pipeline
        logger.info("Starting CrewAI pipeline execution...")
        result = crew.kickoff()
        
        logger.info("CrewAI pipeline completed successfully!")
        logger.info(f"Result: {result}")
        
        return {
            "status": "success",
            "result": result,
            "test_mode": test_mode
        }
        
    except Exception as e:
        logger.error(f"Error in CrewAI pipeline: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "test_mode": test_mode
        }

def run_pipeline_simple(industry, region, test_mode=False):
    """
    Run the pipeline without CrewAI (simple sequential execution)
    """
    try:
        logger.info(f"Starting simple Vibe Scout pipeline for {industry} in {region}")
        
        # Initialize lead manager
        from utils.lead_manager import LeadManager
        lead_manager = LeadManager()
        
        # Step 1: Lead Collection
        logger.info("Step 1: Collecting leads...")
        from scraper.collect import LeadCollector
        collector = LeadCollector()
        
        # Get target count from market config
        target_count = 25  # Default
        try:
            with open('config/markets.json', 'r', encoding='utf-8') as f:
                markets_config = json.load(f)
                for market in markets_config['markets']:
                    if market['name'].lower() == industry.lower():
                        target_count = market.get('target_count', 25)
                        break
        except Exception as e:
            logger.warning(f"Could not load market config: {e}")
        
        leads = collector.collect_leads(industry, region, test_mode=test_mode, target_count=target_count)
        
        # Filter out already contacted leads
        new_leads = lead_manager.filter_new_leads(leads)
        
        if not new_leads:
            logger.warning("No new leads to contact. All leads have been contacted before.")
            return {
                'status': 'warning',
                'message': 'No new leads to contact',
                'leads_collected': 0,
                'emails_sent': 0,
                'test_mode': test_mode,
                'lead_stats': lead_manager.get_stats()
            }
        
        # Save leads
        os.makedirs('data', exist_ok=True)
        with open('data/leads.json', 'w') as f:
            json.dump(new_leads, f, indent=2)
        
        # Step 2: Site Analysis
        logger.info("Step 2: Analyzing websites...")
        from analysis.site_seo import SiteAnalyzer
        site_analyzer = SiteAnalyzer()
        site_analyzed_leads = site_analyzer.analyze_sites_from_leads(leads, test_mode=test_mode)
        
        # Save site analysis
        with open('data/site_analysis.json', 'w') as f:
            json.dump(site_analyzed_leads, f, indent=2)
        
        # Step 3: Social Media Analysis
        logger.info("Step 3: Analyzing social media...")
        from analysis.social import SocialMediaAnalyzer
        social_analyzer = SocialMediaAnalyzer()
        social_analyzed_leads = social_analyzer.analyze_social_media_for_leads(site_analyzed_leads, test_mode=test_mode)
        
        # Save social analysis
        with open('data/social_analysis.json', 'w') as f:
            json.dump(social_analyzed_leads, f, indent=2)
        
        # Step 4: Email Generation
        logger.info("Step 4: Generating emails...")
        from llm.generate_email import EmailGenerator
        email_generator = EmailGenerator()
        emails = email_generator.generate_bulk_emails(social_analyzed_leads, test_mode=test_mode)
        
        # Save emails
        with open('data/emails.json', 'w') as f:
            json.dump(emails, f, indent=2)
        
        # Step 5: Email Sending
        logger.info("Step 5: Sending emails...")
        from mailer.send_emails import EmailSender
        email_sender = EmailSender()
        
        # Add industry and region info to emails
        for email in emails:
            email['industry'] = industry
            email['region'] = region
        
        send_results = email_sender.send_bulk_emails(emails, test_mode=test_mode)
        
        # Add campaign metadata to results
        send_results['industry'] = industry
        send_results['region'] = region
        send_results['campaign_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save campaign results
        with open('data/campaign_results.json', 'w') as f:
            json.dump(send_results, f, indent=2)
        
        # Step 6: Report Generation
        logger.info("Step 6: Generating final report...")
        from reports.build_report import ReportBuilder
        report_builder = ReportBuilder()
        report_file = report_builder.build_comprehensive_report(social_analyzed_leads, send_results, test_mode=test_mode)
        
        # Step 7: Send summary to consultant
        logger.info("Step 7: Sending summary to consultant...")
        email_sender.send_summary_to_consultant(send_results, test_mode=test_mode)
        
        # Mark leads as contacted
        for lead in new_leads:
            lead_manager.mark_contacted(lead['name'])
        
        logger.info("Simple pipeline completed successfully!")
        return {
            "status": "success",
            "leads_collected": len(new_leads),
            "emails_sent": len(emails),
            "report_file": report_file,
            "test_mode": test_mode,
            "lead_stats": lead_manager.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Error in simple pipeline: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "test_mode": test_mode
        }

def main():
    """Main function to run the Vibe Scout pipeline"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Vibe Scout - Software Development Lead Generation Pipeline')
    parser.add_argument('--industry', required=True, help='Industry to search for (e.g., restaurantes, advocacias, farmacias, etc.)')
    parser.add_argument('--region', default='Rio de Janeiro', help='Region to search in (default: Rio de Janeiro)')
    parser.add_argument('--test', action='store_true', help='Run in test mode with limited data collection')
    parser.add_argument('--simple', action='store_true', help='Use simple pipeline instead of CrewAI')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("VIBE SCOUT - SOFTWARE DEVELOPMENT PIPELINE")
    print("=" * 60)
    
    print(f"Industry: {args.industry}")
    print(f"Region: {args.region}")
    print(f"Test Mode: {args.test}")
    print(f"Pipeline Type: {'Simple' if args.simple else 'CrewAI'}")
    print("=" * 60)
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Run pipeline
    if args.simple:
        result = run_pipeline_simple(args.industry, args.region, args.test)
    else:
        result = run_crewai_pipeline(args.industry, args.region, args.test)
    
            # Display results
        print("\n" + "=" * 60)
        print("PIPELINE RESULTS")
        print("=" * 60)
        
        if result["status"] == "success":
            print("✅ Pipeline completed successfully!")
            if "leads_collected" in result:
                print(f"📊 Leads collected: {result['leads_collected']}")
            if "emails_sent" in result:
                print(f"📧 Emails sent: {result['emails_sent']}")
            if "report_file" in result:
                print(f"📄 Report generated: {result['report_file']}")
            if "result" in result:
                print(f"🤖 CrewAI result: {result['result']}")
        elif result["status"] == "warning":
            print("⚠️ Pipeline completed with warnings!")
            if "message" in result:
                print(f"Message: {result['message']}")
            if "leads_collected" in result:
                print(f"📊 Leads collected: {result['leads_collected']}")
            if "emails_sent" in result:
                print(f"📧 Emails sent: {result['emails_sent']}")
        else:
            print("❌ Pipeline failed!")
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print("Unknown error occurred")
        
        print("=" * 60)

if __name__ == "__main__":
    main() 