"""
Email utilities for Argo Aviation Referral Portal
SendGrid integration for email confirmations
"""

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import secrets
import os
from datetime import datetime, timedelta

# SendGrid configuration
SENDGRID_API_KEY = "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"
FROM_EMAIL = "noreply@argo-aviation.com"  # You can change this
FROM_NAME = "Argo Aviation Referral Portal"

def send_confirmation_email(user_email, user_name, confirmation_token):
    """Send email confirmation to new user"""
    
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    
    # Create confirmation URL
    confirmation_url = f"https://web-production-9c059.up.railway.app/confirm-email/{confirmation_token}"
    
    # Email content with Argo Aviation branding
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #DAA520, #B8860B); color: white; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
            .content {{ color: #333; line-height: 1.6; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #DAA520, #B8860B); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛩️ Argo Aviation</h1>
                <p>Referral Portal - E-Mail Bestätigung</p>
            </div>
            <div class="content">
                <h2>Willkommen, {user_name}!</h2>
                <p>Vielen Dank für Ihre Registrierung beim Argo Aviation Referral Portal.</p>
                <p>Um Ihr Konto zu aktivieren, klicken Sie bitte auf den folgenden Button:</p>
                
                <a href="{confirmation_url}" class="button">E-Mail Adresse bestätigen</a>
                
                <p>Falls der Button nicht funktioniert, kopieren Sie diesen Link in Ihren Browser:</p>
                <p style="word-break: break-all; color: #666;">{confirmation_url}</p>
                
                <p><strong>Wichtig:</strong> Dieser Link ist 24 Stunden gültig.</p>
                
                <p>Falls Sie sich nicht registriert haben, ignorieren Sie diese E-Mail.</p>
            </div>
            <div class="footer">
                <p>© 2024 Argo Aviation Referral Portal</p>
                <p>Diese E-Mail wurde automatisch generiert. Bitte antworten Sie nicht auf diese E-Mail.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Willkommen bei Argo Aviation Referral Portal!
    
    Hallo {user_name},
    
    vielen Dank für Ihre Registrierung. Um Ihr Konto zu aktivieren, besuchen Sie bitte:
    {confirmation_url}
    
    Dieser Link ist 24 Stunden gültig.
    
    Falls Sie sich nicht registriert haben, ignorieren Sie diese E-Mail.
    
    © 2024 Argo Aviation Referral Portal
    """
    
    # Create email
    from_email = Email(FROM_EMAIL, FROM_NAME)
    to_email = To(user_email)
    subject = "Argo Aviation - E-Mail Bestätigung erforderlich"
    
    mail = Mail(from_email, to_email, subject, Content("text/plain", text_content))
    mail.add_content(Content("text/html", html_content))
    
    try:
        response = sg.send(mail)
        return True, f"Email sent successfully. Status: {response.status_code}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def generate_confirmation_token():
    """Generate a secure confirmation token"""
    return secrets.token_urlsafe(32)

def send_welcome_email(user_email, user_name):
    """Send welcome email after successful confirmation"""
    
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #DAA520, #B8860B); color: white; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 20px; }}
            .content {{ color: #333; line-height: 1.6; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #DAA520, #B8860B); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛩️ Argo Aviation</h1>
                <p>Willkommen im Referral Portal!</p>
            </div>
            <div class="content">
                <h2>Herzlich Willkommen, {user_name}! 🎉</h2>
                <p>Ihre E-Mail Adresse wurde erfolgreich bestätigt!</p>
                <p>Sie können jetzt:</p>
                <ul>
                    <li>Stellenausschreibungen durchsuchen</li>
                    <li>Kandidaten für Jobs empfehlen</li>
                    <li>Ihre Empfehlungen verfolgen</li>
                    <li>Referral-Boni verdienen</li>
                </ul>
                
                <a href="https://web-production-9c059.up.railway.app/login" class="button">Jetzt anmelden</a>
                
                <p>Vielen Dank, dass Sie Teil des Argo Aviation Teams sind!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    from_email = Email(FROM_EMAIL, FROM_NAME)
    to_email = To(user_email)
    subject = "🎉 Willkommen bei Argo Aviation Referral Portal!"
    
    mail = Mail(from_email, to_email, subject, Content("text/html", html_content))
    
    try:
        response = sg.send(mail)
        return True, f"Welcome email sent successfully. Status: {response.status_code}"
    except Exception as e:
        return False, f"Error sending welcome email: {str(e)}"
