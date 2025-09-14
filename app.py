import os
import logging
from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db
from models import User, TeamMember, PTORequest, Manager, Position

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
        # Drop all tables and recreate them
        db.drop_all()
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

# Import and register routes
from routes_simple import register_routes
register_routes(app)

with app.app_context():
    initialize_database()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)