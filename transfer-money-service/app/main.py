import jwt
import requests
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tibarpay Transfer Money Service")

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
        return True
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to check AML limits")

def resolve_account_number(account_number: str, raw_token: str):
    try:
        # We need an endpoint in user-service to resolve account number, but we haven't created one!
        # Alternative: We can fetch all users and filter, but that's inefficient for large data.
        # Let's create an endpoint in user-service or just query the database directly since it's an internal microservice? No, different databases.
        # Wait, I didn't create an endpoint in user-service to resolve account number.
        # I'll create an internal endpoint in user-service!
        resp = requests.get(f"http://user-service:8000/api/users/resolve-account/{account_number}", headers={"Authorization": f"Bearer {raw_token}"}, timeout=5)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Recipient account not found")
        resp.raise_for_status()
        return resp.json()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to resolve recipient account number")

@app.post("/api/transfer-money/execute", response_model=schemas.TransactionOut)
def execute_transfer_money(req: schemas.TransferMoneyRequest, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user_token)):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
    sender_id = current_user.get("user_id")
    raw_token = current_user.get("raw_token")
    
    # 1. Resolve recipient
    recipient = resolve_account_number(req.recipient_account_number, raw_token)
    recipient_id = recipient["id"]
    
    if sender_id == recipient_id:
        raise HTTPException(status_code=400, detail="Cannot transfer money to yourself")
    
    # 2. Fetch sender profile for tier
    profile = get_user_profile(raw_token)
    tier = profile.get("tier", "starter")
    
    # 3. Check AML Limit
    check_aml_limit(tier, "transfer_money", req.amount, raw_token)
    
    # 4. Check Wallet Balance
    sender_wallet = db.query(models.Wallet).filter(models.Wallet.user_id == sender_id).first()
    if not sender_wallet or sender_wallet.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
        
    # 5. Update Wallets
    recipient_wallet = db.query(models.Wallet).filter(models.Wallet.user_id == recipient_id).first()
    if not recipient_wallet:
        recipient_wallet = models.Wallet(user_id=recipient_id, balance=0.0)
        db.add(recipient_wallet)
        
    sender_wallet.balance -= req.amount
    recipient_wallet.balance += req.amount
    
    # 6. Record Transactions
    tx_out = models.Transaction(
        user_id=sender_id,
        type="TRANSFER_OUT",
        amount=req.amount,
        status="completed",
        details=json.dumps({"recipient_id": recipient_id, "recipient_email": recipient["email"]})
    )
    db.add(tx_out)
    
    tx_in = models.Transaction(
        user_id=recipient_id,
        type="TRANSFER_IN",
        amount=req.amount,
        status="completed",
        details=json.dumps({"sender_id": sender_id, "sender_email": profile["email"]})
    )
    db.add(tx_in)
    
    db.commit()
    db.refresh(tx_out)
    return tx_out

@app.get("/api/transfer-money/transactions", response_model=List[schemas.TransactionOut])
def get_transactions(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user_token)):
    user_id = current_user.get("user_id")
    role = current_user.get("role", "user")
    
    if role in ["Super Admin", "Admin"]:
        txs = db.query(models.Transaction).filter(
            models.Transaction.type.in_(["TRANSFER_OUT", "TRANSFER_IN"])
        ).order_by(models.Transaction.created_at.desc()).all()
    else:
        txs = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.type.in_(["TRANSFER_OUT", "TRANSFER_IN"])
        ).order_by(models.Transaction.created_at.desc()).all()
    return txs
