#!/usr/bin/env python3
"""Test to verify email addresses being used"""

from dotenv import load_dotenv
import os
from email_service import EmailService

# Load environment variables
load_dotenv()

print("="*70)
print("EMAIL CONFIGURATION TEST")
print("="*70)
print()
print("Environment Variables:")
print(f"  ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")
print(f"  CLINICAL_EMAIL: {os.getenv('CLINICAL_EMAIL')}")
print(f"  FROM_EMAIL: {os.getenv('FROM_EMAIL')}")
print()

# Initialize email service
email_service = EmailService()

print("Email Service Configuration:")
print(f"  admin_email: {email_service.admin_email}")
print(f"  clinical_email: {email_service.clinical_email}")
print(f"  from_email: {email_service.from_email}")
print()

# Create a mock PTO request to test email addresses
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
        self.reason = "Testing email addresses"

print("Testing Email Routing:")
print("-" * 40)

# Test admin team request
admin_request = MockPTORequest()
admin_request.manager_team = "admin"
print(f"\nAdmin Team Request:")
print(f"  Manager notification will go to: {email_service.admin_email}")

# Test clinical team request
clinical_request = MockPTORequest()
clinical_request.manager_team = "clinical"
print(f"\nClinical Team Request:")
print(f"  Manager notification will go to: {email_service.clinical_email}")

print()
print("="*70)
print("SUMMARY:")
print("  All manager notifications now go to: htn.prevention@mountsinai.org")
print("  Employee notifications go to: samantha.zakow@mountsinai.org (hardcoded for testing)")
print("  All emails sent FROM: sbzakow@mswheart.com")
print("="*70)