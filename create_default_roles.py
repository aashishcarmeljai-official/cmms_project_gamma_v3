#!/usr/bin/env python3
"""
Utility script to create default roles for all companies
Run this script to ensure all companies have the standard roles: admin, manager, technician, viewer
"""

import json
from app import app, db
from models import Company, Role

def create_default_roles_for_company(company_id):
    """Create default system roles for a company"""
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
    
    created_count = 0
    for role_data in default_roles:
        # Check if role already exists
        existing_role = Role.query.filter_by(
            company_id=company_id,
            name=role_data['name']
        ).first()
        
        if not existing_role:
            role = Role(
                company_id=company_id,
                name=role_data['name'],
                display_name=role_data['display_name'],
                description=role_data['description'],
                permissions=json.dumps(role_data['permissions']),
                is_system_role=role_data['is_system_role'],
                is_active=True
            )
            db.session.add(role)
            created_count += 1
            print(f"  ✓ Created role: {role_data['display_name']}")
        else:
            print(f"  - Role already exists: {role_data['display_name']}")
    
    db.session.commit()
    return created_count

def main():
    """Create default roles for all companies"""
    with app.app_context():
        print("Creating default roles for all companies...")
        
        companies = Company.query.all()
        if not companies:
            print("No companies found. Please create a company first.")
            return
        
        total_created = 0
        for company in companies:
            print(f"\nProcessing company: {company.name} (ID: {company.id})")
            created = create_default_roles_for_company(company.id)
            total_created += created
        
        print(f"\n✓ Completed! Created {total_created} new roles across {len(companies)} companies.")
        print("\nDefault roles available:")
        print("- Administrator (admin)")
        print("- Manager (manager)")
        print("- Technician (technician)")
        print("- Viewer (viewer)")

if __name__ == '__main__':
    main() 