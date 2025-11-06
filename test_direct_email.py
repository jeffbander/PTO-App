#!/usr/bin/env python3
"""Direct test of email service to verify manager email address"""

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
        self.reason = "Testing manager email to htn.prevention@mountsinai.org"

# Initialize email service
email_service = EmailService()

print("="*70)
print("DIRECT EMAIL TEST - Manager Notification")
print("="*70)
print()
print("Configuration:")
print(f"  FROM: {email_service.from_email}")
print(f"  Manager Email (Admin): {email_service.admin_email}")
print(f"  Manager Email (Clinical): {email_service.clinical_email}")
print()

# Test sending submission email (only to manager)
pto_request = MockPTORequest()
print("Sending manager notification...")
print()

result = email_service.send_submission_email(pto_request)

if result:
    print("\nEMAIL SENT SUCCESSFULLY!")
    print("Manager notification sent to: htn.prevention@mountsinai.org")
else:
    print("\nEmail sending may have failed - check logs above")

print()
print("="*70)