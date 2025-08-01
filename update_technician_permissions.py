import os
import sys
from app import app, db
from models import Role, User, Company
import json

# Define the correct permissions for technician
TECHNICIAN_PERMISSIONS = [
    "equipment_view",
    "inventory_view",
    "location_view",
    "inventory_add",
    "workorder_view",
    "workorder_edit",
    "user_view",
    "sop_view",
    "team_view"
]


def update_technician_roles():
    companies = Company.query.all()
    total_roles_updated = 0
    total_users_updated = 0
    for company in companies:
        # Find technician role for this company
        technician_role = Role.query.filter_by(company_id=company.id, name="technician").first()
        if not technician_role:
            print(f"No technician role found for company {company.name} (ID: {company.id})")
            continue
        # Update permissions if needed
        current_perms = set(json.loads(technician_role.permissions or "[]"))
        desired_perms = set(TECHNICIAN_PERMISSIONS)
        if current_perms != desired_perms:
            technician_role.permissions = json.dumps(TECHNICIAN_PERMISSIONS)
            db.session.add(technician_role)
            total_roles_updated += 1
            print(f"Updated permissions for technician role in company {company.name} (ID: {company.id})")
        # Update users with role 'technician' to have correct role_id
        users = User.query.filter_by(company_id=company.id, role="technician").all()
        for user in users:
            if user.role_id != technician_role.id:
                user.role_id = technician_role.id
                db.session.add(user)
                total_users_updated += 1
                print(f"Updated user {user.username} (ID: {user.id}) to correct technician role_id")
    db.session.commit()
    print(f"\nSummary:")
    print(f"Roles updated: {total_roles_updated}")
    print(f"Users updated: {total_users_updated}")

if __name__ == "__main__":
    with app.app_context():
        update_technician_roles() 