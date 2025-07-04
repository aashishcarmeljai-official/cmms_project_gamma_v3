from app import app, db
from sqlalchemy import text

# This script assumes the table is called 'teams' and the old constraint is on 'name'.
# The new constraint will be on (company_id, name).

def constraint_exists(constraint_name):
    with app.app_context():
        result = db.session.execute(text(f"""
            SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE table_name = 'teams' AND constraint_name = :cname
        """), {'cname': constraint_name})
        return result.scalar() > 0

def main():
    with app.app_context():
        # Drop the old unique constraint if it exists
        try:
            # The constraint name may vary by DB. Try common names.
            old_constraints = ['name', 'uq_teams_name', 'teams_name_key']
            for old_constraint in old_constraints:
                try:
                    if constraint_exists(old_constraint):
                        print(f"Dropping old unique constraint: {old_constraint}")
                        db.session.execute(text(f"ALTER TABLE teams DROP CONSTRAINT {old_constraint}"))
                        db.session.commit()
                        print(f"Dropped constraint: {old_constraint}")
                except Exception as e:
                    print(f"Could not drop constraint {old_constraint}: {e}")
        except Exception as e:
            print(f"Error checking/dropping old constraint: {e}")

        # Add the new composite unique constraint
        try:
            print("Adding new unique constraint on (company_id, name)...")
            db.session.execute(text(
                "ALTER TABLE teams ADD CONSTRAINT uq_team_company_name UNIQUE (company_id, name)"
            ))
            db.session.commit()
            print("✅ Added new unique constraint: uq_team_company_name")
        except Exception as e:
            print(f"Error adding new unique constraint: {e}")

if __name__ == "__main__":
    main() 