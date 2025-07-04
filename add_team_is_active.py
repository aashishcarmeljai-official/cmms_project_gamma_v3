#!/usr/bin/env python3
"""
Migration script to add is_active column to teams table
Run this script to add the missing is_active field to existing teams
"""

from app import app, db
from sqlalchemy import text

def add_team_is_active_column():
    """Add is_active column to teams table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'teams' AND column_name = 'is_active'
            """))
            
            if result.fetchone():
                print("✅ is_active column already exists in teams table")
                return
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE teams 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """))
            
            # Update existing teams to be active
            db.session.execute(text("""
                UPDATE teams 
                SET is_active = TRUE 
                WHERE is_active IS NULL
            """))
            
            db.session.commit()
            print("✅ Successfully added is_active column to teams table")
            print("✅ All existing teams set to active")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding is_active column: {str(e)}")
            raise

if __name__ == "__main__":
    add_team_is_active_column() 