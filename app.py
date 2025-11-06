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

        # Initialize positions if they don't exist
        positions_to_create = [
            {'name': 'APP', 'team': 'clinical'},
            {'name': 'CVI RNs', 'team': 'clinical'},
            {'name': 'CVI MOAs', 'team': 'clinical'},
            {'name': 'CVI Echo Techs', 'team': 'clinical'},
            {'name': 'Front Desk/Admin', 'team': 'admin'},
            {'name': 'CT Desk', 'team': 'admin'},
        ]

        for pos_data in positions_to_create:
            existing_pos = Position.query.filter_by(name=pos_data['name']).first()
            if not existing_pos:
                new_pos = Position(name=pos_data['name'], team=pos_data['team'])
                db.session.add(new_pos)
        db.session.commit()

        # Initialize default managers if they don't exist
        from werkzeug.security import generate_password_hash
        
        managers_to_create = [
            {
                'name': 'Admin Manager',
                'email': 'admin.manager@mswcvi.com',
                'role': 'admin',
                'password': 'admin123'
            },
            {
                'name': 'Clinical Manager',
                'email': 'clinical.manager@mswcvi.com', 
                'role': 'clinical',
                'password': 'clinical123'
            },
            {
                'name': 'Super Admin',
                'email': 'superadmin@mswcvi.com',
                'role': 'superadmin', 
                'password': 'super123'
            },
            {
                'name': 'MOA Supervisor',
                'email': 'moa.supervisor@mswcvi.com',
                'role': 'moa_supervisor',
                'password': 'moa123'
            },
            {
                'name': 'Echo Tech Supervisor', 
                'email': 'echo.supervisor@mswcvi.com',
                'role': 'echo_supervisor',
                'password': 'echo123'
            }
        ]
        
        for manager_data in managers_to_create:
            existing_manager = Manager.query.filter_by(email=manager_data['email']).first()
            if not existing_manager:
                new_manager = Manager(
                    name=manager_data['name'],
                    email=manager_data['email'],
                    role=manager_data['role'],
                    password_hash=generate_password_hash(manager_data['password'])
                )
                db.session.add(new_manager)

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