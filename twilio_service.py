"""
Twilio Service Layer for SMS Call-Out Feature
Handles SMS text messages for employee call-out reporting
"""

import os
import logging
from datetime import datetime, date
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from models import TeamMember, PTORequest, CallOutRecord, get_eastern_time
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwilioSMSService:
    """Service for handling incoming SMS for call-outs"""

    def __init__(self):
        """Initialize Twilio SMS service with credentials from environment"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.sms_number = os.getenv('TWILIO_SMS_NUMBER') or os.getenv('TWILIO_PHONE_NUMBER')

        # Group MMS settings (Twilio Conversations API)
        self.conversation_sid = os.getenv('GROUP_MMS_CONVERSATION_SID')
        self.group_participants = [p.strip() for p in os.getenv('GROUP_MMS_PARTICIPANTS', '').split(',') if p.strip()]

        # Initialize Twilio client if credentials are available
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured. SMS will not work.")

    def authenticate_sender(self, from_number):
        """
        Authenticate SMS sender by phone number match
        Returns: (authenticated, member) tuple
        """
        # Normalize phone number
        normalized_number = from_number.replace('+1', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

        # Try phone number match
        member = TeamMember.query.filter(
            db.func.replace(db.func.replace(db.func.replace(TeamMember.phone, '-', ''), ' ', ''), '+1', '') == normalized_number
        ).first()

        if member:
            logger.info(f"Authenticated SMS from {member.name}: {from_number}")
            return (True, member)

        logger.warning(f"SMS authentication failed for {from_number}")
        return (False, None)

    def extract_reason(self, message_body):
        """Extract call-out reason from SMS text"""
        # Clean up the message text
        reason = message_body.strip()

        # Remove common prefixes
        prefixes_to_remove = [
            "calling out",
            "call out",
            "calling in sick",
            "calling in",
            "sick today",
            "sick",
            "-",
            ":"
        ]

        reason_lower = reason.lower()
        for prefix in prefixes_to_remove:
            if reason_lower.startswith(prefix):
                reason = reason[len(prefix):].strip()
                reason_lower = reason.lower()

        return reason if reason else "Not specified"

    def generate_sms_response(self, authenticated, member=None, request_id=None):
        """Generate TwiML response for SMS"""
        response = MessagingResponse()

        if authenticated and member and request_id:
            response.message(
                f"Call-out APPROVED, {member.name}. Your request has been automatically approved and your sick time has been deducted. Your manager has been notified. Feel better!"
            )
        elif not authenticated:
            response.message(
                "Phone number not found in system. Please contact your manager directly or submit via the web app."
            )
        else:
            response.message(
                "Error processing call-out. Please contact your manager directly."
            )

        return str(response)

    def create_call_out_request(self, member, message_sid, message_body, from_number):
        """
        Create PTO request and CallOutRecord for SMS call-out
        Auto-approves and deducts from sick balance immediately
        Returns: PTORequest object
        """
        try:
            # Get today's date in Eastern time
            today = get_eastern_time().date()
            today_str = today.strftime('%Y-%m-%d')

            # Extract reason from SMS
            reason = self.extract_reason(message_body)

            # Classify the call-out as sick or fmla based on the raw SMS body
            from call_out_classifier import classify_call_out
            classification = classify_call_out(message_body)

            # Create PTO request for today only (Sick, call-out)
            # Auto-approve call-outs (no manager approval needed)
            pto_request = PTORequest(
                member_id=member.id,
                start_date=today_str,
                end_date=today_str,
                pto_type='Sick',
                manager_team=member.team,
                status='approved',  # Auto-approve call-outs
                is_call_out=True,
                reason=f"Call-out via SMS: {reason}",
                approved_date=get_eastern_time(),
                callout_classification=classification
            )

            db.session.add(pto_request)
            db.session.flush()  # Get the PTO request ID

            # Deduct from sick balance immediately
            hours_to_deduct = pto_request.duration_hours
            current_sick_balance = float(member.sick_balance_hours)
            new_sick_balance = max(0, current_sick_balance - hours_to_deduct)
            member.sick_balance_hours = new_sick_balance

            logger.info(f"Auto-approved call-out #{pto_request.id} for {member.name}")
            logger.info(f"Deducted {hours_to_deduct} hours from sick balance. New balance: {new_sick_balance} hours")

            # Create CallOutRecord
            call_out_record = CallOutRecord(
                member_id=member.id,
                pto_request_id=pto_request.id,
                call_sid=message_sid,
                source='sms',
                phone_number_used=from_number,
                verified=True,
                authentication_method='phone_match',
                message_text=message_body,
                processed_at=get_eastern_time()
            )

            db.session.add(call_out_record)
            db.session.commit()

            logger.info(f"Created and auto-approved SMS call-out request #{pto_request.id} for {member.name}")
            return pto_request

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create SMS call-out request: {str(e)}")
            raise

    def send_employee_confirmation_sms(self, to_number, employee_name, request_id):
        """Send SMS confirmation to employee"""
        if not self.client or not to_number:
            logger.warning("Cannot send employee confirmation: No client or phone number")
            return False

        try:
            message_body = f"Call-out APPROVED, {employee_name}. Your request has been automatically approved and your sick time has been deducted. Your manager has been notified. Feel better!"
            message = self.client.messages.create(
                body=message_body,
                from_=self.sms_number,
                to=to_number
            )
            logger.info(f"Employee confirmation sent to {to_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send employee confirmation SMS: {str(e)}")
            return False

    def send_manager_notification_sms(self, manager_number, employee_name, request_id):
        """
        Send SMS notification to manager (DEPRECATED - use send_group_mms_notification instead)
        Kept for backwards compatibility
        """
        if not self.client or not manager_number:
            return False

        try:
            message = self.client.messages.create(
                body=f"FYI: {employee_name} called out sick today. AUTO-APPROVED. Sick time deducted. Check email for details.",
                from_=self.sms_number,
                to=manager_number
            )
            logger.info(f"Manager notification sent to {manager_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send manager SMS: {str(e)}")
            return False

    def create_group_conversation(self, friendly_name="Manager Call-Out Notifications"):
        """
        One-time setup: Create a Twilio Conversation and add all manager participants.
        Returns the Conversation SID to save to GROUP_MMS_CONVERSATION_SID env var.

        Usage:
            sms = TwilioSMSService()
            sid = sms.create_group_conversation()
            # Copy the SID to .env: GROUP_MMS_CONVERSATION_SID=CHxxx...
        """
        if not self.client:
            logger.error("Twilio client not initialized. Cannot create conversation.")
            return None

        if not self.group_participants:
            logger.error("No GROUP_MMS_PARTICIPANTS configured. Add phone numbers to .env first.")
            return None

        try:
            # Create the Conversation
            conversation = self.client.conversations.v1.conversations.create(
                friendly_name=friendly_name
            )
            logger.info(f"Created Conversation: {conversation.sid}")

            # Add a system/chat participant for sending messages
            self.client.conversations.v1.conversations(conversation.sid).participants.create(
                identity='pto-system'
            )
            logger.info("Added system participant: pto-system")

            # Add each manager phone number as a participant
            # The Twilio number serves as the proxy address for all participants
            for phone in self.group_participants:
                try:
                    self.client.conversations.v1.conversations(conversation.sid).participants.create(
                        messaging_binding_address=phone,
                        messaging_binding_proxy_address=self.sms_number
                    )
                    logger.info(f"Added participant: {phone}")
                except Exception as e:
                    logger.error(f"Failed to add participant {phone}: {str(e)}")

            logger.info(f"Conversation setup complete. SID: {conversation.sid}")
            logger.info(f"Add this to your .env: GROUP_MMS_CONVERSATION_SID={conversation.sid}")
            return conversation.sid

        except Exception as e:
            logger.error(f"Failed to create group conversation: {str(e)}")
            return None

    def send_group_mms_notification(self, employee_name, request_id, reason="Not specified"):
        """
        Send call-out notification to the manager group MMS conversation.
        All participants in the conversation will see the message in a shared thread.

        Args:
            employee_name: Name of the employee who called out
            request_id: PTO request ID
            reason: Call-out reason (optional)

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.client:
            logger.error("Twilio client not initialized. Cannot send group notification.")
            return False

        if not self.conversation_sid:
            logger.warning("GROUP_MMS_CONVERSATION_SID not configured. Falling back to individual SMS.")
            # Fallback: send individual SMS to each participant
            success = False
            for phone in self.group_participants:
                if self.send_manager_notification_sms(phone, employee_name, request_id):
                    success = True
            return success

        try:
            # Build the notification message
            message_body = (
                f"📢 CALL-OUT NOTIFICATION\n\n"
                f"Employee: {employee_name}\n"
                f"Request ID: #{request_id}\n"
                f"Reason: {reason}\n"
                f"Status: AUTO-APPROVED\n\n"
                f"Sick time has been deducted. Check email for full details."
            )

            # Send message to the Conversation
            # Author is the system identity (chat participant)
            message = self.client.conversations.v1.conversations(
                self.conversation_sid
            ).messages.create(
                body=message_body,
                author='pto-system'
            )

            logger.info(f"Group MMS notification sent: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Failed to send group MMS notification: {str(e)}")
            # Fallback to individual SMS
            logger.info("Falling back to individual SMS notifications...")
            success = False
            for phone in self.group_participants:
                if self.send_manager_notification_sms(phone, employee_name, request_id):
                    success = True
            return success
