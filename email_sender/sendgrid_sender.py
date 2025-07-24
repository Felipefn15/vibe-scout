#!/usr/bin/env python3
"""
SendGrid Email Sender
Handles email sending using SendGrid API
"""

import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SendGridSender:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'felipe@technologie.com.br')
        self.from_name = os.getenv('FROM_NAME', 'Felipe França')
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY not found. Email sending will be simulated.")
            self.client = None
        else:
            try:
                from sendgrid import SendGridAPIClient
                self.client = SendGridAPIClient(api_key=self.api_key)
                logger.info("SendGrid client initialized successfully")
            except ImportError:
                logger.warning("SendGrid library not installed. Email sending will be simulated.")
                self.client = None
    
    def send_email(self, to_email: str, subject: str, body: str, lead_name: str = "") -> bool:
        """Send an email using SendGrid"""
        try:
            if not to_email or not subject or not body:
                logger.warning(f"Missing email data for {lead_name}")
                return False
            
            if not self.client:
                logger.info(f"Simulating email send to {to_email} for {lead_name}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Body length: {len(body)} characters")
                return True
            
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            # Create email
            from_email = Email(self.from_email, self.from_name)
            to_email_obj = To(to_email)
            content = Content("text/plain", body)
            mail = Mail(from_email, to_email_obj, subject, content)
            
            # Send email
            response = self.client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email} for {lead_name}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
    
    def send_bulk_emails(self, emails_data: list) -> Dict:
        """Send multiple emails and return results"""
        results = {
            'total': len(emails_data),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for email_data in emails_data:
            success = self.send_email(
                to_email=email_data.get('to_email', ''),
                subject=email_data.get('subject', ''),
                body=email_data.get('body', ''),
                lead_name=email_data.get('lead_name', '')
            )
            
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'lead_name': email_data.get('lead_name', ''),
                    'email': email_data.get('to_email', ''),
                    'error': 'Failed to send email'
                })
        
        logger.info(f"Bulk email results: {results['sent']}/{results['total']} sent successfully")
        return results
    
    def test_connection(self) -> bool:
        """Test SendGrid connection"""
        if not self.client:
            logger.warning("SendGrid client not available")
            return False
        
        try:
            # Try to get account info to test connection
            response = self.client.client.user.account.get()
            if response.status_code == 200:
                logger.info("SendGrid connection test successful")
                return True
            else:
                logger.error(f"SendGrid connection test failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"SendGrid connection test error: {e}")
            return False

def main():
    """Test the SendGrid sender"""
    sender = SendGridSender()
    
    # Test connection
    if sender.test_connection():
        print("✅ SendGrid connection successful")
    else:
        print("⚠️  SendGrid connection failed (may be normal if API key not configured)")
    
    # Test email sending
    test_email = {
        'to_email': 'test@example.com',
        'subject': 'Test Email',
        'body': 'This is a test email from Vibe Scout',
        'lead_name': 'Test Company'
    }
    
    success = sender.send_email(**test_email)
    if success:
        print("✅ Email sending test successful")
    else:
        print("⚠️  Email sending test failed (may be normal if API key not configured)")

if __name__ == "__main__":
    main() 