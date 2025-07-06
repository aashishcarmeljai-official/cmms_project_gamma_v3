#!/usr/bin/env python3
"""
Test script to verify the migration setup without actually running it.
This script checks if all prerequisites are met for the category migration.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if environment is properly configured"""
    print("Testing environment configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"✅ DATABASE_URL found: {database_url}")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\nTesting required imports...")
    
    try:
        from sqlalchemy import create_engine, text, inspect
        print("✅ SQLAlchemy imports successful")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        from datetime import datetime
        print("✅ datetime import successful")
    except ImportError as e:
        print(f"❌ datetime import failed: {e}")
        return False
    
    try:
        import shutil
        print("✅ shutil import successful")
    except ImportError as e:
        print(f"❌ shutil import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Check if companies table exists (works for both SQLite and PostgreSQL)
            if database_url and 'sqlite' in database_url:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'"))
            else:
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name='companies'"))
            
            if result.fetchone():
                print("✅ Companies table exists")
                
                # Count companies
                result = conn.execute(text("SELECT COUNT(*) FROM companies"))
                company_count = result.scalar()
                print(f"✅ Found {company_count} companies in database")
            else:
                print("❌ Companies table not found")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True

def test_migration_script():
    """Test if migration script can be imported"""
    print("\nTesting migration script...")
    
    try:
        import migrate_categories
        print("✅ Migration script imports successfully")
    except Exception as e:
        print(f"❌ Migration script import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("Category Migration Test Script")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("Migration Script", test_migration_script)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You're ready to run the migration.")
        print("\nTo run the migration:")
        print("python migrate_categories.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the migration.")
    
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 