"""
Add/Update Employee Phone Numbers
Interactive script to add phone numbers for Twilio SMS call-out feature
"""

import sys
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app
from models import TeamMember
from database import db
import re

def validate_phone(phone):
    """
    Validate and normalize phone number
    Accepts formats like: +15551234567, 5551234567, (555) 123-4567, etc.
    Returns normalized format: +15551234567
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # Remove leading 1 if present (but not +1)
    if cleaned.startswith('1') and not cleaned.startswith('+'):
        cleaned = cleaned[1:]

    # If it doesn't start with +, add +1
    if not cleaned.startswith('+'):
        cleaned = '+1' + cleaned

    # Validate length (should be +1 followed by 10 digits)
    if len(cleaned) != 12 or not cleaned[1:].isdigit():
        return None

    return cleaned

def display_employees():
    """Display numbered list of employees"""
    members = TeamMember.query.order_by(TeamMember.name).all()

    print("\n" + "="*70)
    print("  EMPLOYEE LIST")
    print("="*70)
    print(f"{'#':<4} {'Employee Name':<30} {'Team':<12} {'Current Phone':<20}")
    print("-"*70)

    for idx, member in enumerate(members, 1):
        team = member.team if member.team else "Unknown"
        phone = member.phone if member.phone else "NO PHONE"
        print(f"{idx:<4} {member.name:<30} {team:<12} {phone:<20}")

    print("-"*70)
    return members

def add_phone_interactive():
    """Interactive session to add/update phone numbers"""

    with app.app_context():
        print("\n" + "="*70)
        print("  ADD/UPDATE EMPLOYEE PHONE NUMBERS")
        print("="*70)
        print("\nThis script helps you add phone numbers for the Twilio SMS call-out feature.")

        while True:
            # Display employees
            members = display_employees()

            if not members:
                print("\n[ERROR] No employees found in database!")
                break

            # Get user selection
            print("\nOptions:")
            print("  - Enter employee number (1-{}) to update".format(len(members)))
            print("  - Type 'done' or 'quit' to exit")
            print("  - Type 'check' to see current status")

            choice = input("\nYour choice: ").strip().lower()

            if choice in ['done', 'quit', 'exit', 'q']:
                print("\n[OK] Exiting. Changes saved!")
                break

            if choice == 'check':
                # Show only employees without phones
                no_phone = [m for m in members if not m.phone]
                if no_phone:
                    print(f"\n[!] {len(no_phone)} employee(s) still need phone numbers:")
                    for m in no_phone:
                        print(f"  - {m.name}")
                else:
                    print("\n[OK] All employees have phone numbers!")
                continue

            # Try to parse as number
            try:
                emp_num = int(choice)
                if emp_num < 1 or emp_num > len(members):
                    print(f"\n[ERROR] Invalid number. Please enter 1-{len(members)}")
                    continue
            except ValueError:
                print("\n[ERROR] Invalid input. Please enter a number or 'done'")
                continue

            # Get selected employee
            selected = members[emp_num - 1]

            print(f"\n[EDIT] Updating: {selected.name}")
            if selected.phone:
                print(f"   Current phone: {selected.phone}")
            else:
                print(f"   Current phone: NO PHONE")

            # Get new phone number
            print("\nEnter phone number (formats accepted):")
            print("  - +15551234567")
            print("  - 5551234567")
            print("  - (555) 123-4567")
            print("  - 555-123-4567")
            print("  (or type 'skip' to skip this employee)")

            phone_input = input("\nPhone number: ").strip()

            if phone_input.lower() in ['skip', 's', '']:
                print("[SKIP] Skipped.")
                continue

            # Validate and normalize
            normalized_phone = validate_phone(phone_input)

            if not normalized_phone:
                print(f"\n[ERROR] Invalid phone number format: {phone_input}")
                print("        Phone must be 10 digits (US/Canada)")
                retry = input("        Try again? (y/n): ").strip().lower()
                if retry == 'y':
                    continue
                else:
                    continue

            # Confirm update
            print(f"\n[OK] Normalized to: {normalized_phone}")
            confirm = input(f"   Update {selected.name} to {normalized_phone}? (y/n): ").strip().lower()

            if confirm == 'y':
                selected.phone = normalized_phone
                db.session.commit()
                print(f"     [OK] Updated successfully!")
            else:
                print(f"     [SKIP] Skipped.")

            # Ask if they want to continue
            print()
            cont = input("Add another phone number? (y/n): ").strip().lower()
            if cont != 'y':
                print("\n[OK] All done! Changes saved.")
                break

        print("\n" + "="*70)
        print("  FINAL STATUS")
        print("="*70)

        # Show final count
        all_members = TeamMember.query.all()
        with_phone = sum(1 for m in all_members if m.phone)
        without_phone = len(all_members) - with_phone

        print(f"\nTotal employees: {len(all_members)}")
        print(f"[OK] With phone:    {with_phone}")
        print(f"[--] Without phone: {without_phone}")

        if without_phone > 0:
            print(f"\n[!] {without_phone} employee(s) still need phone numbers.")
            print("    Run this script again to add more.")
        else:
            print("\n[OK] All employees configured! Ready for Twilio SMS integration.")

        print("\n" + "="*70 + "\n")

def bulk_add_phones():
    """Alternative: Bulk add from dictionary"""
    print("\nBULK ADD MODE")
    print("="*70)
    print("\nTo add multiple phones at once, edit this file (add_phones.py)")
    print("and uncomment the phone_data dictionary below with your data.\n")

    # Example phone data (commented out)
    # Uncomment and fill in to use bulk mode
    """
    phone_data = {
        'John Smith': '+15551234567',
        'Sarah Johnson': '+15559876543',
        'Dr. Michael Chen': '+15558675309',
        # Add more employees...
    }

    with app.app_context():
        for name, phone in phone_data.items():
            member = TeamMember.query.filter_by(name=name).first()
            if member:
                member.phone = phone
                print(f'[OK] Updated {name}: {phone}')
            else:
                print(f'[--] Employee not found: {name}')

        db.session.commit()
        print('\n[OK] All phone numbers saved!')
    """

if __name__ == "__main__":
    try:
        print("\nWelcome to the Employee Phone Number Manager!")
        print("="*70)

        # Check if they want bulk or interactive mode
        print("\nHow would you like to add phone numbers?")
        print("  1. Interactive mode (recommended - add one at a time)")
        print("  2. Bulk mode (edit this script with all numbers)")

        mode = input("\nChoice (1 or 2): ").strip()

        if mode == '2':
            bulk_add_phones()
        else:
            add_phone_interactive()

    except KeyboardInterrupt:
        print("\n\n[STOP] Cancelled by user. Any saved changes remain in database.")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        print("Make sure the database is initialized and accessible.")
