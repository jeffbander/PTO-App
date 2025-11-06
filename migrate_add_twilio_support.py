"""
Database Migration Script: Add Twilio Call-Out Support
Adds PIN field to users table and creates call_out_records table
"""

from app import app
from database import db
from sqlalchemy import text

def migrate_database():
    """Add Twilio-related fields and tables to the database"""

    with app.app_context():
        print("=" * 60)
        print("Database Migration: Adding Twilio Call-Out Support")
        print("=" * 60)

        try:
            # Check if 'pin' column already exists in users table
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]

            if 'pin' not in columns:
                print("\nAdding 'pin' column to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN pin VARCHAR(4)"))
                db.session.commit()
                print("  -> PIN column added successfully")
            else:
                print("\nPIN column already exists in users table")

            # Check if call_out_records table exists
            result = db.session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='call_out_records'"
            ))
            table_exists = result.fetchone() is not None

            if not table_exists:
                print("\nCreating call_out_records table...")

                # Create call_out_records table
                create_table_sql = """
                CREATE TABLE call_out_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    pto_request_id INTEGER,
                    call_sid VARCHAR(100),
                    recording_url TEXT,
                    recording_duration INTEGER,
                    source VARCHAR(10) NOT NULL,
                    phone_number_used VARCHAR(20) NOT NULL,
                    verified BOOLEAN DEFAULT 0,
                    authentication_method VARCHAR(20),
                    message_text TEXT,
                    created_at DATETIME,
                    processed_at DATETIME,
                    FOREIGN KEY (member_id) REFERENCES team_members(id),
                    FOREIGN KEY (pto_request_id) REFERENCES pto_requests(id)
                )
                """

                db.session.execute(text(create_table_sql))
                db.session.commit()
                print("  -> call_out_records table created successfully")
            else:
                print("\ncall_out_records table already exists")

            print("\n" + "=" * 60)
            print("SUCCESS: Migration completed successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Set up Twilio account and get credentials")
            print("2. Update .env file with Twilio configuration")
            print("3. Add phone numbers to employee records")
            print("4. Optionally set PINs for employees")
            print("5. Configure Twilio webhook URLs")
            print("\n")

        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_database()
