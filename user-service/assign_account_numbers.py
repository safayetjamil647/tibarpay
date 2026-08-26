from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
from app.config import settings
from app.models import User

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    db = SessionLocal()
    users = db.query(User).all()
    for user in users:
        if not user.account_number:
            user.account_number = "".join([str(random.randint(0, 9)) for _ in range(10)])
    db.commit()
    db.close()
    print("Account numbers assigned to existing users.")

if __name__ == "__main__":
    main()
