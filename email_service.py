"""
Enhanced email service with HTML email support for PTO notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

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
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@mswcvi.com')
        self.clinical_email = os.getenv('CLINICAL_EMAIL', 'clinical@mswcvi.com')

    def send_email(self, to_email, subject, body_html=None, body_text=None):
        """Send email via SMTP with HTML support"""
        if not self.enabled:
            # Console fallback for testing/debugging
            logger.info("EMAIL NOTIFICATION (Console Mode - Email Disabled)")
            logger.info(f"TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            logger.info(f"BODY: {body_text or 'See HTML version'}")
            logger.info("-" * 50)
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

            # Send email via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            # In production, you might want to raise this exception
            # For now, we'll just log it and return False
            return False

    def send_submission_email(self, pto_request):
        """Send email notifications when PTO request is submitted"""

        # Get employee and request details
        employee_name = pto_request.member.name
        request_id = pto_request.id

        # Check if this is a call-out and get call-out details
        call_out_info = None
        if pto_request.is_call_out:
            from models import CallOutRecord
            call_out_record = CallOutRecord.query.filter_by(pto_request_id=pto_request.id).first()
            if call_out_record:
                call_out_info = {
                    'source': call_out_record.source,
                    'phone': call_out_record.phone_number_used,
                    'auth_method': call_out_record.authentication_method,
                    'message_text': call_out_record.message_text,
                    'created_at': call_out_record.created_at
                }

        # Send BOTH employee confirmation AND manager notification

        # 1. Employee confirmation email
        employee_email = pto_request.member.email
        employee_subject = f"PTO Request Submitted - Request #{request_id}"

        # Add call-out badge to subject if applicable
        if call_out_info:
            employee_subject = f"✅ CALL-OUT Approved - Request #{request_id}"

        employee_body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: {'#28a745' if call_out_info else '#17a2b8'}; color: white; padding: 20px; text-align: center;">
                    <h2>{'✅ CALL-OUT Auto-Approved' if call_out_info else 'PTO Request Confirmation'}</h2>
                </div>

                <div style="padding: 20px; background-color: #f8f9fa;">
                    <p>Dear {employee_name},</p>

                    <p>Your {'<strong>same-day call-out</strong> has been <strong style="color: #28a745;">AUTOMATICALLY APPROVED</strong>' if call_out_info else 'PTO request has been successfully submitted and is pending manager approval'}.</p>

                    {'<div style="background-color: #d4edda; border: 2px solid #28a745; padding: 15px; margin: 15px 0; border-radius: 5px;"><strong>✅ Auto-Approved:</strong> Your call-out has been automatically approved and your sick time balance has been updated. Your manager has been notified for their records.</div>' if call_out_info else ''}

                    <div style="background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid {'#28a745' if call_out_info else '#17a2b8'};">
                        <h3 style="margin-top: 0;">Request Details:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Request ID:</strong> #{request_id}</li>
                            <li><strong>Start Date:</strong> {pto_request.start_date}</li>
                            <li><strong>End Date:</strong> {pto_request.end_date}</li>
                            <li><strong>PTO Type:</strong> {pto_request.pto_type}</li>
                            <li><strong>Reason:</strong> {pto_request.reason}</li>
                            <li><strong>Status:</strong> <span style="color: {'#28a745' if call_out_info else '#ffc107'}; font-weight: bold;">{'APPROVED' if call_out_info else 'PENDING APPROVAL'}</span></li>
                            {'<li><strong>Submitted Via:</strong> <span style="color: #17a2b8;">💬 Text Message</span></li>' if call_out_info and call_out_info['source'] == 'sms' else ''}
                            {'<li><strong>Phone Used:</strong> ' + call_out_info['phone'] + '</li>' if call_out_info else ''}
                        </ul>
                    </div>

                    <p>{'Your sick time balance has been automatically updated. Feel better!' if call_out_info else 'You will receive an email notification once your manager reviews your request.'}</p>

                    <p>Thank you,<br>PTO Management System</p>
                </div>

                <div style="background-color: #e9ecef; padding: 10px; text-align: center; font-size: 12px;">
                    <p>This is an automated confirmation. Please do not reply to this email.</p>
                </div>
            </body>
        </html>
        """

        employee_body_text = f"""
        Dear {employee_name},

        Your PTO request has been successfully submitted and is pending manager approval.

        Request Details:
        - Request ID: #{request_id}
        - Start Date: {pto_request.start_date}
        - End Date: {pto_request.end_date}
        - PTO Type: {pto_request.pto_type}
        - Reason: {pto_request.reason}
        - Status: PENDING APPROVAL

        You will receive an email notification once your manager reviews your request.

        Thank you,
        PTO Management System
        """

        # Send employee confirmation
        self.send_email(employee_email, employee_subject, employee_body_html, employee_body_text)

        # 2. Manager notification
        manager_email = self.admin_email if pto_request.manager_team == 'admin' else self.clinical_email
        manager_subject = f"{'✅ CALL-OUT Auto-Approved (FYI)' if call_out_info else 'New PTO Request'} - {employee_name}"

        # Build call-out details section for manager
        call_out_section = ''
        if call_out_info:
            sms_message = ''
            if call_out_info['source'] == 'sms' and call_out_info['message_text']:
                sms_message = f'''
                    <div style="background-color: #e7f3ff; padding: 15px; margin: 15px 0; border-radius: 5px;">
                        <h4 style="margin-top: 0;">💬 SMS Message:</h4>
                        <p style="font-style: italic; padding: 10px; background-color: white; border-left: 3px solid #17a2b8;">
                            "{call_out_info['message_text']}"
                        </p>
                    </div>
                '''

            source_icon = '💬 Text Message'
            auth_badge = call_out_info['auth_method'].replace('_', ' ').title() if call_out_info['auth_method'] else 'Unknown'

            call_out_section = f'''
                <div style="background-color: #d4edda; border: 2px solid #28a745; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #155724;">✅ CALL-OUT AUTO-APPROVED</h3>
                    <p style="margin: 5px 0;"><strong>Submitted Via:</strong> {source_icon}</p>
                    <p style="margin: 5px 0;"><strong>Phone Number:</strong> {call_out_info['phone']}</p>
                    <p style="margin: 5px 0;"><strong>Authentication:</strong> <span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.9em;">✓ {auth_badge}</span></p>
                    <p style="margin: 5px 0;"><strong>Received At:</strong> {call_out_info['created_at'].strftime('%I:%M %p') if call_out_info['created_at'] else 'N/A'}</p>
                    <p style="margin: 5px 0;"><strong>Status:</strong> <span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.9em;">✓ APPROVED</span></p>
                </div>
                {sms_message}
            '''

        manager_body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: {'#28a745' if call_out_info else '#28a745'}; color: white; padding: 20px; text-align: center;">
                    <h2>{'✅ Call-Out Auto-Approved (FYI)' if call_out_info else 'New PTO Request Pending Approval'}</h2>
                </div>

                <div style="padding: 20px; background-color: #f8f9fa;">
                    <p>{'<strong style="color: #28a745;">FYI:</strong> An employee called out sick for today and was automatically approved. Sick time has been deducted.' if call_out_info else 'A new PTO request requires your attention.'}</p>

                    {call_out_section}

                    <div style="background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid {'#dc3545' if call_out_info else '#28a745'};">
                        <h3 style="margin-top: 0;">Request Details:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Request ID:</strong> #{request_id}</li>
                            <li><strong>Employee:</strong> {employee_name}</li>
                            <li><strong>Team:</strong> {pto_request.manager_team}</li>
                            <li><strong>Start Date:</strong> {pto_request.start_date}</li>
                            <li><strong>End Date:</strong> {pto_request.end_date}</li>
                            <li><strong>PTO Type:</strong> {pto_request.pto_type}</li>
                            <li><strong>Reason:</strong> {pto_request.reason}</li>
                        </ul>
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://127.0.0.1:5000/dashboard" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Request Now</a>
                    </div>

                    <p>Please log in to the PTO Management System to approve or deny this request.</p>
                </div>

                <div style="background-color: #e9ecef; padding: 10px; text-align: center; font-size: 12px;">
                    <p>This is an automated message from the PTO Management System.</p>
                </div>
            </body>
        </html>
        """

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
        self.send_email(manager_email, manager_subject, manager_body_html, manager_body_text)

        # ALSO send notification to admin (ms15639@nyu.edu)
        admin_notification_email = "ms15639@nyu.edu"
        admin_subject = f"[PTO System] {'Call-Out Auto-Approved' if call_out_info else 'New PTO Request'} - {employee_name}"
        self.send_email(admin_notification_email, admin_subject, manager_body_html, manager_body_text)

        return True

    def send_approval_email(self, pto_request):
        """Send email notification when PTO request is approved"""

        # Override employee email to send to samantha.zakow@mountsinai.org for testing
        employee_email = 'samantha.zakow@mountsinai.org'
        employee_name = pto_request.member.name
        request_id = pto_request.id

        subject = f"PTO Request Approved - Request #{request_id}"

        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                    <h2>PTO Request Approved!</h2>
                </div>

                <div style="padding: 20px; background-color: #f8f9fa;">
                    <p>Dear {employee_name},</p>

                    <p style="color: #28a745; font-weight: bold;">Good news! Your PTO request has been approved by your manager.</p>

                    <div style="background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid #28a745;">
                        <h3 style="margin-top: 0;">Approved Request Details:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Request ID:</strong> #{request_id}</li>
                            <li><strong>Employee:</strong> {employee_name}</li>
                            <li><strong>Start Date:</strong> {pto_request.start_date}</li>
                            <li><strong>End Date:</strong> {pto_request.end_date}</li>
                            <li><strong>PTO Type:</strong> {pto_request.pto_type}</li>
                            <li><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">APPROVED</span></li>
                        </ul>
                    </div>

                    <p>Your request is being processed and you will receive a final confirmation once all administrative tasks are complete.</p>

                    <p>Thank you,<br>PTO Management System</p>
                </div>

                <div style="background-color: #e9ecef; padding: 10px; text-align: center; font-size: 12px;">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </body>
        </html>
        """

        body_text = f"""
        Dear {employee_name},

        Good news! Your PTO request has been approved by your manager.

        Approved Request Details:
        - Request ID: #{request_id}
        - Employee: {employee_name}
        - Start Date: {pto_request.start_date}
        - End Date: {pto_request.end_date}
        - PTO Type: {pto_request.pto_type}
        - Status: APPROVED

        Your request is being processed and you will receive a final confirmation once all administrative tasks are complete.

        Thank you,
        PTO Management System
        """

        return self.send_email(employee_email, subject, body_html, body_text)

    def send_denial_email(self, pto_request, denial_reason=None):
        """Send email notification when PTO request is denied"""

        # Override employee email to send to samantha.zakow@mountsinai.org for testing
        employee_email = 'samantha.zakow@mountsinai.org'
        employee_name = pto_request.member.name
        request_id = pto_request.id

        reason_text = denial_reason or "No specific reason provided"

        subject = f"PTO Request Denied - Request #{request_id}"

        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
                    <h2>PTO Request Denied</h2>
                </div>

                <div style="padding: 20px; background-color: #f8f9fa;">
                    <p>Dear {employee_name},</p>

                    <p>We regret to inform you that your PTO request has been denied.</p>

                    <div style="background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid #dc3545;">
                        <h3 style="margin-top: 0;">Request Details:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Request ID:</strong> #{request_id}</li>
                            <li><strong>Employee:</strong> {employee_name}</li>
                            <li><strong>Start Date:</strong> {pto_request.start_date}</li>
                            <li><strong>End Date:</strong> {pto_request.end_date}</li>
                            <li><strong>PTO Type:</strong> {pto_request.pto_type}</li>
                            <li><strong>Status:</strong> <span style="color: #dc3545; font-weight: bold;">DENIED</span></li>
                            <li><strong>Reason for Denial:</strong> {reason_text}</li>
                        </ul>
                    </div>

                    <p>If you have questions about this decision, please contact your manager directly.</p>

                    <p>Thank you,<br>PTO Management System</p>
                </div>

                <div style="background-color: #e9ecef; padding: 10px; text-align: center; font-size: 12px;">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </body>
        </html>
        """

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

        return self.send_email(employee_email, subject, body_html, body_text)

    def send_checklist_complete_email(self, pto_request):
        """Send email notification when checklist is completed and request is fully approved"""

        # Override employee email to send to samantha.zakow@mountsinai.org for testing
        employee_email = 'samantha.zakow@mountsinai.org'
        employee_name = pto_request.member.name
        request_id = pto_request.id

        subject = f"PTO Request Fully Approved - Request #{request_id}"

        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                    <h2>PTO Request Fully Approved!</h2>
                </div>

                <div style="padding: 20px; background-color: #f8f9fa;">
                    <p>Dear {employee_name},</p>

                    <p style="color: #28a745; font-weight: bold;">Your PTO request has been fully processed and approved!</p>

                    <div style="background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid #28a745;">
                        <h3 style="margin-top: 0;">Final Approval Details:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>Request ID:</strong> #{request_id}</li>
                            <li><strong>Employee:</strong> {employee_name}</li>
                            <li><strong>Start Date:</strong> {pto_request.start_date}</li>
                            <li><strong>End Date:</strong> {pto_request.end_date}</li>
                            <li><strong>PTO Type:</strong> {pto_request.pto_type}</li>
                            <li><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">FULLY APPROVED</span></li>
                        </ul>
                    </div>

                    <div style="background-color: #d4edda; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4 style="margin-top: 0; color: #155724;">✓ All Requirements Complete:</h4>
                        <ul style="color: #155724;">
                            <li>Manager approval received</li>
                            <li>Timekeeping has been entered</li>
                            <li>Coverage has been arranged</li>
                        </ul>
                    </div>

                    <p>Your PTO is now confirmed. Enjoy your time off!</p>

                    <p>Thank you,<br>PTO Management System</p>
                </div>

                <div style="background-color: #e9ecef; padding: 10px; text-align: center; font-size: 12px;">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </body>
        </html>
        """

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

        return self.send_email(employee_email, subject, body_html, body_text)