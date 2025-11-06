#!/usr/bin/env python3
"""Simple test script to verify email sending functionality"""

import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_email_workflow():
    """Submit a PTO request to trigger email notifications"""

    print("\n" + "="*70)
    print("TESTING EMAIL NOTIFICATIONS")
    print("="*70)

    # Prepare PTO request data
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

    pto_data = {
        'team': 'admin',
        'position': 'Front Desk/Admin',
        'name': 'Test Employee',
        'email': 'sbzakow@mswheart.com',
        'start_date': tomorrow,
        'end_date': end_date,
        'pto_type': 'Vacation',
        'reason': 'Testing email notifications',
        'is_partial_day': '',
        'start_time': '',
        'end_time': ''
    }

    print("\n1. SUBMITTING PTO REQUEST")
    print("-" * 40)
    print(f"   Employee: {pto_data['name']}")
    print(f"   Email: {pto_data['email']}")
    print(f"   Dates: {pto_data['start_date']} to {pto_data['end_date']}")

    # Submit the request
    response = requests.post(f"{BASE_URL}/submit_request", data=pto_data, allow_redirects=False)

    if response.status_code == 302:
        print(f"   ✓ PTO Request submitted successfully")
        print(f"   - Email should be sent to: sbzakow@mswheart.com")
        print(f"   - From: samantha.zakow@mountsinai.org")
        print("\n   Check your email inbox for:")
        print("   1. Employee notification - 'PTO Request Submitted'")
        print("   2. Manager notification - 'New PTO Request'")
    else:
        print(f"   ✗ Failed to submit request: {response.status_code}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("Please check sbzakow@mswheart.com for email notifications")
    print("="*70)

if __name__ == "__main__":
    test_email_workflow()