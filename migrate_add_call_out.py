"""
Migration script to add is_call_out column to pto_requests table.
Run this script if you want to add the new column without recreating the entire database.

Usage: python migrate_add_call_out.py
"""
import os
from flask import Flask
from database import db
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///pto_tracker.db")

# Initialize database
db.init_app(app)

def migrate():
    """Add is_call_out column to pto_requests table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(pto_requests)"))
            columns = [row[1] for row in result]

            if 'is_call_out' in columns:
                print("✅ Column 'is_call_out' already exists in pto_requests table.")
                return

            # Add the new column
            print("Adding 'is_call_out' column to pto_requests table...")
            db.session.execute(text("""
                ALTER TABLE pto_requests
                ADD COLUMN is_call_out BOOLEAN DEFAULT 0
            """))
            db.session.commit()
            print("✅ Successfully added 'is_call_out' column to pto_requests table.")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("Starting migration...")
    migrate()
    print("Migration complete!")
