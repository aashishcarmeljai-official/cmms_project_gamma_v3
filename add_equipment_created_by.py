from app import app, db
from models import User, Equipment
from sqlalchemy import text

def upgrade():
    # Add the column as nullable first
    db.session.execute(text('ALTER TABLE equipment ADD COLUMN created_by_id INTEGER'))
    # Get a valid user id to use for existing equipment
    user = db.session.query(User).first()
    user_id = user.id if user else 1  # fallback to 1 if no user exists
    # Set all existing equipment to this user
    db.session.execute(text('UPDATE equipment SET created_by_id = :user_id'), {'user_id': user_id})
    # Alter the column to be non-nullable and add the foreign key constraint
    db.session.execute(text('''
        ALTER TABLE equipment 
        ALTER COLUMN created_by_id SET NOT NULL
    '''))
    db.session.execute(text('''
        ALTER TABLE equipment 
        ADD CONSTRAINT fk_equipment_created_by FOREIGN KEY (created_by_id) REFERENCES users(id)
    '''))
    db.session.commit()

def downgrade():
    db.session.execute(text('ALTER TABLE equipment DROP CONSTRAINT IF EXISTS fk_equipment_created_by'))
    db.session.execute(text('ALTER TABLE equipment DROP COLUMN IF EXISTS created_by_id'))
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        upgrade()
        print('Migration complete.') 