"""
Database Migration Script: Add SMS Recipients table
Creates the sms_recipients table and seeds it from the current
MANAGER_ADMIN_SMS and MANAGER_CLINICAL_SMS environment variables.

The number 6465565559 is explicitly excluded during seeding.
"""

import os
from app import app
from database import db
from models import SMSRecipient
from sqlalchemy import inspect

EXCLUDED_NUMBERS = {'6465565559', '+16465565559', '16465565559'}


def _digits(raw):
    return ''.join(ch for ch in (raw or '') if ch.isdigit())


def migrate_database():
    with app.app_context():
        print("=" * 60)
        print("Database Migration: SMS Recipients")
        print("=" * 60)

        inspector = inspect(db.engine)
        if 'sms_recipients' not in inspector.get_table_names():
            print("\nCreating sms_recipients table...")
            SMSRecipient.__table__.create(bind=db.engine)
            print("  -> sms_recipients table created")
        else:
            print("\nsms_recipients table already exists")

        # Seed from env vars (admin + clinical) if table is empty
        existing_count = SMSRecipient.query.count()
        if existing_count > 0:
            print(f"\nTable already has {existing_count} recipients. Skipping seed.")
            return

        seed_entries = []
        admin_raw = os.getenv('MANAGER_ADMIN_SMS', '')
        clinical_raw = os.getenv('MANAGER_CLINICAL_SMS', '')

        for phone in [p.strip() for p in admin_raw.split(',') if p.strip()]:
            if _digits(phone) in EXCLUDED_NUMBERS or phone in EXCLUDED_NUMBERS:
                print(f"  -> skipping excluded number {phone}")
                continue
            seed_entries.append(('Admin Manager', phone, 'admin'))

        for phone in [p.strip() for p in clinical_raw.split(',') if p.strip()]:
            if _digits(phone) in EXCLUDED_NUMBERS or phone in EXCLUDED_NUMBERS:
                print(f"  -> skipping excluded number {phone}")
                continue
            seed_entries.append(('Clinical Manager', phone, 'clinical'))

        if not seed_entries:
            print("\nNo env-configured numbers to seed. Table left empty.")
            print("Add recipients via the admin UI at /sms-recipients.")
            return

        for name, phone, team in seed_entries:
            normalized = SMSRecipient.normalize_phone(phone)
            recipient = SMSRecipient(
                name=name,
                phone=normalized,
                team=team,
                active=True,
            )
            db.session.add(recipient)
            print(f"  -> seeded {team}: {normalized}")

        db.session.commit()
        print("\nSeed complete.")

        print("\n" + "=" * 60)
        print("SUCCESS")
        print("=" * 60)


if __name__ == "__main__":
    migrate_database()
