import jwt
import requests
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tibarpay Add Money Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "supersecretkey"

def get_token_header(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return authorization

def get_current_user_token(token: str = Depends(get_token_header)) -> Dict[str, Any]:
    raw_token = token.split(" ")[1]
    try:
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=["HS256"])
        payload["raw_token"] = raw_token
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_profile(raw_token: str):
    try:
        resp = requests.get("http://user-service:8000/api/auth/me", headers={"Authorization": f"Bearer {raw_token}"}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")

def check_aml_limit(tier: str, action: str, amount: float, raw_token: str):
    try:
        resp = requests.get(f"http://aml-service:8002/api/aml/user-limits?tier={tier}", headers={"Authorization": f"Bearer {raw_token}"}, timeout=5)
        resp.raise_for_status()
        limits = resp.json()
        for limit in limits:
            if limit["action"] == action:
                if amount > limit["limit_amount"]:
                    raise HTTPException(status_code=400, detail=f"AML Limit Exceeded for {action}. Max allowed: ${limit['limit_amount']}")
                return True
        # If no limit rule is explicitly found, allow or deny? Default deny for safety or allow? Allow if no rule.
        return True
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to check AML limits")

@app.get("/api/add-money/balance", response_model=schemas.WalletOut)
def get_balance(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user_token)):
    user_id = current_user.get("user_id")
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).first()
    if not wallet:
        wallet = models.Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

@app.post("/api/add-money/execute", response_model=schemas.TransactionOut)
def execute_add_money(req: schemas.AddMoneyRequest, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user_token)):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
    user_id = current_user.get("user_id")
    raw_token = current_user.get("raw_token")
    
    # 1. Fetch user profile for tier
    profile = get_user_profile(raw_token)
    tier = profile.get("tier", "starter")
    
    # 2. Check AML Limit
    check_aml_limit(tier, "add_money", req.amount, raw_token)
    
    # 3. Update Wallet
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).first()
    if not wallet:
        wallet = models.Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        
    wallet.balance += req.amount
    
    # 4. Record Transaction
    tx = models.Transaction(
        user_id=user_id,
        type="ADD_MONEY",
        amount=req.amount,
        status="completed",
        details="{}"
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

@app.get("/api/add-money/transactions", response_model=List[schemas.TransactionOut])
def get_transactions(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user_token)):
    user_id = current_user.get("user_id")
    role = current_user.get("role", "user")
    
    if role in ["Super Admin", "Admin"]:
        txs = db.query(models.Transaction).filter(models.Transaction.type == "ADD_MONEY").order_by(models.Transaction.created_at.desc()).all()
    else:
        txs = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.type == "ADD_MONEY"
        ).order_by(models.Transaction.created_at.desc()).all()
    return txs
