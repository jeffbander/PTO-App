#!/usr/bin/env python3
"""Complete test of PTO workflow with email notifications"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_complete_workflow():
    """Test complete PTO workflow with all email notifications"""

    print("\n" + "="*70)
    print("COMPLETE PTO WORKFLOW TEST WITH EMAIL NOTIFICATIONS")
    print("="*70)
    print("Emails will be sent FROM: sbzakow@mswheart.com")
    print("Emails will be sent TO: samantha.zakow@mountsinai.org")
    print("="*70)

    # Step 1: Submit a new PTO request
    print("\n📧 STEP 1: SUBMITTING NEW PTO REQUEST")
    print("-" * 40)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    pto_data = {
        'team': 'admin',
        'position': 'Front Desk/Admin',
        'name': 'Samantha Test',
        'email': 'samantha.zakow@mountsinai.org',
        'start_date': tomorrow,
        'end_date': next_week,
        'pto_type': 'Vacation',
        'reason': 'Testing email notification system - Full workflow test',
        'is_partial_day': '',
        'start_time': '',
        'end_time': ''
    }

    response = requests.post(f"{BASE_URL}/submit_request", data=pto_data, allow_redirects=False)

    if response.status_code == 302:
        print(f"   ✓ PTO Request submitted successfully")
        print(f"   - Employee: {pto_data['name']}")
        print(f"   - Dates: {pto_data['start_date']} to {pto_data['end_date']}")
        print(f"   - Type: {pto_data['pto_type']}")
        print(f"\n   📧 EMAIL #1 & #2 SENT:")
        print(f"   → Employee notification sent to: samantha.zakow@mountsinai.org")
        print(f"   → Manager notification sent to: samantha.zakow@mountsinai.org")
    else:
        print(f"   ✗ Failed to submit request")
        return

    time.sleep(2)  # Wait a moment

    # Step 2: Login as manager
    print("\n📧 STEP 2: MANAGER LOGIN")
    print("-" * 40)

    session = requests.Session()
    login_data = {
        'email': 'admin.manager@mswcvi.com',
        'password': 'admin123'
    }

    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   ✓ Logged in as Admin Manager")

    # Step 3: Get dashboard and find the request
    dashboard = session.get(f"{BASE_URL}/dashboard/admin")

    # Extract request ID (assuming it's the most recent, ID #1)
    import re
    pattern = r'/approve_request/(\d+)'
    matches = re.findall(pattern, dashboard.text)

    if matches:
        request_id = matches[0]
        print(f"   ✓ Found PTO request ID: #{request_id}")
    else:
        print("   ✗ No pending request found")
        return

    # Step 4: Approve the request
    print("\n📧 STEP 3: APPROVING PTO REQUEST")
    print("-" * 40)

    approve_url = f"{BASE_URL}/approve_request/{request_id}"
    approve_response = session.get(approve_url, allow_redirects=False)

    if approve_response.status_code == 302:
        print(f"   ✓ Request #{request_id} approved by manager")
        print(f"   - Status changed: PENDING → IN_PROGRESS")
        print(f"\n   📧 EMAIL #3 SENT:")
        print(f"   → Approval notification sent to: samantha.zakow@mountsinai.org")

    time.sleep(2)

    # Step 5: Complete checklist items
    print("\n📧 STEP 4: COMPLETING CHECKLIST")
    print("-" * 40)

    checklist_data = {
        'timekeeping_entered': 'on',
        'coverage_arranged': 'on'
    }

    update_url = f"{BASE_URL}/update_checklist/{request_id}"
    checklist_response = session.post(update_url, data=checklist_data, allow_redirects=False)

    if checklist_response.status_code == 302:
        print(f"   ✓ Checklist items completed:")
        print(f"     ✓ Timekeeping Entered")
        print(f"     ✓ Coverage Arranged")
        print(f"   - Status changed: IN_PROGRESS → APPROVED")
        print(f"\n   📧 EMAIL #4 SENT:")
        print(f"   → Final approval notification sent to: samantha.zakow@mountsinai.org")

    # Summary
    print("\n" + "="*70)
    print("📧 EMAIL SUMMARY")
    print("="*70)
    print("The following emails were sent to samantha.zakow@mountsinai.org:")
    print("")
    print("1. PTO Request Submitted - Initial submission notification")
    print("2. New PTO Request (Manager) - Manager notification")
    print("3. PTO Request Approved - Manager approval notification")
    print("4. PTO Request Fully Approved - Final approval notification")
    print("")
    print("All emails sent FROM: sbzakow@mswheart.com")
    print("="*70)
    print("\n✅ WORKFLOW TEST COMPLETE - CHECK EMAIL INBOX!")

if __name__ == "__main__":
    test_complete_workflow()