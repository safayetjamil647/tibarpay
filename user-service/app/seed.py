import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth import hash_password

def seed_db():
    print("Starting database seeding process...")
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            print(f"Admin user already exists: {admin.email}")
            return
        
        email = os.getenv("SEED_ADMIN_EMAIL", "admin@tibarpay.com")
        password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
        
        hashed_pwd = hash_password(password)
        admin_user = User(
            email=email,
            hashed_password=hashed_pwd,
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print(f"Successfully seeded admin user:")
        print(f"  Email:    {email}")
        print(f"  Password: {password}")
        print("Keep these credentials secure or change them on first login.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
