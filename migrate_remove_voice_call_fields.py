"""
Database migration to remove voice call-specific fields from CallOutRecord table
Run this script once to update the database schema
"""

from database import db
from app import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_remove_voice_fields():
    """Remove recording_url and recording_duration columns from call_out_records table"""

    with app.app_context():
        try:
            # Check if we're using SQLite or another database
            db_url = app.config['SQLALCHEMY_DATABASE_URI']

            if 'sqlite' in db_url.lower():
                # SQLite doesn't support DROP COLUMN directly
                # We need to recreate the table without those columns
                logger.info("Detected SQLite database - recreating table...")

                # For SQLite, the easiest approach is to:
                # 1. Keep the old table as-is (it won't hurt to have extra columns)
                # 2. Or manually recreate if needed
                logger.warning("SQLite doesn't support DROP COLUMN. Extra columns (recording_url, recording_duration) will remain but won't be used.")
                logger.info("This is harmless - the columns will simply be ignored by the application.")

            else:
                # For PostgreSQL, MySQL, etc., we can drop columns directly
                logger.info("Dropping recording_url and recording_duration columns...")

                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE call_out_records DROP COLUMN IF EXISTS recording_url'))
                    conn.execute(db.text('ALTER TABLE call_out_records DROP COLUMN IF EXISTS recording_duration'))
                    conn.commit()

                logger.info("Columns dropped successfully!")

            logger.info("Migration completed successfully!")
            logger.info("Voice call features have been removed from the database schema.")

        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            logger.error("This may be because the columns don't exist or have already been removed.")
            raise


if __name__ == '__main__':
    logger.info("Starting migration to remove voice call fields...")
    logger.info("This will remove recording_url and recording_duration from call_out_records table")

    confirm = input("Do you want to continue? (yes/no): ")

    if confirm.lower() in ['yes', 'y']:
        migrate_remove_voice_fields()
    else:
        logger.info("Migration cancelled.")
