#!/usr/bin/env python3
"""Test that both employee and manager receive emails on submission"""

from dotenv import load_dotenv
load_dotenv()

from email_service import EmailService

# Create mock objects
class MockMember:
    def __init__(self):
        self.name = "Test Employee"
        self.email = "test@example.com"

class MockPTORequest:
    def __init__(self):
        self.id = 999
        self.member = MockMember()
        self.manager_team = "admin"
        self.start_date = "2025-09-20"
        self.end_date = "2025-09-25"
        self.pto_type = "Vacation"
        self.reason = "Testing both emails on submission"

# Initialize email service
email_service = EmailService()

print("="*70)
print("TESTING SUBMISSION EMAILS")
print("="*70)
print()

# Test sending submission email (should send to BOTH employee and manager)
pto_request = MockPTORequest()
print("Sending submission emails...")
print()

result = email_service.send_submission_email(pto_request)

print("\nExpected emails:")
print("1. Employee confirmation -> samantha.zakow@mountsinai.org")
print("2. Manager notification -> htn.prevention@mountsinai.org")
print()
print("="*70)