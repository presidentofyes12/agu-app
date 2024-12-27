import smtplib
from email.mime.text import MIMEText
from odoo import models, fields, api

class CustomMail(models.Model):
    _name = 'custom.mail'
    _description = 'Custom Mail Integration with Thunderbird Mail'

    @api.model
    def send_thunderbird_mail(self, recipient, subject, body):
        # Thunderbird SMTP server configuration
        smtp_server = 'test'
        smtp_port = 587
        smtp_user = 'g'
        smtp_password = 'your_thunderbird_password'  # Replace with the actual password

        # Create the email message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = recipient

        # Send the email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [recipient], msg.as_string())
            return True
        except Exception as e:
            _logger.error('Failed to send email: %s', e)
            return False
