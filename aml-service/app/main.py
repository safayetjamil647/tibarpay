from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tibarpay AML Service")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def init_db(db: Session):
    # Seed default global rules if not exists
    if not db.query(models.GlobalAMLRule).first():
        db.add(models.GlobalAMLRule(action="add_money", limit_amount=1000.0))
        db.add(models.GlobalAMLRule(action="transfer_money", limit_amount=500.0))
        db.commit()

@app.on_event("startup")
def startup_event():
    with next(get_db()) as db:
        init_db(db)

@app.get("/api/aml/policies", response_model=schemas.AMLLimitsOut)
def get_policies(db: Session = Depends(get_db)):
    global_rules = db.query(models.GlobalAMLRule).all()
    tier_rules = db.query(models.TierAMLRule).all()
    return {"global_rules": global_rules, "tier_rules": tier_rules}

@app.post("/api/aml/internal/global", response_model=schemas.GlobalAMLRuleOut)
def update_global_policy(rule_in: schemas.GlobalAMLRuleCreate, db: Session = Depends(get_db)):
    db_rule = db.query(models.GlobalAMLRule).filter(models.GlobalAMLRule.action == rule_in.action).first()
    if db_rule:
        db_rule.limit_amount = rule_in.limit_amount
    else:
        db_rule = models.GlobalAMLRule(**rule_in.dict())
        db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.post("/api/aml/internal/tier", response_model=schemas.TierAMLRuleOut)
def update_tier_policy(rule_in: schemas.TierAMLRuleCreate, db: Session = Depends(get_db)):
    db_rule = db.query(models.TierAMLRule).filter(
        models.TierAMLRule.action == rule_in.action,
        models.TierAMLRule.tier_name == rule_in.tier_name
    ).first()
    if db_rule:
        db_rule.limit_amount = rule_in.limit_amount
    else:
        db_rule = models.TierAMLRule(**rule_in.dict())
        db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.get("/api/aml/user-limits", response_model=List[schemas.UserLimitOut])
def get_user_limits(tier: str = "starter", db: Session = Depends(get_db)):
    global_rules = db.query(models.GlobalAMLRule).all()
    tier_rules = db.query(models.TierAMLRule).filter(models.TierAMLRule.tier_name.ilike(tier)).all()
    
    tier_overrides = {tr.action: tr.limit_amount for tr in tier_rules}
    
    limits = []
    for gr in global_rules:
        if gr.action in tier_overrides:
            limits.append({
                "action": gr.action,
                "limit_amount": tier_overrides[gr.action],
                "source": f"tier ({tier})"
            })
        else:
            limits.append({
                "action": gr.action,
                "limit_amount": gr.limit_amount,
                "source": "global"
            })
    return limits
