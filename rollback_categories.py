#!/usr/bin/env python3
"""
Rollback script to remove Category table and related data.
Use this script only if you need to undo the category migration.
WARNING: This will permanently delete all category data!
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def backup_database(db_path):
    """Create a backup of the database before rollback"""
    import shutil
    from datetime import datetime
    
    backup_path = f"{db_path}.rollback_backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def get_category_count(engine):
    """Get the number of categories in the database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM categories"))
            count = result.scalar()
            return count
    except Exception as e:
        print(f"❌ Error counting categories: {e}")
        return 0

def drop_category_table(engine):
    """Drop the categories table"""
    print("Dropping categories table...")
    
    try:
        with engine.connect() as conn:
            # Drop indexes first
            indexes = [
                "DROP INDEX IF EXISTS idx_categories_company_id;",
                "DROP INDEX IF EXISTS idx_categories_type;",
                "DROP INDEX IF EXISTS idx_categories_active;",
                "DROP INDEX IF EXISTS idx_categories_company_type;"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    print(f"  ⚠️  Warning: Could not drop index: {e}")
            
            # Drop the table
            conn.execute(text("DROP TABLE IF EXISTS categories;"))
            conn.commit()
        
        print("✅ Categories table dropped successfully!")
        return True
    except Exception as e:
        print(f"❌ Error dropping categories table: {e}")
        return False

def main():
    """Main rollback function"""
    print("=" * 60)
    print("CMMS Category Rollback Script")
    print("=" * 60)
    print("⚠️  WARNING: This will permanently delete all category data!")
    print("=" * 60)
    
    # Confirm with user
    confirm = input("Are you sure you want to proceed? Type 'YES' to continue: ")
    if confirm != "YES":
        print("❌ Rollback cancelled by user")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    print(f"Database URL: {database_url}")
    
    # Create database engine
    try:
        engine = create_engine(database_url)
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False
    
    # Check if categories table exists
    if not check_table_exists(engine, 'categories'):
        print("❌ Categories table not found. Nothing to rollback.")
        return True
    
    # Get category count
    category_count = get_category_count(engine)
    print(f"Found {category_count} categories in database")
    
    # Create backup
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        if os.path.exists(db_path):
            backup_path = backup_database(db_path)
            if not backup_path:
                print("⚠️  Warning: Could not create backup. Proceeding anyway...")
    
    # Drop categories table
    if not drop_category_table(engine):
        return False
    
    print("=" * 60)
    print("Rollback Summary:")
    print(f"✅ Categories table dropped")
    print(f"✅ {category_count} categories removed")
    print("=" * 60)
    print("🎉 Rollback completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Rollback cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 