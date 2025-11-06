"""
Migration script to add sick_balance_hours column to users table.
Run this script if you want to add the new column without recreating the entire database.

Usage: python migrate_add_sick_balance.py
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
    """Add sick_balance_hours column to users table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]

            if 'sick_balance_hours' in columns:
                print("✅ Column 'sick_balance_hours' already exists in users table.")
                return

            # Add the new column with default value of 60.0 hours
            print("Adding 'sick_balance_hours' column to users table...")
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN sick_balance_hours NUMERIC(5,2) DEFAULT 60.0
            """))
            db.session.commit()
            print("✅ Successfully added 'sick_balance_hours' column to users table.")

            # Update existing records to have 60.0 hours sick balance
            print("Updating existing users with default sick balance...")
            db.session.execute(text("""
                UPDATE users
                SET sick_balance_hours = 60.0
                WHERE sick_balance_hours IS NULL
            """))
            db.session.commit()
            print("✅ Successfully updated existing users with default sick balance.")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("Starting migration...")
    migrate()
    print("Migration complete!")
