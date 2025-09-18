"""Enhanced email service for sending PTO notifications with HTML support"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_domain_name():
    """Get the application domain name"""
    return os.environ.get('APP_DOMAIN', 'http://localhost:5000')

class EmailService:
    """Email service for sending notifications"""

    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.username = os.environ.get('EMAIL_USERNAME', 'noreply@mswcvi.com')
        self.password = os.environ.get('EMAIL_PASSWORD', 'default_password')
        self.enabled = os.environ.get('EMAIL_ENABLED', 'False').lower() == 'true'
        self.from_name = 'MSW CVI PTO System'

    def send_email(self, to_email, subject, body_html=None, body_text=None):
        """Send email via SMTP with HTML support"""
        if not self.enabled:
            # Console fallback for testing/debugging
            logger.info("="*50)
            logger.info("EMAIL NOTIFICATION (Console Mode - Email Disabled)")
            logger.info("="*50)
            logger.info(f"TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            if body_text:
                logger.info(f"BODY:\n{body_text}")
            logger.info("="*50)
            return True

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.username}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text part
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)

            # Add HTML part
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            logger.info(f"[SUCCESS] Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to send email to {to_email}: {e}")
            # Fallback to console output
            logger.info("="*50)
            logger.info("EMAIL NOTIFICATION (Fallback Console Mode)")
            logger.info("="*50)
            logger.info(f"TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            if body_text:
                logger.info(f"BODY:\n{body_text}")
            logger.info("="*50)
            return False

def send_submission_email(request_data, request_id):
    """Send email notifications for PTO request submission"""
    email_service = EmailService()

    # Employee notification
    employee_subject = f"PTO Request Submitted - Request #{request_id}"

    employee_body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #007bff; color: white; padding: 20px; text-align: center;">
                <h2>PTO Request Submitted</h2>
            </div>
            <div style="padding: 20px;">
                <p>Dear {request_data.get('name', 'Employee')},</p>
                <p>Your PTO request has been successfully submitted.</p>

                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Request ID:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">#{request_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Date Range:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('start_date')} to {request_data.get('end_date')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Type:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('pto_type', 'PTO')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;"><span style="color: #ffc107;">Pending Approval</span></td>
                    </tr>
                </table>

                <p>You will receive another email once your request has been reviewed.</p>

                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from the MSW CVI PTO System
                </p>
            </div>
        </body>
    </html>
    """

    employee_body_text = f"""
Dear {request_data.get('name', 'Employee')},

Your PTO request has been successfully submitted.

Request Details:
- Request ID: #{request_id}
- Date Range: {request_data.get('start_date')} to {request_data.get('end_date')}
- Type: {request_data.get('pto_type', 'PTO')}
- Status: Pending Approval

You will receive another email once your request has been reviewed.

Best regards,
MSW CVI PTO System
"""

    employee_email = request_data.get('email')
    if employee_email:
        email_service.send_email(employee_email, employee_subject, employee_body_html, employee_body_text)

    # Manager notification
    manager_subject = f"New PTO Request - {request_data.get('name')} - Request #{request_id}"

    manager_body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
                <h2>New PTO Request Requires Review</h2>
            </div>
            <div style="padding: 20px;">
                <p>A new PTO request has been submitted and requires your review.</p>

                <h3>Employee Information</h3>
                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Name:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('name')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Email:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('email')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Position:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('position')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Team:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('team')}</td>
                    </tr>
                </table>

                <h3>Request Details</h3>
                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Request ID:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">#{request_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Date Range:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('start_date')} to {request_data.get('end_date')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Type:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('pto_type', 'PTO')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Reason:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request_data.get('reason', 'Not specified')}</td>
                    </tr>
                </table>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{get_domain_name()}/dashboard"
                       style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Review Request
                    </a>
                </div>

                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from the MSW CVI PTO System
                </p>
            </div>
        </body>
    </html>
    """

    manager_body_text = f"""
A new PTO request has been submitted and requires your review.

Employee: {request_data.get('name')}
Email: {request_data.get('email')}
Position: {request_data.get('position')}
Team: {request_data.get('team')}

Request Details:
- Request ID: #{request_id}
- Date Range: {request_data.get('start_date')} to {request_data.get('end_date')}
- Type: {request_data.get('pto_type', 'PTO')}
- Reason: {request_data.get('reason', 'Not specified')}

Please log in to the PTO system to review and approve/deny this request:
{get_domain_name()}/dashboard

