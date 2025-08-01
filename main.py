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
import asyncio
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
        from llm.llm_client import ModularLLMClient
        
        # Configure modular LLM client
        llm_client = ModularLLMClient()
        
        # Check if any LLM providers are available
        available_providers = llm_client.get_available_providers()
        if not available_providers or available_providers == ['Mock']:
            logger.warning("No LLM providers available. Using mock mode.")
            test_mode = True
        
        logger.info(f"Available LLM providers: {available_providers}")
        
        # Create LangChain compatible LLM wrapper for CrewAI
        class LangChainLLMWrapper:
            def __init__(self, llm_client):
                self.llm_client = llm_client
            
            async def ainvoke(self, messages, **kwargs):
                # Extract the last user message
                user_message = None
                for message in reversed(messages):
                    if message.type == "human":
                        user_message = message.content
                        break
                
                if not user_message:
                    user_message = str(messages[-1].content)
                
                # Generate response using modular client
                response = await self.llm_client.generate(
                    user_message,
                    max_tokens=kwargs.get('max_tokens', 2048),
                    temperature=kwargs.get('temperature', 0.7)
                )
                
                # Return in LangChain format
                from langchain.schema import AIMessage
                return AIMessage(content=response.content)
            
            def invoke(self, messages, **kwargs):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                return loop.run_until_complete(self.ainvoke(messages, **kwargs))
        
        llm = LangChainLLMWrapper(llm_client) if not test_mode else None
        
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
            
            Expected output: Campaign results and delivery statistics
            """,
            agent=email_sender_agent,
            expected_output="JSON file with campaign results"
        )
        
        build_report_task = Task(
            description="""
            Create comprehensive campaign report with insights and recommendations.
            
            Steps:
            1. Load all campaign data (leads, analysis, emails, results)
            2. Calculate key metrics and performance indicators
            3. Identify patterns and insights
            4. Generate actionable recommendations
            5. Create professional report in markdown format
            
            Expected output: Comprehensive campaign report
            """,
            agent=report_builder_agent,
            expected_output="Markdown report with campaign insights"
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
            process=Process.sequential,
            verbose=True
        )
        
        # Run the crew
        logger.info("Starting CrewAI pipeline execution...")
        result = crew.kickoff()
        
        # Save LLM statistics
        stats = llm_client.get_stats()
        with open('llm_stats.json', 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info("CrewAI pipeline completed successfully!")
        logger.info(f"LLM Statistics: {json.dumps(stats, indent=2)}")
        
        return result
        
    except ImportError as e:
        logger.error(f"Missing required dependencies: {e}")
        logger.info("Please install CrewAI: pip install crewai")
        return None
    except Exception as e:
        logger.error(f"Error in CrewAI pipeline: {e}")
        return None

async def run_pipeline_simple(industry, region, test_mode=False):
    """
    Run a simplified pipeline without CrewAI for testing
    """
    try:
        logger.info(f"Running simple pipeline for {industry} in {region}")
        
        # Import required modules
        from scraper.collect import LeadCollector
        from utils.lead_scorer import LeadScorer
        from llm.generate_email import EmailGenerator
        
        # Initialize components
        collector = LeadCollector()
        scorer = LeadScorer()
        email_generator = EmailGenerator()
        
        # Collect leads
        logger.info("Collecting leads...")
        leads = await collector.collect_leads(industry, region)
        
        if not leads:
            logger.warning("No leads collected")
            return []
        
        # Score leads
        logger.info("Scoring leads...")
        scored_leads = []
        for lead in leads:
            score_data = scorer.calculate_lead_score(lead)
            lead['score'] = score_data
            scored_leads.append(lead)
        
        # Filter high-quality leads
        high_quality_leads = [lead for lead in scored_leads if lead['score']['total_score'] >= 70]
        
        logger.info(f"Collected {len(leads)} leads, {len(high_quality_leads)} high-quality")
        
        # Generate emails for high-quality leads
        if high_quality_leads:
            logger.info("Generating personalized emails...")
            emails = email_generator.generate_bulk_emails(high_quality_leads, test_mode=test_mode)
            
            # Save results
            with open('data/leads.json', 'w') as f:
                json.dump(leads, f, indent=2, ensure_ascii=False)
            
            with open('data/scored_leads.json', 'w') as f:
                json.dump(scored_leads, f, indent=2, ensure_ascii=False)
            
            with open('data/emails.json', 'w') as f:
                json.dump(emails, f, indent=2, ensure_ascii=False)
            
            # Save LLM statistics
            stats = email_generator.get_llm_stats()
            with open('llm_stats.json', 'w') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Generated {len(emails)} emails")
            logger.info(f"LLM Statistics: {json.dumps(stats, indent=2)}")
            
            return emails
        
        return []
        
    except Exception as e:
        logger.error(f"Error in simple pipeline: {e}")
        return []

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Vibe Scout Lead Generation Pipeline')
    parser.add_argument('--industry', type=str, default='restaurante', help='Target industry')
    parser.add_argument('--region', type=str, default='São Paulo', help='Target region')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--simple', action='store_true', help='Use simple pipeline without CrewAI')
    
    args = parser.parse_args()
    
    logger.info("Starting Vibe Scout Lead Generation Pipeline")
    logger.info(f"Industry: {args.industry}")
    logger.info(f"Region: {args.region}")
    logger.info(f"Test mode: {args.test}")
    logger.info(f"Simple mode: {args.simple}")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    if args.simple:
        result = asyncio.run(run_pipeline_simple(args.industry, args.region, args.test))
    else:
        result = run_crewai_pipeline(args.industry, args.region, args.test)
    
    if result:
        logger.info("Pipeline completed successfully!")
    else:
        logger.error("Pipeline failed!")

if __name__ == "__main__":
    main() 