#!/usr/bin/env python3
"""
Utility script to create default departments for all companies
Run this script to ensure all companies have the standard departments
"""

from app import app, db
from models import Company
from app import create_default_departments_for_company

def main():
    """Create default departments for all companies"""
    with app.app_context():
        print("Creating default departments for all companies...")
        companies = Company.query.all()
        if not companies:
            print("No companies found. Please create a company first.")
            return
        for company in companies:
            print(f"\nProcessing company: {company.name} (ID: {company.id})")
            create_default_departments_for_company(company.id)
            print("  ✓ Default departments created (if missing)")
        print(f"\n✓ Completed! Default departments should now be available for all companies.")

if __name__ == '__main__':
    main() 