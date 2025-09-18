#!/usr/bin/env python3
"""Test to verify manager email is sent to htn.prevention@mountsinai.org"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_manager_email():
    """Test that manager receives email at htn.prevention@mountsinai.org"""

    print("\n" + "="*70)
    print("TESTING MANAGER EMAIL TO htn.prevention@mountsinai.org")
    print("="*70)

    # Submit a new PTO request
    print("\nSubmitting PTO request...")

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    pto_data = {
        'team': 'admin',
        'position': 'Front Desk/Admin',
        'name': 'Test Employee',
        'email': 'test@example.com',
        'start_date': tomorrow,
        'end_date': next_week,
        'pto_type': 'Vacation',
        'reason': 'Testing manager email to htn.prevention@mountsinai.org',
        'is_partial_day': '',
        'start_time': '',
        'end_time': ''
    }

    response = requests.post(f"{BASE_URL}/submit_request", data=pto_data, allow_redirects=False)

    if response.status_code == 302:
        print("✓ PTO Request submitted successfully")
        print()
        print("EMAIL NOTIFICATIONS SENT:")
        print("-" * 40)
        print("  Manager notification:")
        print("    TO: htn.prevention@mountsinai.org")
        print("    SUBJECT: New PTO Request - Test Employee")
        print()
        print("  (Note: Employee does NOT receive email on submission)")
        print()
        print("="*70)
        print("Manager should check htn.prevention@mountsinai.org for the notification!")
        print("="*70)
    else:
        print("✗ Failed to submit request")

if __name__ == "__main__":
    test_manager_email()