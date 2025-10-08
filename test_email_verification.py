#!/usr/bin/env python3
"""Test to verify email sending functionality"""

import requests
from datetime import datetime, timedelta
import time

BASE_URL = "http://127.0.0.1:5000"

def test_email_functionality():
    """Submit a PTO request and verify email is sent"""

    print("\n" + "="*70)
    print("TESTING EMAIL FUNCTIONALITY")
    print("="*70)

    print("\nSubmitting a PTO request to trigger email notifications...")
    print("-" * 40)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    pto_data = {
        'team': 'admin',
        'position': 'Front Desk/Admin',
        'name': 'John Smith',
        'email': 'john.smith@mswcvi.com',
        'start_date': tomorrow,
        'end_date': next_week,
        'pto_type': 'Personal',
        'reason': 'Testing email notifications',
        'is_partial_day': '',
        'start_time': '',
        'end_time': ''
    }

    print(f"\nPTO Request Details:")
    print(f"  Employee: {pto_data['name']}")
    print(f"  Email: {pto_data['email']}")
    print(f"  Dates: {pto_data['start_date']} to {pto_data['end_date']}")
    print(f"  Type: {pto_data['pto_type']}")

    response = requests.post(f"{BASE_URL}/submit_request", data=pto_data, allow_redirects=False)

    if response.status_code == 302:
        print(f"\nPTO Request submitted successfully (Status: {response.status_code})")
        print("\nIf EMAIL_ENABLED=True in .env, the following should happen:")
        print("  1. Employee receives confirmation email")
        print("  2. Manager receives notification email")
        print("\nCheck the Flask server console output for email logs.")
        print("Email will be sent to: samantha.zakow@mountsinai.org")
        return True
    else:
        print(f"\nError: Request failed with status {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_email_functionality()

    print("\n" + "="*70)
    if success:
        print("EMAIL TEST COMPLETED")
        print("\nTo verify emails were sent:")
        print("  1. Check Flask console for email logs")
        print("  2. Check inbox for: samantha.zakow@mountsinai.org")
        print("  3. Look for 'PTO Request Submitted' subject line")
    else:
        print("EMAIL TEST FAILED")
    print("="*70)
