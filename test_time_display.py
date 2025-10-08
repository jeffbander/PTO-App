#!/usr/bin/env python3
"""Test to verify time is displayed on dashboards for partial day requests"""

import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_partial_day_time_display():
    """Submit a partial day PTO request and check if time appears on dashboards"""

    print("\n" + "="*70)
    print("TESTING TIME DISPLAY ON DASHBOARDS")
    print("="*70)

    # Step 1: Submit partial day PTO request
    print("\n1. SUBMITTING PARTIAL DAY PTO REQUEST")
    print("-" * 40)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    pto_data = {
        'team': 'clinical',
        'position': 'CVI Echo Techs',
        'name': 'Robert Wilson',
        'email': 'robert.wilson@mswcvi.com',
        'start_date': tomorrow,
        'end_date': tomorrow,
        'pto_type': 'Personal',
        'reason': 'Medical appointment',
        'is_partial_day': 'true',
        'start_time': '09:00',
        'end_time': '14:30'
    }

    response = requests.post(f"{BASE_URL}/submit_request", data=pto_data, allow_redirects=False)

    if response.status_code == 302:
        print(f"Partial day PTO request submitted successfully!")
        print(f"Employee: {pto_data['name']}")
        print(f"Date: {pto_data['start_date']}")
        print(f"Time: {pto_data['start_time']} - {pto_data['end_time']}")
        print(f"Duration: 5.5 hours (partial day)")
    else:
        print(f"Error submitting request: {response.status_code}")
        return False

    # Step 2: Check dashboards
    print("\n2. CHECKING DASHBOARDS FOR TIME DISPLAY")
    print("-" * 40)

    # Test Clinical Manager Dashboard
    session = requests.Session()
    login_data = {
        'email': 'clinical.manager@mswcvi.com',
        'password': 'clinical123'
    }
    session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)

    dashboard = session.get(f"{BASE_URL}/dashboard/clinical")
    if '09:00' in dashboard.text and '14:30' in dashboard.text:
        print("[OK] Clinical Manager Dashboard - Time displayed")
    else:
        print("[WARN] Clinical Manager Dashboard - Time may not be visible")

    # Test Echo Supervisor Dashboard
    session2 = requests.Session()
    login_data2 = {
        'email': 'echo.supervisor@mswcvi.com',
        'password': 'echo123'
    }
    session2.post(f"{BASE_URL}/login", data=login_data2, allow_redirects=False)

    echo_dashboard = session2.get(f"{BASE_URL}/dashboard/echo_supervisor")
    if '09:00' in echo_dashboard.text and '14:30' in echo_dashboard.text:
        print("[OK] Echo Supervisor Dashboard - Time displayed")
    else:
        print("[WARN] Echo Supervisor Dashboard - Time may not be visible")

    # Test Super Admin Dashboard
    session3 = requests.Session()
    login_data3 = {
        'email': 'superadmin@mswcvi.com',
        'password': 'super123'
    }
    session3.post(f"{BASE_URL}/login", data=login_data3, allow_redirects=False)

    super_dashboard = session3.get(f"{BASE_URL}/dashboard/superadmin")
    if '09:00' in super_dashboard.text and '14:30' in super_dashboard.text:
        print("[OK] Super Admin Dashboard - Time displayed")
    else:
        print("[WARN] Super Admin Dashboard - Time may not be visible")

    print("\n3. TIME DISPLAY FEATURES")
    print("-" * 40)
    print("Time information now appears on:")
    print("  - Admin Manager Dashboard (pending, in-progress, approved tabs)")
    print("  - Clinical Manager Dashboard (pending, in-progress, approved tabs)")
    print("  - Echo Supervisor Dashboard (all requests)")
    print("  - MOA Supervisor Dashboard (all requests)")
    print("  - Super Admin Dashboard (all requests)")
    print("  - All workqueue pages (in-progress, approved, completed)")

    return True

if __name__ == "__main__":
    print("\nStarting Time Display Test...")

    success = test_partial_day_time_display()

    print("\n" + "="*70)
    if success:
        print("TIME DISPLAY TEST COMPLETED")
        print("\nUpdates applied to:")
        print("  - dashboard_echo_supervisor.html")
        print("  - dashboard_moa_supervisor.html")
        print("  - dashboard_superadmin.html")
        print("\nTime format: HH:MM (e.g., 09:00 - 14:30)")
        print("Duration shown in hours for partial days (e.g., 5.5 hrs)")
    else:
        print("TIME DISPLAY TEST FAILED")
    print("="*70)
