import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallets"
    user_id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    type = Column(String, index=True, nullable=False) # ADD_MONEY, TRANSFER_OUT, TRANSFER_IN
    amount = Column(Float, nullable=False)
    status = Column(String, default="completed")
    details = Column(String, nullable=True) # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
