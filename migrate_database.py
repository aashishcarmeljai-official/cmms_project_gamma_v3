#!/usr/bin/env python3
"""
Database migration script for CMMS
This script will update the database schema to match the current models.
"""

import os
import json
from sqlalchemy import text, inspect
from app import app, db
from models import User, Equipment, WorkOrder, MaintenanceSchedule, Inventory, WorkOrderPart, Location, Team, SOP, SOPChecklistItem, WhatsAppUser, WhatsAppTemplate, EmergencyBroadcast, NotificationLog, Company, Role, Department

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns

def add_missing_columns():
    """Add missing columns to existing tables"""
    with app.app_context():
        print("Checking for missing columns...")
        
        # Check and add role column to users table
        if not check_column_exists('users', 'role'):
            print("Adding 'role' column to users table...")
            db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'technician'"))
            db.session.commit()
            print("✅ Added 'role' column to users table")
        else:
            print("✅ 'role' column already exists in users table")
        
        # Check and add company_id column to users table
        if not check_column_exists('users', 'company_id'):
            print("Adding 'company_id' column to users table...")
            db.session.execute(text("ALTER TABLE users ADD COLUMN company_id INTEGER"))
            db.session.commit()
            print("✅ Added 'company_id' column to users table")
        else:
            print("✅ 'company_id' column already exists in users table")
        
        # Check and add location_id column to users table
        if not check_column_exists('users', 'location_id'):
            print("Adding 'location_id' column to users table...")
            db.session.execute(text("ALTER TABLE users ADD COLUMN location_id INTEGER"))
            db.session.commit()
            print("✅ Added 'location_id' column to users table")
        else:
            print("✅ 'location_id' column already exists in users table")
        
        # Check and add google_id column to users table
        if not check_column_exists('users', 'google_id'):
            print("Adding 'google_id' column to users table...")
            db.session.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE"))
            db.session.commit()
            print("✅ Added 'google_id' column to users table")
        else:
            print("✅ 'google_id' column already exists in users table")
        
        # Check and add password_reset_required column to users table
        if not check_column_exists('users', 'password_reset_required'):
            print("Adding 'password_reset_required' column to users table...")
            db.session.execute(text("ALTER TABLE users ADD COLUMN password_reset_required BOOLEAN DEFAULT FALSE"))
            db.session.commit()
            print("✅ Added 'password_reset_required' column to users table")
        else:
            print("✅ 'password_reset_required' column already exists in users table")
        
        # Check and add updated_at column to users table
        if not check_column_exists('users', 'updated_at'):
            print("Adding 'updated_at' column to users table...")
            db.session.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            db.session.commit()
            print("✅ Added 'updated_at' column to users table")
        else:
            print("✅ 'updated_at' column already exists in users table")

        # Add role_id column to users table if it doesn't exist
        if not check_column_exists('users', 'role_id'):
            print("Adding role_id column to users table...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN role_id INTEGER REFERENCES roles(id)"))
                conn.commit()
            print("✓ Added role_id column to users table")

def create_missing_tables():
    """Create any missing tables"""
    with app.app_context():
        print("Creating missing tables...")
        db.create_all()
        print("✅ All tables created/updated")

def create_default_company():
    """Create a default company if none exists"""
    with app.app_context():
        existing_company = Company.query.first()
        if not existing_company:
            print("Creating default company...")
            company = Company(name='Default Company')
            db.session.add(company)
            db.session.commit()
            print(f"✅ Created default company: {company.name} (ID: {company.id})")
            
            # Update existing users to use this company
            users_without_company = User.query.filter_by(company_id=None).all()
            for user in users_without_company:
                user.company_id = company.id
            db.session.commit()
            print(f"✅ Updated {len(users_without_company)} users to use default company")
        else:
            print(f"✅ Company already exists: {existing_company.name}")

