#!/usr/bin/env python3
"""Test employee approval functionality"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"

# Submit a test registration
registration_data = {
    'name': 'NOT_LISTED',
    'new_employee_name': 'Approval Test Employee',
    'new_employee_email': f'approval.test.{int(time.time())}@mswcvi.com',
    'new_employee_team': 'clinical',
    'new_employee_position': 'CVI RN',
    'employee_notes': 'Test for approval functionality'
}

print("Submitting test employee registration...")
response = requests.post(f"{BASE_URL}/submit_request", data=registration_data, allow_redirects=False)
print(f"Status: {response.status_code}")

# Login as clinical manager
session = requests.Session()
login_data = {
    'email': 'clinical.manager@mswcvi.com',
    'password': 'clinical123'
}

print("\nLogging in as clinical manager...")
login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)

if login_response.status_code in [302, 303]:
    print("Login successful")

    # Get the dashboard to find the employee ID
    dashboard_response = session.get(f"{BASE_URL}/dashboard/clinical")

    # Extract the approve_employee URL from the response
    import re
    pattern = r'/approve_employee/(\d+)'
    matches = re.findall(pattern, dashboard_response.text)

    if matches:
        # Get the last employee ID (most recent)
        employee_id = matches[-1]
        print(f"\nFound pending employee with ID: {employee_id}")

        # Try to approve the employee
        approve_url = f"{BASE_URL}/approve_employee/{employee_id}"
        print(f"Attempting to approve employee at: {approve_url}")

        approve_response = session.get(approve_url, allow_redirects=False)
        print(f"Approval response status: {approve_response.status_code}")

        if approve_response.status_code in [302, 303]:
            print("✓ Employee approval completed successfully!")

            # Check if employee was added to team members
            from app import app
            from models import TeamMember

            with app.app_context():
                new_member = TeamMember.query.filter_by(
                    email=registration_data['new_employee_email']
                ).first()

                if new_member:
                    print(f"✓ Employee successfully added to team members!")
                    print(f"  Name: {new_member.name}")
                    print(f"  PTO Balance: {new_member.pto_balance_hours} hours")
                else:
                    print("⚠ Employee not found in team members yet")
        else:
            print(f"⚠ Unexpected response from approval: {approve_response.status_code}")
    else:
        print("⚠ No pending employees found in dashboard")

print("\nTest completed.")