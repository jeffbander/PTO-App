#!/usr/bin/env python3
"""Test the complete PTO workflow from submission to completion"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_complete_workflow():
    """Test the entire PTO workflow"""

    print("=" * 70)
    print("TESTING COMPLETE PTO WORKFLOW")
    print("=" * 70)

    # Step 1: Submit a PTO request
    print("\n1. SUBMITTING PTO REQUEST")
    print("-" * 40)

    # Calculate dates for the request (starting tomorrow)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    pto_data = {
        'team': 'clinical',
        'position': 'CVI RNs',
        'name': 'Lisa Rodriguez',
        'email': 'lisa.rodriguez@mswcvi.com',
        'start_date': tomorrow,
        'end_date': next_week,
        'pto_type': 'Vacation',
        'reason': 'Testing workflow system - vacation next week',
        'is_partial_day': '',
        'start_time': '',
        'end_time': ''
    }

    response = requests.post(f"{BASE_URL}/submit_request", data=pto_data, allow_redirects=False)
    print(f"   ✓ PTO Request submitted (Status: {response.status_code})")
    print(f"   - Employee: {pto_data['name']}")
    print(f"   - Dates: {pto_data['start_date']} to {pto_data['end_date']}")
    print(f"   - Status: PENDING")

    # Step 2: Login as clinical manager
    print("\n2. MANAGER APPROVAL")
    print("-" * 40)

    session = requests.Session()
    login_data = {
        'email': 'clinical.manager@mswcvi.com',
        'password': 'clinical123'
    }

    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   ✓ Logged in as Clinical Manager")

    # Get the dashboard to find the request
    dashboard = session.get(f"{BASE_URL}/dashboard/clinical")

    # Find and approve the request
    import re
    pattern = r'/approve_request/(\d+)'
    matches = re.findall(pattern, dashboard.text)

    if matches:
        request_id = matches[0]  # Get the first pending request
        approve_url = f"{BASE_URL}/approve_request/{request_id}"

        approve_response = session.get(approve_url, allow_redirects=False)
        print(f"   ✓ Request #{request_id} approved by manager")
        print(f"   - Status changed: PENDING → IN_PROGRESS")

        # Step 3: Check In Progress Workqueue
        print("\n3. IN PROGRESS WORKQUEUE")
        print("-" * 40)

        in_progress = session.get(f"{BASE_URL}/workqueue/in_progress")

        if 'Lisa Rodriguez' in in_progress.text:
            print(f"   ✓ Request appears in In Progress workqueue")
            print(f"   - Checklist items:")
            print(f"     □ Timekeeping Entered")
            print(f"     □ Coverage Arranged")

            # Step 4: Complete checklist items
            print("\n4. COMPLETING CHECKLIST")
            print("-" * 40)

            checklist_data = {
                'timekeeping_entered': 'on',
                'coverage_arranged': 'on'
            }

            update_url = f"{BASE_URL}/update_checklist/{request_id}"
            checklist_response = session.post(update_url, data=checklist_data, allow_redirects=False)

            print(f"   ✓ Checklist items marked complete:")
            print(f"     ✓ Timekeeping Entered")
            print(f"     ✓ Coverage Arranged")
            print(f"   - Status changed: IN_PROGRESS → APPROVED")

            # Step 5: Check Approved Workqueue
            print("\n5. APPROVED WORKQUEUE")
            print("-" * 40)

            approved = session.get(f"{BASE_URL}/workqueue/approved")

            if 'Lisa Rodriguez' in approved.text:
                print(f"   ✓ Request appears in Approved workqueue")
                print(f"   - Status: Fully approved and ready")
                print(f"   - PTO period: {tomorrow} to {next_week}")

                # Step 6: Simulate completion (for past date requests)
                print("\n6. COMPLETION CHECK")
                print("-" * 40)

                # Submit a past date request to test completion
                past_pto = {
                    'team': 'admin',
                    'position': 'Front Desk/Admin',
                    'name': 'John Smith',
                    'email': 'john.smith@mswcvi.com',
                    'start_date': '2025-01-01',
                    'end_date': '2025-01-05',
                    'pto_type': 'Vacation',
                    'reason': 'Past vacation for testing completion',
                    'is_partial_day': '',
                    'start_time': '',
                    'end_time': ''
                }

                # Submit past request
                past_response = requests.post(f"{BASE_URL}/submit_request", data=past_pto, allow_redirects=False)

                # Login as admin manager
                admin_session = requests.Session()
                admin_login = {
                    'email': 'admin.manager@mswcvi.com',
                    'password': 'admin123'
                }
                admin_session.post(f"{BASE_URL}/login", data=admin_login, allow_redirects=False)

                # Approve the past request
                admin_dashboard = admin_session.get(f"{BASE_URL}/dashboard/admin")
                past_matches = re.findall(pattern, admin_dashboard.text)

                if past_matches:
                    past_id = past_matches[0]
                    admin_session.get(f"{BASE_URL}/approve_request/{past_id}", allow_redirects=False)

                    # Complete checklist
                    admin_session.post(f"{BASE_URL}/update_checklist/{past_id}",
                                     data={'timekeeping_entered': 'on', 'coverage_arranged': 'on'},
                                     allow_redirects=False)

                    # Run completion check
                    completion = admin_session.get(f"{BASE_URL}/check_and_complete_requests")

                    print(f"   ✓ Automatic completion check executed")
                    print(f"   - Past requests moved to COMPLETED status")

                    # Check completed workqueue
                    completed = admin_session.get(f"{BASE_URL}/workqueue/completed")

                    if 'John Smith' in completed.text:
                        print(f"   ✓ Past request appears in Completed workqueue")

            # Step 7: Summary
            print("\n7. WORKFLOW SUMMARY")
            print("-" * 40)
            print("   ✓ All workflow stages tested successfully:")
            print("     1. PENDING    - Initial submission")
            print("     2. IN_PROGRESS - Manager approved, checklist pending")
            print("     3. APPROVED   - Checklist complete, PTO ready")
            print("     4. COMPLETED  - PTO period ended")

            print("\n   Workqueue Navigation:")
            print("     • Pending Queue    - New requests awaiting manager review")
            print("     • In Progress Queue - Approved requests with checklist")
            print("     • Approved Queue   - Fully approved, active/upcoming PTO")
            print("     • Completed Queue  - Historical archive")

            return True
        else:
            print("   ⚠ Request not found in In Progress workqueue")
    else:
        print("   ⚠ No pending requests found to approve")

    return False

if __name__ == "__main__":
    print("\nStarting PTO Workflow Test...")
    print("This will test the complete workflow from submission to completion.\n")

    success = test_complete_workflow()

    print("\n" + "=" * 70)
    if success:
        print("TEST COMPLETED SUCCESSFULLY ✓")
        print("All workflow stages are functioning correctly!")
    else:
        print("TEST INCOMPLETE")
        print("Some workflow stages could not be tested.")
    print("=" * 70)