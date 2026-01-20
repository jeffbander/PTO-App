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

def run_migrations():
    """Add new columns to existing tables if they don't exist"""
    from sqlalchemy import text, inspect

    # List of migrations: (table, column, type, default)
    migrations = [
        ('users', 'starting_pto_hours', 'NUMERIC(5,2)', '60.0'),
        ('users', 'starting_sick_hours', 'NUMERIC(5,2)', '60.0'),
    ]

    try:
        inspector = inspect(db.engine)
        existing_columns = {col['name'] for col in inspector.get_columns('users')}
    except Exception as e:
        print(f'Could not inspect database: {e}')
        existing_columns = set()

    for table, column, col_type, default in migrations:
        if column in existing_columns:
            print(f'Column {column} already exists in {table}')
            continue

        try:
            db.session.execute(text(
                f'ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}'
            ))
            db.session.commit()
            print(f'Added column {column} to {table}')
        except Exception as e:
            db.session.rollback()
            print(f'Could not add column {column} to {table}: {e}')

def migrate_admin_positions():
    """Migrate old admin positions (Front Desk, CT Desk, etc.) to Secretary II"""
    # Get Secretary II position
    secretary_pos = Position.query.filter_by(name='Secretary II', team='admin').first()
    if not secretary_pos:
        print('Secretary II position not found, skipping migration')
        return

    # Old admin positions to migrate
    old_positions = ['Front Desk/Admin', 'CT Desk', 'Front Desk Coordinator', 'Admin Assistant']

    for old_name in old_positions:
        old_pos = Position.query.filter_by(name=old_name).first()
        if old_pos:
            # Update all team members with this position to Secretary II
            members_updated = TeamMember.query.filter_by(position_id=old_pos.id).update(
                {'position_id': secretary_pos.id}
            )
            if members_updated > 0:
                print(f'Migrated {members_updated} employees from {old_name} to Secretary II')

            # Delete the old position
            db.session.delete(old_pos)
            print(f'Deleted old position: {old_name}')

    db.session.commit()

def initialize_database():
    with app.app_context():
        # Create tables if they don't exist (but don't drop existing data)
        # WARNING: Only use db.drop_all() during development if you need to reset schema
        # db.drop_all()  # COMMENTED OUT - Enable ONLY to update schema during development
        db.create_all()

        # Run migrations to add new columns to existing tables
        run_migrations()

        # Initialize positions if they don't exist
        positions_to_create = [
            {'name': 'APP', 'team': 'clinical'},
            {'name': 'CVI RNs', 'team': 'clinical'},
            {'name': 'CVI MOAs', 'team': 'clinical'},
            {'name': 'CVI Echo Techs', 'team': 'clinical'},
            {'name': 'Secretary II', 'team': 'admin'},
            {'name': 'Leadership', 'team': 'admin'},
            {'name': 'Other', 'team': 'admin'},
        ]

        for pos_data in positions_to_create:
            existing_pos = Position.query.filter_by(name=pos_data['name']).first()
            if not existing_pos:
                new_pos = Position(name=pos_data['name'], team=pos_data['team'])
                db.session.add(new_pos)
        db.session.commit()

        # Migrate old admin positions to Secretary II
        migrate_admin_positions()

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