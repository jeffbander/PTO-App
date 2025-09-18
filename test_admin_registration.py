#!/usr/bin/env python3
"""Test admin team employee registration"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"

# Submit admin team registration
registration_data = {
    'name': 'NOT_LISTED',
    'new_employee_name': 'Admin Test Employee',
    'new_employee_email': f'admin.test.{int(time.time())}@mswcvi.com',
    'new_employee_team': 'admin',
    'new_employee_position': 'Front Desk Coordinator',
    'employee_notes': 'Test admin team registration'
}

print("Submitting admin team employee registration...")
response = requests.post(f"{BASE_URL}/submit_request", data=registration_data, allow_redirects=False)
print(f"Status: {response.status_code}")

# Login as admin manager
session = requests.Session()
login_data = {
    'email': 'admin.manager@mswcvi.com',
    'password': 'admin123'
}

print("\nLogging in as admin manager...")
login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)

if login_response.status_code in [302, 303]:
    print("Login successful")

    # Access admin dashboard
    dashboard_response = session.get(f"{BASE_URL}/dashboard/admin")

    if 'Admin Test Employee' in dashboard_response.text:
        print("✓ Admin team registration found in admin dashboard!")

        # Count pending items in the dashboard
        if 'Pending Employee Registrations' in dashboard_response.text:
            print("✓ Dashboard shows pending employee registrations section")
            print("\nSUCCESS: Admin team registrations are routed to admin dashboard!")
    else:
        print("⚠ Registration not found in admin dashboard")

print("\nTest completed.")