#!/usr/bin/env python3
"""
Migration script to add location_id column to work_orders table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import WorkOrder, Location
from sqlalchemy import text

def migrate_work_orders_location():
    """Add location_id column to work_orders table"""
    
    with app.app_context():
        try:
            # Add the location_id column if it doesn't exist
            with db.engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE work_orders 
                    ADD COLUMN location_id INTEGER 
                    REFERENCES locations(id)
                """))
                conn.commit()
            print("✓ Added location_id column to work_orders table")
            
            print("Migration completed successfully!")
            print("Note: Existing work orders will show equipment location as fallback until manually updated.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            if "already exists" in str(e):
                print("Column already exists - migration not needed.")
            else:
                print("Migration failed. Please check the error above.")

if __name__ == "__main__":
    migrate_work_orders_location() 