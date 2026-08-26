from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class GlobalAMLRule(Base):
    __tablename__ = "global_aml_rules"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, unique=True, index=True) # e.g. "add_money", "transfer_money"
    limit_amount = Column(Float, default=0.0)

class TierAMLRule(Base):
    __tablename__ = "tier_aml_rules"
    id = Column(Integer, primary_key=True, index=True)
    tier_name = Column(String, index=True) # e.g. "starter", "standard", "premium"
    action = Column(String, index=True)
    limit_amount = Column(Float, default=0.0)
