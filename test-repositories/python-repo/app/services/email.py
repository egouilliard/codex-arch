import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..utils.helpers import format_email_template
import logging

# Setup logging
logger = logging.getLogger(__name__)

class EmailConfig:
    """
    Email configuration class for SMTP settings
    """
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@example.com')
        self.from_name = os.environ.get('FROM_NAME', 'My Flask App')
        self.debug_mode = os.environ.get('EMAIL_DEBUG', 'True').lower() == 'true'
        
    def get_connection(self):
        """
        Create and return an SMTP connection
        
        Returns:
            smtplib.SMTP: SMTP connection
        """
        if self.debug_mode:
            logger.info(f"Would connect to {self.smtp_server}:{self.smtp_port}")
            return None
            
        try:
            conn = smtplib.SMTP(self.smtp_server, self.smtp_port)
            conn.starttls()
            conn.login(self.smtp_username, self.smtp_password)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {str(e)}")
            return None

# Initialize email configuration
email_config = EmailConfig()

def send_email(to_email, subject, html_content, text_content=None):
    """
    Send an email using SMTP
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str): HTML email content
        text_content (str, optional): Plain text email content
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if email_config.debug_mode:
        logger.info(f"Would send email to {to_email} with subject '{subject}'")
        logger.debug(f"Email content: {html_content}")
        return True
        
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{email_config.from_name} <{email_config.from_email}>"
    msg['To'] = to_email
    
    # Add plain text version if provided, or convert from HTML
    if text_content is None:
        # Simple conversion from HTML to text (in a real app, use a proper HTML->text converter)
        text_content = html_content.replace('<br>', '\n').replace('</p>', '\n\n')
        text_content = ''.join(c for c in text_content if ord(c) < 128)  # Strip non-ASCII chars
    
    msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))
    
    conn = email_config.get_connection()
    if conn is None:
        return False
        
    try:
        conn.send_message(msg)
        conn.quit()
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_welcome_email(to_email, username):
    """
    Send a welcome email to a new user
    
    Args:
        to_email (str): User's email address
        username (str): User's username
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Welcome to Our Flask App!"
    
    template_data = {
        'username': username,
        'login_url': 'https://example.com/login',
        'support_email': 'support@example.com'
    }
    
    html_content = format_email_template('welcome.html', template_data)
    text_content = format_email_template('welcome.txt', template_data)
    
    return send_email(to_email, subject, html_content, text_content)

def send_password_reset(to_email, reset_token):
    """
    Send a password reset email with a reset token
    
    Args:
        to_email (str): User's email address
        reset_token (str): Password reset token
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Password Reset Request"
    
    reset_url = f"https://example.com/reset-password?token={reset_token}"
    
    template_data = {
        'reset_url': reset_url,
        'support_email': 'support@example.com',
        'expires_in': '30 minutes'
    }
    
    html_content = format_email_template('password_reset.html', template_data)
    text_content = format_email_template('password_reset.txt', template_data)
    
    return send_email(to_email, subject, html_content, text_content)

def send_notification_email(to_email, notification_type, data):
    """
    Send a notification email based on type
    
    Args:
        to_email (str): User's email address
        notification_type (str): Type of notification (e.g., 'comment', 'like')
        data (dict): Data for the notification
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if notification_type == 'comment':
        subject = f"New Comment on Your Post: {data['post_title']}"
        template = 'comment_notification'
    elif notification_type == 'like':
        subject = f"Someone Liked Your Post: {data['post_title']}"
        template = 'like_notification'
    else:
        subject = "New Notification"
        template = 'general_notification'
    
    html_content = format_email_template(f"{template}.html", data)
    text_content = format_email_template(f"{template}.txt", data)
    
    return send_email(to_email, subject, html_content, text_content) 