def create_admin_user():
    """Create admin user if none exists"""
    with app.app_context():
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print("Creating admin user...")
            company = Company.query.first()
            if not company:
                company = Company(name='Default Company')
                db.session.add(company)
                db.session.commit()
            
            admin = User(
                username='admin',
                email='admin@company.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                department='IT',
                company_id=company.id
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user: admin@company.com / admin123")
        else:
            print("✅ Admin user already exists")

def create_roles_table():
    """Create the roles table if it doesn't exist"""
    with app.app_context():
        inspector = inspect(db.engine)
        if 'roles' not in inspector.get_table_names():
            print("Creating roles table...")
            Role.__table__.create(db.engine)
            print("✓ Created roles table")
        else:
            print("✓ Roles table already exists")

def create_default_roles():
    """Create default system roles for each company"""
    with app.app_context():
        companies = Company.query.all()
        
        for company in companies:
            print(f"Setting up default roles for company: {company.name}")
            
            # Define default system roles
            default_roles = [
                {
                    'name': 'admin',
                    'display_name': 'Administrator',
                    'description': 'Full system access with all permissions',
                    'permissions': [
                        'equipment_view', 'equipment_create', 'equipment_edit', 'equipment_delete',
                        'workorder_view', 'workorder_create', 'workorder_edit', 'workorder_delete',
                        'user_view', 'user_create', 'user_edit', 'user_delete',
                        'admin_dashboard', 'role_manage', 'system_settings', 'reports_access',
                        'team_manage', 'location_manage', 'inventory_manage', 'sop_manage'
                    ],
                    'is_system_role': True
                },
                {
                    'name': 'manager',
                    'display_name': 'Manager',
                    'description': 'Management access with team oversight capabilities',
                    'permissions': [
                        'equipment_view', 'equipment_create', 'equipment_edit',
                        'workorder_view', 'workorder_create', 'workorder_edit',
                        'user_view', 'user_create', 'user_edit',
                        'admin_dashboard', 'reports_access', 'team_manage',
                        'location_manage', 'inventory_manage', 'sop_manage'
                    ],
                    'is_system_role': True
                },
                {
                    'name': 'technician',
                    'display_name': 'Technician',
                    'description': 'Standard technician access for maintenance tasks',
                    'permissions': [
                        'equipment_view',
                        'workorder_view', 'workorder_edit',
                        'user_view'
                    ],
                    'is_system_role': True
                },
                {
                    'name': 'viewer',
                    'display_name': 'Viewer',
                    'description': 'Read-only access to view system data',
                    'permissions': [
                        'equipment_view',
                        'workorder_view',
                        'user_view'
                    ],
                    'is_system_role': True
                }
            ]
            
            # Create roles for this company
            for role_data in default_roles:
                existing_role = Role.query.filter_by(
                    company_id=company.id,
                    name=role_data['name']
                ).first()
                
                if not existing_role:
                    role = Role(
                        company_id=company.id,
                        name=role_data['name'],
                        display_name=role_data['display_name'],
                        description=role_data['description'],
                        permissions=json.dumps(role_data['permissions']),
                        is_system_role=role_data['is_system_role'],
                        is_active=True
                    )
                    db.session.add(role)
                    print(f"  ✓ Created role: {role_data['display_name']}")
                else:
                    print(f"  - Role already exists: {role_data['display_name']}")
            
            db.session.commit()

def update_user_roles():
    """Update existing users to use the new role system"""
    with app.app_context():
        print("Updating user roles...")
        
        # Get all users
        users = User.query.all()
        
        for user in users:
            if user.role and not user.role_id:
                # Find the corresponding role for this user's company
                role = Role.query.filter_by(
                    company_id=user.company_id,
                    name=user.role
                ).first()
                
                if role:
                    user.role_id = role.id
                    print(f"  ✓ Updated user {user.email} to role: {role.display_name}")
                else:
                    # If role doesn't exist, assign to viewer role
                    viewer_role = Role.query.filter_by(
                        company_id=user.company_id,
                        name='viewer'
                    ).first()
                    if viewer_role:
                        user.role_id = viewer_role.id
                        print(f"  ⚠ Updated user {user.email} to viewer role (original role not found)")
        
        db.session.commit()
        print("✓ User roles updated")

def create_departments_table():
    """Create the departments table if it doesn't exist"""
    with app.app_context():
        inspector = inspect(db.engine)
        if 'departments' not in inspector.get_table_names():
            print("Creating departments table...")
            Department.__table__.create(db.engine)
            print("✓ Created departments table")
        else:
            print("✓ Departments table already exists")

def main():
    """Run all migrations"""
    print("Starting database migration...")
    
    try:
        # Create roles table
        create_roles_table()
        
        # Add missing columns
        add_missing_columns()
        
        # Create missing tables
        create_missing_tables()
        
        # Create departments table
        create_departments_table()
        
        # Create default company
        create_default_company()
        
        # Create admin user
        create_admin_user()
        
        # Create default roles
        create_default_roles()
        
        # Update user roles
        update_user_roles()
        
        print("\n✓ Database migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    main() 