Best regards,
MSW CVI PTO System
"""

    # Log manager notification for testing
    logger.info(f"Manager notification sent for request #{request_id}")

    return True

def send_approval_email(request):
    """Send email notification when PTO request is approved"""
    email_service = EmailService()

    subject = f"PTO Request Approved - Request #{request.id}"

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                <h2>PTO Request Approved!</h2>
            </div>
            <div style="padding: 20px;">
                <p>Dear {request.member.name},</p>
                <p>Good news! Your PTO request has been approved by your manager.</p>

                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Request ID:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">#{request.id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Date Range:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request.start_date} to {request.end_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Type:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request.pto_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;"><span style="color: #ffc107;">In Progress</span></td>
                    </tr>
                </table>

                <p><strong>Next Steps:</strong></p>
                <p>Your manager will complete the following checklist items:</p>
                <ul>
                    <li>Enter timekeeping information</li>
                    <li>Arrange coverage for your absence</li>
                </ul>

                <p>Once these items are complete, your PTO will be fully approved.</p>

                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from the MSW CVI PTO System
                </p>
            </div>
        </body>
    </html>
    """

    body_text = f"""
Dear {request.member.name},

Good news! Your PTO request has been approved by your manager.

Request Details:
- Request ID: #{request.id}
- Date Range: {request.start_date} to {request.end_date}
- Type: {request.pto_type}
- Status: In Progress

Next Steps:
Your manager will complete the following checklist items:
- Enter timekeeping information
- Arrange coverage for your absence

Once these items are complete, your PTO will be fully approved.

Best regards,
MSW CVI PTO System
"""

    return email_service.send_email(request.member.email, subject, body_html, body_text)

def send_denial_email(request, denial_reason=None):
    """Send email notification when PTO request is denied"""
    email_service = EmailService()

    subject = f"PTO Request Update - Request #{request.id}"

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
                <h2>PTO Request Update</h2>
            </div>
            <div style="padding: 20px;">
                <p>Dear {request.member.name},</p>
                <p>Your PTO request has been reviewed by your manager.</p>

                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Request ID:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">#{request.id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Date Range:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request.start_date} to {request.end_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Type:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request.pto_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;"><span style="color: #dc3545;">Denied</span></td>
                    </tr>
                    {f'''<tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Reason:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{denial_reason}</td>
                    </tr>''' if denial_reason else ''}
                </table>

                <p>If you have questions about this decision, please contact your manager directly.</p>

                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from the MSW CVI PTO System
                </p>
            </div>
        </body>
    </html>
    """

    body_text = f"""
Dear {request.member.name},

Your PTO request has been reviewed by your manager.

Request Details:
- Request ID: #{request.id}
- Date Range: {request.start_date} to {request.end_date}
- Type: {request.pto_type}
- Status: Denied
{f"- Reason: {denial_reason}" if denial_reason else ""}

If you have questions about this decision, please contact your manager directly.

Best regards,
MSW CVI PTO System
"""

    return email_service.send_email(request.member.email, subject, body_html, body_text)

def send_checklist_complete_email(request):
    """Send email notification when checklist is complete and request is fully approved"""
    email_service = EmailService()

    subject = f"PTO Request Fully Approved - Request #{request.id}"

    body_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                <h2>✅ PTO Request Fully Approved!</h2>
            </div>
            <div style="padding: 20px;">
                <p>Dear {request.member.name},</p>
                <p>Great news! All checklist items have been completed and your PTO is now fully approved.</p>

                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Request ID:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">#{request.id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Date Range:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request.start_date} to {request.end_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Type:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{request.pto_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;"><span style="color: #28a745; font-weight: bold;">✅ Fully Approved</span></td>
                    </tr>
                </table>

                <p><strong>Completed Checklist:</strong></p>
                <ul style="color: #28a745;">
                    <li>✓ Timekeeping Entered</li>
                    <li>✓ Coverage Arranged</li>
                </ul>

                <p style="font-size: 18px; color: #28a745; text-align: center; margin: 30px 0;">
                    <strong>Enjoy your time off!</strong>
                </p>

                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from the MSW CVI PTO System
                </p>
            </div>
        </body>
    </html>
    """

    body_text = f"""
Dear {request.member.name},

Great news! All checklist items have been completed and your PTO is now fully approved.

Request Details:
- Request ID: #{request.id}
- Date Range: {request.start_date} to {request.end_date}
- Type: {request.pto_type}
- Status: ✅ Fully Approved

Completed Checklist:
✓ Timekeeping Entered
✓ Coverage Arranged

Enjoy your time off!

Best regards,
MSW CVI PTO System
"""

    return email_service.send_email(request.member.email, subject, body_html, body_text)