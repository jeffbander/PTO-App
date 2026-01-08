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

        # Initialize default managers in Manager table
        from werkzeug.security import generate_password_hash

        managers_to_create = [
            {
                'name': 'Lauryn Padron',
                'email': 'lauryn.padron@mountsinai.org',
                'role': 'admin',
                'password': 'Carlostylermila5!'
            },
            {
                'name': 'Ashley Stark',
                'email': 'ashley.stark@mountsinai.org',
                'role': 'clinical',
                'password': 'Heart123!'
            },
            {
                'name': 'Samantha Zakow',
                'email': 'htn.prevention@mountsinai.org',
                'role': 'superadmin',
                'password': 'Password123'
            }
        ]

        for manager_data in managers_to_create:
            # Check if manager already exists by email
            existing_manager = Manager.query.filter_by(email=manager_data['email']).first()

            if existing_manager:
                # Update existing manager
                existing_manager.name = manager_data['name']
                existing_manager.password_hash = generate_password_hash(manager_data['password'])
                existing_manager.role = manager_data['role']
                print(f"Updated Manager {manager_data['name']}")
            else:
                # Check if email exists as any other user type
                existing_user = User.query.filter_by(email=manager_data['email']).first()
                if existing_user:
                    print(f"Warning: Cannot create manager - email {manager_data['email']} already in use")
                    continue

                # Create new manager
                new_manager = Manager(
                    name=manager_data['name'],
                    email=manager_data['email'],
                    role=manager_data['role'],
                    password_hash=generate_password_hash(manager_data['password'])
                )
                db.session.add(new_manager)
                print(f"Created Manager {manager_data['name']} as {manager_data['role']}")

        db.session.commit()

        # Sample employee and PTO request creation disabled - using real employee data
        # To re-enable sample data, uncomment the code in this section
        print("Database initialization complete (sample data creation disabled)")

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