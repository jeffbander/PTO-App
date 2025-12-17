import os
import logging
from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db
from models import User, TeamMember, PTORequest, Manager, Position
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///pto_tracker.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

def initialize_database():
    with app.app_context():
        # Create tables if they don't exist (but don't drop existing data)
        # WARNING: Only use db.drop_all() during development if you need to reset schema
        # db.drop_all()  # COMMENTED OUT - Enable ONLY to update schema during development
        db.create_all()

        # Add new columns to team_members table if they don't exist (for Leadership feature)
        try:
            from sqlalchemy import text
            # Check if columns exist and add them if not (PostgreSQL compatible)
            db.session.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                   WHERE table_name='team_members' AND column_name='password_hash') THEN
                        ALTER TABLE team_members ADD COLUMN password_hash VARCHAR(256);
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                   WHERE table_name='team_members' AND column_name='role') THEN
                        ALTER TABLE team_members ADD COLUMN role VARCHAR(30);
                    END IF;
                END $$;
            """))
            db.session.commit()
            print("Database migration for Leadership columns completed")
        except Exception as e:
            # SQLite doesn't support DO blocks, try SQLite-compatible migration
            try:
                db.session.rollback()
                # For SQLite - check columns differently
                result = db.session.execute(text("PRAGMA table_info(team_members)"))
                columns = [row[1] for row in result.fetchall()]
                if 'password_hash' not in columns:
                    db.session.execute(text("ALTER TABLE team_members ADD COLUMN password_hash VARCHAR(256)"))
                if 'role' not in columns:
                    db.session.execute(text("ALTER TABLE team_members ADD COLUMN role VARCHAR(30)"))
                db.session.commit()
                print("SQLite migration for Leadership columns completed")
            except Exception as e2:
                db.session.rollback()
                print(f"Migration note: {e2}")

        # Initialize positions if they don't exist
        positions_to_create = [
            {'name': 'APP', 'team': 'clinical'},
            {'name': 'CVI RNs', 'team': 'clinical'},
            {'name': 'CVI MOAs', 'team': 'clinical'},
            {'name': 'CVI Echo Techs', 'team': 'clinical'},
            {'name': 'Front Desk/Admin', 'team': 'admin'},
            {'name': 'CT Desk', 'team': 'admin'},
            {'name': 'Leadership - Admin', 'team': 'admin'},
            {'name': 'Leadership - Clinical', 'team': 'clinical'},
        ]

        for pos_data in positions_to_create:
            existing_pos = Position.query.filter_by(name=pos_data['name']).first()
            if not existing_pos:
                new_pos = Position(name=pos_data['name'], team=pos_data['team'])
                db.session.add(new_pos)
        db.session.commit()

        # Initialize default managers as Leadership TeamMembers (they can submit PTO and login)
        from werkzeug.security import generate_password_hash

        # Get Leadership positions
        leadership_admin = Position.query.filter_by(name='Leadership - Admin').first()
        leadership_clinical = Position.query.filter_by(name='Leadership - Clinical').first()

        managers_to_create = [
            {
                'name': 'Lauryn Padron',
                'email': 'lauryn.padron@mountsinai.org',
                'role': 'admin',
                'password': 'Carlostylermila5!',
                'position': leadership_admin
            },
            {
                'name': 'Ashley Stark',
                'email': 'ashley.stark@mountsinai.org',
                'role': 'clinical',
                'password': 'Heart123!',
                'position': leadership_clinical
            },
            {
                'name': 'Samantha Zakow',
                'email': 'samantha.zakow@mountsinai.org',
                'role': 'superadmin',
                'password': 'Password123',
                'position': leadership_admin  # Superadmin under admin leadership
            }
        ]

        for manager_data in managers_to_create:
            # Check if this person already exists as a TeamMember
            existing_member = TeamMember.query.filter_by(email=manager_data['email']).first()

            if existing_member:
                # Update existing TeamMember with login credentials
                existing_member.name = manager_data['name']
                existing_member.password_hash = generate_password_hash(manager_data['password'])
                existing_member.role = manager_data['role']
                if manager_data['position']:
                    existing_member.position_id = manager_data['position'].id
                print(f"Updated TeamMember {manager_data['name']} with leadership credentials")
            else:
                # Check if email exists as any other user type
                existing_user = User.query.filter_by(email=manager_data['email']).first()
                if existing_user:
                    print(f"Warning: Cannot create {manager_data['role']} - email {manager_data['email']} already in use by another user type")
                    continue

                # Create new TeamMember with leadership role
                if manager_data['position']:
                    new_member = TeamMember(
                        name=manager_data['name'],
                        email=manager_data['email'],
                        position_id=manager_data['position'].id,
                        password_hash=generate_password_hash(manager_data['password']),
                        role=manager_data['role'],
                        pto_balance_hours=60.0,
                        sick_balance_hours=60.0
                    )
                    db.session.add(new_member)
                    print(f"Created TeamMember {manager_data['name']} as {manager_data['role']} leadership")

        db.session.commit()

        # Add sample employees for testing
        sample_employees = [
            {'name': 'John Smith', 'email': 'john.smith@mswcvi.com', 'team': 'admin', 'position': 'Front Desk/Admin', 'pto_balance': 120.0},
            {'name': 'Sarah Johnson', 'email': 'sarah.johnson@mswcvi.com', 'team': 'admin', 'position': 'CT Desk', 'pto_balance': 80.0},
            {'name': 'Dr. Michael Chen', 'email': 'michael.chen@mswcvi.com', 'team': 'clinical', 'position': 'APP', 'pto_balance': 160.0},
            {'name': 'Lisa Rodriguez', 'email': 'lisa.rodriguez@mswcvi.com', 'team': 'clinical', 'position': 'CVI RNs', 'pto_balance': 100.0},
            {'name': 'Emily Davis', 'email': 'emily.davis@mswcvi.com', 'team': 'clinical', 'position': 'CVI MOAs', 'pto_balance': 90.0},
            {'name': 'Robert Wilson', 'email': 'robert.wilson@mswcvi.com', 'team': 'clinical', 'position': 'CVI Echo Techs', 'pto_balance': 75.0},
            {'name': 'Amanda Thompson', 'email': 'amanda.thompson@mswcvi.com', 'team': 'clinical', 'position': 'CVI RNs', 'pto_balance': 110.0},
            {'name': 'David Brown', 'email': 'david.brown@mswcvi.com', 'team': 'clinical', 'position': 'CVI MOAs', 'pto_balance': 85.0},
        ]

        for emp_data in sample_employees:
            existing_employee = TeamMember.query.filter_by(email=emp_data['email']).first()
            if not existing_employee:
                # Find the position object
                position = Position.query.filter_by(name=emp_data['position'], team=emp_data['team']).first()
                if position:
                    new_employee = TeamMember(
                        name=emp_data['name'],
                        email=emp_data['email'],
                        position_id=position.id,
                        pto_balance_hours=emp_data['pto_balance']
                    )
                    db.session.add(new_employee)

        db.session.commit()

        # Add sample PTO requests for testing admin approval interface (only if database is empty)
        # This prevents duplicate sample data from being added on every restart
        existing_requests_count = PTORequest.query.count()
        if existing_requests_count > 0:
            print(f"Database already has {existing_requests_count} PTO requests, skipping sample data creation")
            return

        from datetime import datetime, date, timedelta

        sample_pto_requests = [
            {
                'employee_email': 'john.smith@mswcvi.com',
                'start_date': '2025-09-18',  # Thursday
                'end_date': '2025-09-23',    # Tuesday (includes weekend)
                'pto_type': 'Vacation',
                'reason': 'Long weekend vacation (Thu-Tue)',
                'manager_team': 'admin'
            },
            {
                'employee_email': 'sarah.johnson@mswcvi.com',
                'start_date': '2025-11-27',  # Thursday (Thanksgiving)
                'end_date': '2025-11-28',    # Friday (after Thanksgiving)
                'pto_type': 'Personal',
                'reason': 'Thanksgiving weekend',
                'manager_team': 'admin'
            },
            {
                'employee_email': 'lisa.rodriguez@mswcvi.com',
                'start_date': '2025-12-24',  # Wednesday
                'end_date': '2025-12-26',    # Friday (includes Christmas)
                'pto_type': 'Vacation',
                'reason': 'Christmas holiday period',
                'manager_team': 'clinical'
            },
            {
                'employee_email': 'john.smith@mswcvi.com',
                'start_date': '2025-07-03',  # Thursday
                'end_date': '2025-07-07',    # Monday (includes July 4th)
                'pto_type': 'Personal',
                'reason': 'July 4th extended weekend',
                'manager_team': 'admin'
            },
            {
                'employee_email': 'emily.davis@mswcvi.com',
                'start_date': '2025-09-16',  # Tuesday
                'end_date': '2025-09-16',    # Tuesday (single business day)
                'pto_type': 'Personal',
                'reason': 'Child school event',
                'manager_team': 'clinical'
            },
            {
                'employee_email': 'david.brown@mswcvi.com',
                'start_date': '2025-05-26',  # Monday (Memorial Day)
                'end_date': '2025-05-27',    # Tuesday
                'pto_type': 'Vacation',
                'reason': 'Memorial Day weekend',
                'manager_team': 'clinical'
            },
            {
                'employee_email': 'amanda.thompson@mswcvi.com',
                'start_date': '2025-09-30',  # Tuesday
                'end_date': '2025-09-30',    # Tuesday (single business day)
                'pto_type': 'Sick',
                'reason': 'Medical appointment',
                'manager_team': 'clinical'
            }
        ]

        for pto_data in sample_pto_requests:
            # Find the team member by email
            member = TeamMember.query.filter_by(email=pto_data['employee_email']).first()
            if member:
                # Check if request already exists
                existing_request = PTORequest.query.filter_by(
                    member_id=member.id,
                    start_date=pto_data['start_date']
                ).first()
                if not existing_request:
                    new_request = PTORequest(
                        member_id=member.id,
                        start_date=pto_data['start_date'],
                        end_date=pto_data['end_date'],
                        pto_type=pto_data['pto_type'],
                        reason=pto_data['reason'],
                        manager_team=pto_data['manager_team'],
                        status='pending'
                    )
                    db.session.add(new_request)

        db.session.commit()
        print(f"Database initialized with {len(sample_employees)} employees and {len(sample_pto_requests)} PTO requests")

# Import and register routes
from routes_simple import register_routes
register_routes(app)

# Register Twilio routes for call-out feature
from routes_twilio import register_twilio_routes
register_twilio_routes(app)

with app.app_context():
    initialize_database()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)