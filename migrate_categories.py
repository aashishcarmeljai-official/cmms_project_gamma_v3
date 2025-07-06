#!/usr/bin/env python3
"""
Migration script to add Category table and create default categories for existing companies.
Run this script to upgrade your existing CMMS database to support categories.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_category_table(engine):
    """Create the categories table if it doesn't exist"""
    print("Creating categories table...")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        type VARCHAR(20) NOT NULL CHECK (type IN ('equipment', 'inventory')),
        description TEXT,
        color VARCHAR(7) DEFAULT '#007bff',
        is_active BOOLEAN DEFAULT TRUE,
        company_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE,
        UNIQUE(company_id, name, type)
    );
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        print("✅ Categories table created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating categories table: {e}")
        return False

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def get_existing_companies(engine):
    """Get all existing companies from the database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name FROM companies"))
            companies = result.fetchall()
            return companies
    except Exception as e:
        print(f"❌ Error fetching companies: {e}")
        return []

def create_default_categories_for_company(engine, company_id, company_name):
    """Create default categories for a specific company"""
    print(f"Creating default categories for company: {company_name} (ID: {company_id})")
    
    default_equipment_categories = [
        ('Machinery', 'Heavy machinery and production equipment'),
        ('Electrical', 'Electrical systems and components'),
        ('HVAC', 'Heating, ventilation, and air conditioning'),
        ('Plumbing', 'Plumbing systems and fixtures'),
        ('Vehicles', 'Company vehicles and transportation'),
        ('Computers', 'Computer systems and IT equipment'),
        ('Furniture', 'Office furniture and fixtures'),
        ('Tools', 'Hand tools and power tools')
    ]
    
    default_inventory_categories = [
        ('Filters', 'Air, oil, and water filters'),
        ('Bearings', 'Mechanical bearings and bushings'),
        ('Belts', 'Drive belts and conveyor belts'),
        ('Motors', 'Electric motors and drives'),
        ('Electrical', 'Electrical components and supplies'),
        ('Lubricants', 'Oils, greases, and lubricants'),
        ('Fasteners', 'Bolts, nuts, screws, and washers'),
        ('Pipes', 'Pipes, fittings, and tubing'),
        ('Valves', 'Control valves and regulators'),
        ('Sensors', 'Sensors and instrumentation'),
        ('Tools', 'Maintenance tools and equipment'),
        ('Safety', 'Safety equipment and supplies')
    ]
    
    try:
        with engine.connect() as conn:
            # Insert equipment categories
            for name, description in default_equipment_categories:
                # Check if category already exists
                check_sql = "SELECT id FROM categories WHERE company_id = :company_id AND name = :name AND type = 'equipment'"
                existing = conn.execute(text(check_sql), {"company_id": company_id, "name": name}).fetchone()
                
                if not existing:
                    insert_sql = """
                    INSERT INTO categories (name, type, description, color, company_id, created_at, updated_at)
                    VALUES (:name, 'equipment', :description, '#007bff', :company_id, :created_at, :updated_at)
                    """
                    conn.execute(text(insert_sql), {
                        "name": name,
                        "description": description,
                        "company_id": company_id,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    print(f"  ✅ Added equipment category: {name}")
                else:
                    print(f"  ⏭️  Equipment category already exists: {name}")
            
            # Insert inventory categories
            for name, description in default_inventory_categories:
                # Check if category already exists
                check_sql = "SELECT id FROM categories WHERE company_id = :company_id AND name = :name AND type = 'inventory'"
                existing = conn.execute(text(check_sql), {"company_id": company_id, "name": name}).fetchone()
                
                if not existing:
                    insert_sql = """
                    INSERT INTO categories (name, type, description, color, company_id, created_at, updated_at)
                    VALUES (:name, 'inventory', :description, '#28a745', :company_id, :created_at, :updated_at)
                    """
                    conn.execute(text(insert_sql), {
                        "name": name,
                        "description": description,
                        "company_id": company_id,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    print(f"  ✅ Added inventory category: {name}")
                else:
                    print(f"  ⏭️  Inventory category already exists: {name}")
            
            conn.commit()
            print(f"✅ Default categories created for {company_name}")
            return True
            
    except Exception as e:
        print(f"❌ Error creating categories for company {company_name}: {e}")
        return False

def create_indexes(engine):
    """Create indexes for better performance"""
    print("Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_categories_company_id ON categories(company_id);",
        "CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type);",
        "CREATE INDEX IF NOT EXISTS idx_categories_active ON categories(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_categories_company_type ON categories(company_id, type);"
    ]
    
    try:
        with engine.connect() as conn:
            for index_sql in indexes:
                conn.execute(text(index_sql))
            conn.commit()
        print("✅ Indexes created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        return False

def backup_database(db_path):
    """Create a backup of the database before migration"""
    import shutil
    from datetime import datetime
    
    backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def main():
    """Main migration function"""
    print("=" * 60)
    print("CMMS Category Migration Script")
    print("=" * 60)
    
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
    
    # Check if companies table exists
    if not check_table_exists(engine, 'companies'):
        print("❌ Companies table not found. Please run the initial database setup first.")
        return False
    
    # Create backup (only for SQLite - PostgreSQL backups should be done manually)
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        if os.path.exists(db_path):
            backup_path = backup_database(db_path)
            if not backup_path:
                print("⚠️  Warning: Could not create backup. Proceeding anyway...")
    else:
        print("⚠️  For PostgreSQL databases, please create a backup manually before proceeding.")
        print("   You can use: pg_dump your_database > backup.sql")
        confirm = input("Have you created a backup? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Migration cancelled. Please create a backup first.")
            return False
    
    # Create categories table
    if not create_category_table(engine):
        return False
    
    # Create indexes
    if not create_indexes(engine):
        print("⚠️  Warning: Could not create indexes. Continuing...")
    
    # Get existing companies
    companies = get_existing_companies(engine)
    if not companies:
        print("⚠️  No companies found in database")
        return True
    
    print(f"\nFound {len(companies)} companies in database")
    
    # Create default categories for each company
    success_count = 0
    for company_id, company_name in companies:
        if create_default_categories_for_company(engine, company_id, company_name):
            success_count += 1
        print()
    
    print("=" * 60)
    print("Migration Summary:")
    print(f"✅ Categories table created")
    print(f"✅ Indexes created")
    print(f"✅ Default categories created for {success_count}/{len(companies)} companies")
    print("=" * 60)
    
    if success_count == len(companies):
        print("🎉 Migration completed successfully!")
        return True
    else:
        print("⚠️  Migration completed with some issues. Check the output above.")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 