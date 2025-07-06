# Category Migration Guide

This guide explains how to migrate your existing CMMS database to support the new category system.

## Overview

The category system adds company-specific categories for both equipment and inventory items. Each company will have its own set of categories that can be managed independently.

## Files Included

- `migrate_categories.py` - Main migration script
- `rollback_categories.py` - Rollback script (if needed)
- `CATEGORY_MIGRATION_README.md` - This guide

## Prerequisites

1. **Backup your database** before running any migration
2. Ensure your `.env` file has the correct `DATABASE_URL`
3. Make sure you have the required Python packages installed

## Running the Migration

### Step 1: Backup Your Database

**IMPORTANT**: Always backup your database before running migrations!

```bash
# For SQLite databases
cp your_database.db your_database.db.backup

# For PostgreSQL databases
pg_dump your_database > backup_$(date +%Y%m%d_%H%M%S).sql

# For MySQL databases
mysqldump your_database > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Run the Migration

```bash
python migrate_categories.py
```

The script will:

1. ✅ Create a backup of your database (for SQLite)
2. ✅ Create the `categories` table
3. ✅ Create performance indexes
4. ✅ Add default categories for each existing company
5. ✅ Show a summary of what was done

### Step 3: Verify the Migration

After running the migration, you can verify it worked by:

1. **Check the database**: The `categories` table should exist
2. **Check the web interface**: Go to Admin → Categories to see the new categories
3. **Test equipment/inventory forms**: The category dropdowns should now be populated

## What the Migration Does

### Creates the Categories Table

**PostgreSQL Syntax:**
```sql
CREATE TABLE categories (
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
```

**SQLite Syntax:**
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('equipment', 'inventory')),
    description TEXT,
    color VARCHAR(7) DEFAULT '#007bff',
    is_active BOOLEAN DEFAULT 1,
    company_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE,
    UNIQUE(company_id, name, type)
);
```

### Creates Performance Indexes

- `idx_categories_company_id` - For filtering by company
- `idx_categories_type` - For filtering by type (equipment/inventory)
- `idx_categories_active` - For filtering active categories
- `idx_categories_company_type` - For combined company and type queries

### Adds Default Categories

For each existing company, the migration creates:

**Equipment Categories (8 total):**
- Machinery
- Electrical
- HVAC
- Plumbing
- Vehicles
- Computers
- Furniture
- Tools

**Inventory Categories (12 total):**
- Filters
- Bearings
- Belts
- Motors
- Electrical
- Lubricants
- Fasteners
- Pipes
- Valves
- Sensors
- Tools
- Safety

## Rollback (If Needed)

If you need to undo the migration:

```bash
python rollback_categories.py
```

**⚠️ WARNING**: This will permanently delete all category data!

The rollback script will:
1. Ask for confirmation (type 'YES')
2. Create a backup
3. Drop the categories table and indexes
4. Show a summary

## Troubleshooting

### Common Issues

1. **"DATABASE_URL not found"**
   - Make sure your `.env` file has `DATABASE_URL` set
   - Example: `DATABASE_URL=sqlite:///cmms.db`

2. **"Companies table not found"**
   - Run the initial database setup first
   - Make sure you have at least one company in the database

3. **"Permission denied"**
   - Make sure you have write permissions to the database file
   - For SQLite, check file permissions

4. **"Foreign key constraint failed"**
   - Make sure all companies referenced in categories exist
   - Check for orphaned data

### Getting Help

If you encounter issues:

1. Check the error messages carefully
2. Verify your database connection
3. Ensure you have the latest code changes
4. Check that all required packages are installed

## Post-Migration

After successful migration:

1. **Test the web interface**:
   - Go to Admin → Categories
   - Try adding/editing categories
   - Test equipment and inventory forms

2. **Customize categories**:
   - Add company-specific categories
   - Modify default categories as needed
   - Set custom colors for visual organization

3. **Train users**:
   - Show users how to use the new category system
   - Explain the benefits of proper categorization

## Database Schema

After migration, your database will have this new table:

```
categories
├── id (PRIMARY KEY)
├── name (VARCHAR 100)
├── type (VARCHAR 20) - 'equipment' or 'inventory'
├── description (TEXT)
├── color (VARCHAR 7) - Hex color code
├── is_active (BOOLEAN)
├── company_id (FOREIGN KEY)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

## Support

If you need help with the migration:

1. Check the error messages
2. Verify your database setup
3. Ensure all prerequisites are met
4. Test with a backup database first

The migration is designed to be safe and reversible, but always backup your data before running any database changes. 