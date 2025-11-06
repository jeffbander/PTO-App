"""
Alternative email service implementation using simpler SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending PTO-related email notifications"""

    def __init__(self):
        """Initialize email service with configuration from environment variables"""
        self.enabled = os.getenv('EMAIL_ENABLED', 'False').lower() == 'true'
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@mswcvi.com')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'sbzakow@mswheart.com')
        self.clinical_email = os.getenv('CLINICAL_EMAIL', 'sbzakow@mswheart.com')

    def send_email(self, to_email, subject, body_html=None, body_text=None):
        """Send email via SMTP with HTML support"""

        # Always show email content in console for verification
        logger.info("="*50)
        logger.info("EMAIL NOTIFICATION")
        logger.info(f"TO: {to_email}")
        logger.info(f"FROM: {self.from_email}")
        logger.info(f"SUBJECT: {subject}")
        logger.info(f"BODY: {body_text or 'See HTML version'}")
        logger.info("="*50)

        if not self.enabled:
            logger.info("(Email sending disabled - console mode only)")
            return True

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add text and HTML parts
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)

            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)

            # Try to send email via SMTP with better error handling
            context = ssl.create_default_context()

            # Try TLS first
            try:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()

                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)

                    server.send_message(msg)
                    logger.info(f"✓ Email sent successfully to {to_email}")
                    return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"Authentication failed: {str(e)}")
                logger.error("Please check your Gmail app password in .env file")
                logger.error("To get an app password: https://myaccount.google.com/apppasswords")
                return False

            except smtplib.SMTPException as e:
                logger.error(f"SMTP error: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_submission_email(self, pto_request):
        """Send email notifications for PTO request submission"""

        # Override employee email to send to sbzakow@mswheart.com for testing
        employee_email = 'sbzakow@mswheart.com'
        employee_name = pto_request.member.name
        request_id = pto_request.id

        # Employee notification
        employee_subject = f"PTO Request Submitted - Request #{request_id}"

        employee_body_text = f"""
Dear {employee_name},

Your PTO request has been successfully submitted and is pending manager approval.

Request Details:
- Request ID: #{request_id}
- Employee: {employee_name}
- Start Date: {pto_request.start_date}
- End Date: {pto_request.end_date}
- PTO Type: {pto_request.pto_type}
- Reason: {pto_request.reason}
- Status: PENDING

You will receive an email notification once your manager reviews your request.

Thank you,
PTO Management System
        """

        employee_body_html = f"""
<html>
    <body style="font-family: Arial, sans-serif;">
        <h2>PTO Request Submitted</h2>
        <p>Dear {employee_name},</p>
        <p>Your PTO request has been successfully submitted.</p>
        <table border="1" cellpadding="5">
            <tr><td>Request ID:</td><td>#{request_id}</td></tr>
            <tr><td>Start Date:</td><td>{pto_request.start_date}</td></tr>
            <tr><td>End Date:</td><td>{pto_request.end_date}</td></tr>
            <tr><td>PTO Type:</td><td>{pto_request.pto_type}</td></tr>
            <tr><td>Status:</td><td>PENDING</td></tr>
        </table>
    </body>
</html>
        """

        # Send to employee
        self.send_email(employee_email, employee_subject, employee_body_html, employee_body_text)

        # Manager notification
        manager_email = self.admin_email if pto_request.manager_team == 'admin' else self.clinical_email
        manager_subject = f"New PTO Request - {employee_name}"

        manager_body_text = f"""
A new PTO request requires your attention.

Request Details:
- Request ID: #{request_id}
- Employee: {employee_name}
- Team: {pto_request.manager_team}
- Start Date: {pto_request.start_date}
- End Date: {pto_request.end_date}
- PTO Type: {pto_request.pto_type}
- Reason: {pto_request.reason}

Please log in to the PTO Management System at http://127.0.0.1:5000/dashboard to review this request.

Thank you,
PTO Management System
        """

        # Send to manager
        self.send_email(manager_email, manager_subject, body_text=manager_body_text)

        return True

    def send_approval_email(self, pto_request):
        """Send email notification when PTO request is approved"""

        employee_email = 'sbzakow@mswheart.com'
        employee_name = pto_request.member.name
        request_id = pto_request.id

        subject = f"PTO Request Approved - Request #{request_id}"

        body_text = f"""
Dear {employee_name},

Good news! Your PTO request has been approved by your manager.

Approved Request Details:
- Request ID: #{request_id}
- Employee: {employee_name}
- Start Date: {pto_request.start_date}
- End Date: {pto_request.end_date}
- PTO Type: {pto_request.pto_type}
- Status: IN PROGRESS

Next Steps:
- Your request is now in progress
- Timekeeping will be entered
- Coverage will be arranged
- You will receive a final confirmation once all steps are complete

Thank you,
PTO Management System
        """

        return self.send_email(employee_email, subject, body_text=body_text)

    def send_denial_email(self, pto_request, denial_reason=None):
        """Send email notification when PTO request is denied"""

        employee_email = 'sbzakow@mswheart.com'
        employee_name = pto_request.member.name
        request_id = pto_request.id
        reason_text = denial_reason or "No specific reason provided"

        subject = f"PTO Request Denied - Request #{request_id}"

        body_text = f"""
Dear {employee_name},

We regret to inform you that your PTO request has been denied.

Request Details:
- Request ID: #{request_id}
- Employee: {employee_name}
- Start Date: {pto_request.start_date}
- End Date: {pto_request.end_date}
- PTO Type: {pto_request.pto_type}
- Status: DENIED
- Reason for Denial: {reason_text}

If you have questions about this decision, please contact your manager directly.

Thank you,
PTO Management System
        """

        return self.send_email(employee_email, subject, body_text=body_text)

    def send_checklist_complete_email(self, pto_request):
        """Send email notification when checklist is completed and request is fully approved"""

        employee_email = 'sbzakow@mswheart.com'
        employee_name = pto_request.member.name
        request_id = pto_request.id

        subject = f"PTO Request Fully Approved - Request #{request_id}"

        body_text = f"""
Dear {employee_name},

Your PTO request has been fully processed and approved!

Final Approval Details:
- Request ID: #{request_id}
- Employee: {employee_name}
- Start Date: {pto_request.start_date}
- End Date: {pto_request.end_date}
- PTO Type: {pto_request.pto_type}
- Status: FULLY APPROVED

All Requirements Complete:
✓ Manager approval received
✓ Timekeeping has been entered
✓ Coverage has been arranged

Your PTO is now confirmed. Enjoy your time off!

Thank you,
PTO Management System
        """

        return self.send_email(employee_email, subject, body_text=body_text)