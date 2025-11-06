"""
Check Employee Phone Numbers
Shows which employees have phone numbers configured for Twilio SMS call-outs
"""

import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
from models import TeamMember

def check_phone_numbers():
    """Display all employees and their phone numbers"""

    with app.app_context():
        # Get all team members
        members = TeamMember.query.order_by(TeamMember.name).all()

        if not members:
            print("No employees found in database!")
            return

        print("\n" + "="*70)
        print("  EMPLOYEE PHONE NUMBER STATUS")
        print("="*70)
        print(f"{'Employee Name':<30} {'Team':<12} {'Phone Number':<20}")
        print("-"*70)

        # Track statistics
        has_phone = 0
        no_phone = 0

        for member in members:
            # Get team from position
            team = member.team if member.team else "Unknown"

            # Check phone status
            if member.phone:
                phone_display = member.phone
                status_symbol = "[OK]"
                has_phone += 1
            else:
                phone_display = "NO PHONE"
                status_symbol = "[--]"
                no_phone += 1

            # Display with alignment
            print(f"{status_symbol} {member.name:<28} {team:<12} {phone_display:<20}")

        # Display summary
        print("-"*70)
        print(f"\nSUMMARY:")
        print(f"  Total Employees:     {len(members)}")
        print(f"  [OK] With Phone:     {has_phone}")
        print(f"  [--] Missing Phone:  {no_phone}")

        if no_phone > 0:
            print(f"\n[!] WARNING: {no_phone} employee(s) cannot use SMS call-out feature!")
            print(f"    Run 'python add_phones.py' to add phone numbers.")
        else:
            print(f"\n[OK] All employees have phone numbers configured!")

        print("="*70 + "\n")

if __name__ == "__main__":
    try:
        check_phone_numbers()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        print("Make sure the database is initialized and accessible.")
