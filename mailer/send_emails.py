import json
import logging
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@vibescout.com')
        self.consultant_email = os.getenv('CONSULTANT_EMAIL', 'consultant@vibescout.com')
        
        if not self.sendgrid_api_key:
            logger.warning("SENDGRID_API_KEY not found. Using mock email sending.")
            self.client = None
        else:
            self.client = SendGridAPIClient(api_key=self.sendgrid_api_key)
        
        self.sent_emails = []
        self.failed_emails = []
    
    def send_personalized_email(self, email_data: Dict, recipient_email: str = None) -> Dict:
        """Send a personalized email to a lead"""
        try:
            logger.info(f"Sending email to: {email_data.get('lead_id', 'Unknown')}")
            
            if not self.client:
                return self._mock_send_email(email_data, recipient_email)
            
            # Create email message
            message = Mail(
                from_email=self.from_email,
                to_emails=recipient_email or self._generate_test_email(email_data['lead_id']),
                subject=email_data['subject'],
                html_content=self._format_email_body(email_data['body'])
            )
            
            # Add personalization
            personalization = Personalization()
            personalization.add_to(Email(recipient_email or self._generate_test_email(email_data['lead_id'])))
            personalization.add_substitution("{{lead_name}}", email_data.get('lead_name', 'Cliente'))
            message.add_personalization(personalization)
            
            # Send email
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                result = {
                    'lead_id': email_data['lead_id'],
                    'email': recipient_email or self._generate_test_email(email_data['lead_id']),
                    'subject': email_data['subject'],
                    'status': 'sent',
                    'status_code': response.status_code,
                    'message_id': response.headers.get('X-Message-Id', 'unknown'),
                    'sent_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'personalization_score': email_data.get('personalization_score', 0)
                }
                
                self.sent_emails.append(result)
                logger.info(f"Email sent successfully to {email_data['lead_id']}")
                
                return result
            else:
                raise Exception(f"SendGrid API returned status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending email to {email_data.get('lead_id', 'Unknown')}: {e}")
            
            result = {
                'lead_id': email_data['lead_id'],
                'email': recipient_email or self._generate_test_email(email_data['lead_id']),
                'subject': email_data['subject'],
                'status': 'failed',
                'error_message': str(e),
                'sent_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'personalization_score': email_data.get('personalization_score', 0)
            }
            
            self.failed_emails.append(result)
            return result
    
    def _format_email_body(self, body: str) -> str:
        """Format email body as HTML"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vibe Scout - Marketing Digital</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .cta-button:hover {{
                    background-color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Vibe Scout</h1>
                <p>Especialistas em Marketing Digital</p>
            </div>
            <div class="content">
                {body.replace(chr(10), '<br>')}
                <br><br>
                <a href="mailto:{self.consultant_email}" class="cta-button">Responder Agora</a>
            </div>
            <div class="footer">
                <p>Este email foi enviado pelo sistema Vibe Scout.</p>
                <p>Para cancelar o recebimento, responda com "CANCELAR" no assunto.</p>
            </div>
        </body>
        </html>
        """
        return html_template
    
    def _generate_test_email(self, lead_id: str) -> str:
        """Generate a test email address for demo purposes"""
        # In production, you would use real email addresses
        # For demo, we'll create test addresses
        clean_id = ''.join(c for c in lead_id if c.isalnum()).lower()
        return f"test.{clean_id}@example.com"
    
    def _mock_send_email(self, email_data: Dict, recipient_email: str = None) -> Dict:
        """Mock email sending for testing when SendGrid is not available"""
        test_email = recipient_email or self._generate_test_email(email_data['lead_id'])
        
        result = {
            'lead_id': email_data['lead_id'],
            'email': test_email,
            'subject': email_data['subject'],
            'status': 'sent_mock',
            'status_code': 200,
            'message_id': f"mock_{int(time.time())}",
            'sent_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'personalization_score': email_data.get('personalization_score', 0),
            'note': 'Mock email - not actually sent'
        }
        
        self.sent_emails.append(result)
        logger.info(f"Mock email sent to {email_data['lead_id']} at {test_email}")
        
        return result
    
    def send_bulk_emails(self, emails_data: List[Dict], delay_seconds: int = 2, test_mode: bool = False) -> Dict:
        """Send emails in bulk with rate limiting"""
        logger.info(f"Starting bulk email send for {len(emails_data)} emails")
        
        results = {
            'total_emails': len(emails_data),
            'sent_count': 0,
            'failed_count': 0,
            'sent_emails': [],
            'failed_emails': []
        }
        
        for i, email_data in enumerate(emails_data):
            try:
                # Send email
                result = self.send_personalized_email(email_data)
                
                if result['status'] in ['sent', 'sent_mock']:
                    results['sent_count'] += 1
                    results['sent_emails'].append(result)
                else:
                    results['failed_count'] += 1
                    results['failed_emails'].append(result)
                
                # Add delay between emails to avoid rate limiting
                if i < len(emails_data) - 1:  # Don't delay after the last email
                    time.sleep(delay_seconds)
                
                # Log progress
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i + 1}/{len(emails_data)} emails processed")
                
            except Exception as e:
                logger.error(f"Error in bulk email send for {email_data.get('lead_id', 'Unknown')}: {e}")
                results['failed_count'] += 1
                results['failed_emails'].append({
                    'lead_id': email_data.get('lead_id', 'Unknown'),
                    'error_message': str(e),
                    'status': 'failed'
                })
        
        logger.info(f"Bulk email send completed. Sent: {results['sent_count']}, Failed: {results['failed_count']}")
        
        return results
    
    def send_summary_to_consultant(self, campaign_results: Dict, test_mode: bool = False) -> Dict:
        """Send campaign summary to the consultant"""
        try:
            logger.info("Sending campaign summary to consultant")
            
            # Create summary email
            summary_subject = f"Relatório de Campanha Vibe Scout - {time.strftime('%Y-%m-%d')}"
            
            summary_body = f"""
            <h2>Relatório de Campanha Vibe Scout</h2>
            
            <h3>Resumo Geral:</h3>
            <ul>
                <li><strong>Total de emails:</strong> {campaign_results['total_emails']}</li>
                <li><strong>Enviados com sucesso:</strong> {campaign_results['sent_count']}</li>
                <li><strong>Falharam:</strong> {campaign_results['failed_count']}</li>
                <li><strong>Taxa de sucesso:</strong> {(campaign_results['sent_count'] / campaign_results['total_emails'] * 100):.1f}%</li>
            </ul>
            
            <h3>Emails Enviados:</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>Lead</th>
                    <th>Email</th>
                    <th>Assunto</th>
                    <th>Score Personalização</th>
                    <th>Status</th>
                </tr>
            """
            
            for email in campaign_results['sent_emails'][:10]:  # Show first 10
                summary_body += f"""
                <tr>
                    <td>{email['lead_id']}</td>
                    <td>{email['email']}</td>
                    <td>{email['subject']}</td>
                    <td>{email['personalization_score']}</td>
                    <td>{email['status']}</td>
                </tr>
                """
            
            if len(campaign_results['sent_emails']) > 10:
                summary_body += f"<tr><td colspan='5'>... e mais {len(campaign_results['sent_emails']) - 10} emails</td></tr>"
            
            summary_body += """
            </table>
            
            <h3>Emails com Falha:</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>Lead</th>
                    <th>Erro</th>
                </tr>
            """
            
            for email in campaign_results['failed_emails'][:5]:  # Show first 5 failures
                summary_body += f"""
                <tr>
                    <td>{email['lead_id']}</td>
                    <td>{email.get('error_message', 'Erro desconhecido')}</td>
                </tr>
                """
            
            if len(campaign_results['failed_emails']) > 5:
                summary_body += f"<tr><td colspan='2'>... e mais {len(campaign_results['failed_emails']) - 5} falhas</td></tr>"
            
            summary_body += """
            </table>
            
            <p><em>Relatório gerado automaticamente pelo sistema Vibe Scout</em></p>
            """
            
            # Send summary email
            if self.client:
                message = Mail(
                    from_email=self.from_email,
                    to_emails=self.consultant_email,
                    subject=summary_subject,
                    html_content=summary_body
                )
                
                response = self.client.send(message)
                
                if response.status_code in [200, 201, 202]:
                    logger.info("Campaign summary sent to consultant successfully")
                    return {
                        'status': 'sent',
                        'consultant_email': self.consultant_email,
                        'message_id': response.headers.get('X-Message-Id', 'unknown')
                    }
                else:
                    raise Exception(f"Failed to send summary: {response.status_code}")
            else:
                logger.info("Mock campaign summary sent to consultant")
                return {
                    'status': 'sent_mock',
                    'consultant_email': self.consultant_email,
                    'note': 'Mock summary - not actually sent'
                }
                
        except Exception as e:
            logger.error(f"Error sending campaign summary: {e}")
            return {
                'status': 'failed',
                'error_message': str(e)
            }

