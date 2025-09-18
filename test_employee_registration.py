#!/usr/bin/env python3
"""Test script to verify employee registration functionality"""

import requests
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_employee_registration():
    """Test submitting a new employee registration"""

    print("=" * 60)
    print("TESTING EMPLOYEE REGISTRATION FUNCTIONALITY")
    print("=" * 60)

    # Test employee registration data
    registration_data = {
        'name': 'NOT_LISTED',
        'new_employee_name': 'Test Employee',
        'new_employee_email': f'test.employee.{int(time.time())}@mswcvi.com',
        'new_employee_team': 'clinical',
        'new_employee_position': 'CVI RN Test',
        'employee_notes': 'This is a test registration submitted at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    print(f"\n1. Submitting employee registration for: {registration_data['new_employee_name']}")
    print(f"   Team: {registration_data['new_employee_team']}")
    print(f"   Position: {registration_data['new_employee_position']}")
    print(f"   Email: {registration_data['new_employee_email']}")

    # Submit the registration
    try:
        response = requests.post(f"{BASE_URL}/submit_request", data=registration_data, allow_redirects=False)
        print(f"\n   Response Status: {response.status_code}")

        if response.status_code in [302, 303]:  # Redirect after POST
            print("   ✓ Registration submitted successfully (redirected)")

            # Follow the redirect to see flash messages
            redirect_response = requests.get(BASE_URL + response.headers.get('Location', '/'))
            if 'submitted' in redirect_response.text.lower() or 'success' in redirect_response.text.lower():
                print("   ✓ Success message likely displayed")
        else:
            print(f"   ⚠ Unexpected status code: {response.status_code}")

    except Exception as e:
        print(f"   ✗ Error submitting registration: {e}")
        return False

    print("\n2. Testing manager login to verify registration appears in dashboard")

    # Create a session to maintain cookies
    session = requests.Session()

    # Login as clinical manager
    login_data = {
        'email': 'clinical.manager@mswcvi.com',
        'password': 'clinical123'
    }

    print(f"\n   Logging in as: {login_data['email']}")

    try:
        login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)

        if login_response.status_code in [302, 303]:
            print("   ✓ Login successful")

            # Access the clinical dashboard
            dashboard_response = session.get(f"{BASE_URL}/dashboard/clinical")

            if dashboard_response.status_code == 200:
                print("   ✓ Accessed clinical dashboard")

                # Check if our test employee appears
                if registration_data['new_employee_name'] in dashboard_response.text:
                    print(f"   ✓ Test employee '{registration_data['new_employee_name']}' found in dashboard!")
                    print("\n   SUCCESS: Employee registration is routed to the correct manager dashboard!")

                    # Count pending items
                    if 'pending_employees' in dashboard_response.text:
                        print("   ✓ Dashboard shows pending employee registrations section")
                else:
                    print(f"   ⚠ Test employee not found in dashboard")
                    print("   Note: The template may need updating to display pending employees")
            else:
                print(f"   ✗ Failed to access dashboard: {dashboard_response.status_code}")
        else:
            print(f"   ✗ Login failed: {login_response.status_code}")

    except Exception as e:
        print(f"   ✗ Error during login/dashboard check: {e}")

    # Also check the database directly
    print("\n3. Checking database directly for the pending employee...")

    try:
        # Import database models
        import sys
        sys.path.append('C:\\Users\\zakows01\\PTO take 3\\PTO-App-Samanthas-Version')
        from app import app
        from models import PendingEmployee

        with app.app_context():
            # Check for our test employee
            pending = PendingEmployee.query.filter_by(
                email=registration_data['new_employee_email']
            ).first()

            if pending:
                print(f"   ✓ Found in database:")
                print(f"     - Name: {pending.name}")
                print(f"     - Team: {pending.team}")
                print(f"     - Position: {pending.position}")
                print(f"     - Status: {pending.status}")
                print(f"     - Submitted at: {pending.submitted_at}")

                if pending.team == registration_data['new_employee_team']:
                    print(f"   ✓ Correctly assigned to {pending.team} team!")
            else:
                print("   ⚠ Not found in database yet")

    except Exception as e:
        print(f"   ⚠ Could not check database: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_employee_registration()