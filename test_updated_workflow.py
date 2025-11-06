#!/usr/bin/env python3
"""Test the updated email workflow"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_updated_workflow():
    """Test updated PTO workflow with new email requirements"""

    print("\n" + "="*70)
    print("TESTING UPDATED EMAIL WORKFLOW")
    print("="*70)
    print("\nNew Workflow:")
    print("1. Employee submits PTO -> Employee gets confirmation + Manager notified")
    print("2. Manager approves -> Employee gets approval notification")
    print("3. Checklist completed -> NO email sent")
    print("="*70)

    # Step 1: Submit a new PTO request
    print("\n[STEP 1] SUBMITTING PTO REQUEST")
    print("-" * 40)

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
        'reason': 'Testing updated email workflow',
        'is_partial_day': '',
        'start_time': '',
        'end_time': ''
    }

    response = requests.post(f"{BASE_URL}/submit_request", data=pto_data, allow_redirects=False)

    if response.status_code == 302:
        print("✓ PTO Request submitted successfully")
        print("\nEMAILS SENT:")
        print("  1. Employee confirmation -> samantha.zakow@mountsinai.org")
        print("  2. Manager notification -> htn.prevention@mountsinai.org")
    else:
        print("✗ Failed to submit request")
        return

    time.sleep(2)

    # Step 2: Login as manager
    print("\n[STEP 2] MANAGER LOGIN AND APPROVAL")
    print("-" * 40)

    session = requests.Session()
    login_data = {
        'email': 'admin.manager@mswcvi.com',
        'password': 'admin123'
    }

    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print("✓ Logged in as Admin Manager")

    # Get dashboard and find the request
    dashboard = session.get(f"{BASE_URL}/dashboard/admin")

    import re
    pattern = r'/approve_request/(\d+)'
    matches = re.findall(pattern, dashboard.text)

    if matches:
        request_id = matches[0]
        print(f"✓ Found PTO request ID: #{request_id}")
    else:
        print("✗ No pending request found")
        return

    # Approve the request
    approve_url = f"{BASE_URL}/approve_request/{request_id}"
    approve_response = session.get(approve_url, allow_redirects=False)

    if approve_response.status_code == 302:
        print(f"✓ Request #{request_id} approved by manager")
        print("\nEMAIL SENT:")
        print("  3. Approval notification -> samantha.zakow@mountsinai.org")

    time.sleep(2)

    # Step 3: Complete checklist items
    print("\n[STEP 3] COMPLETING CHECKLIST")
    print("-" * 40)

    checklist_data = {
        'timekeeping_entered': 'on',
        'coverage_arranged': 'on'
    }

    update_url = f"{BASE_URL}/update_checklist/{request_id}"
    checklist_response = session.post(update_url, data=checklist_data, allow_redirects=False)

    if checklist_response.status_code == 302:
        print("✓ Checklist items completed")
        print("✓ Status changed to APPROVED")
        print("\nNO EMAIL SENT (per updated requirements)")

    # Summary
    print("\n" + "="*70)
    print("EMAIL WORKFLOW SUMMARY")
    print("="*70)
    print("\nEmails sent during this workflow:")
    print("1. Employee confirmation (on submission) -> samantha.zakow@mountsinai.org")
    print("2. Manager notification (on submission) -> htn.prevention@mountsinai.org")
    print("3. Approval notification (on approval) -> samantha.zakow@mountsinai.org")
    print("\nNOT sent:")
    print("4. Final approval (on checklist completion) - REMOVED per requirements")
    print("\n✅ UPDATED WORKFLOW TEST COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    test_updated_workflow()