def send_emails_to_leads(emails_data: List[Dict]) -> Dict:
    """Main function to send emails to all leads"""
    sender = EmailSender()
    
    # Send bulk emails
    campaign_results = sender.send_bulk_emails(emails_data)
    
    # Send summary to consultant
    summary_result = sender.send_summary_to_consultant(campaign_results)
    campaign_results['summary_sent'] = summary_result
    
    # Save campaign results
    with open('email_campaign_results.json', 'w') as f:
        json.dump(campaign_results, f, indent=2, ensure_ascii=False)
    
    return campaign_results

def main():
    """Main function to be called by CrewAI"""
    # Load generated emails
    try:
        with open('generated_emails.json', 'r') as f:
            emails = json.load(f)
    except FileNotFoundError:
        logger.error("generated_emails.json not found. Run the email generation first.")
        return {}
    
    # Send emails
    campaign_results = send_emails_to_leads(emails)
    
    logger.info(f"Email campaign completed:")
    logger.info(f"- Total emails: {campaign_results['total_emails']}")
    logger.info(f"- Sent successfully: {campaign_results['sent_count']}")
    logger.info(f"- Failed: {campaign_results['failed_count']}")
    
    return campaign_results

if __name__ == "__main__":
    # Test the email sender
    test_emails = [
        {
            'lead_id': 'Restaurante Teste',
            'lead_name': 'Restaurante Teste',
            'subject': 'Melhorias Digitais para Restaurante Teste',
            'body': 'Olá! Identificamos oportunidades de melhoria...',
            'personalization_score': 85
        },
        {
            'lead_id': 'Loja Online',
            'lead_name': 'Loja Online',
            'subject': 'Otimização Digital para Loja Online',
            'body': 'Olá! Analisamos seu site e encontramos...',
            'personalization_score': 78
        }
    ]
    
    results = send_emails_to_leads(test_emails)
    
    print(f"Test email campaign results:")
    print(f"Sent: {results['sent_count']}")
    print(f"Failed: {results['failed_count']}")
    print(f"Success rate: {(results['sent_count'] / results['total_emails'] * 100):.1f}%") 