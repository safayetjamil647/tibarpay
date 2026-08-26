from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import hashlib
import random
import time
import json
import datetime
from typing import List
import requests

from app.database import get_db
from app import models, schemas, auth, deps

app = FastAPI(title="Tibarpay User Service")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH ROUTES
@app.post("/api/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # All users registered through this endpoint are regular users.
    # Admins are seeded directly in the database as requested.
    hashed_pwd = auth.hash_password(user_in.password)
    
    # Resolve dynamic tier
    db_tier = db.query(models.Tier).filter(models.Tier.name.ilike(user_in.tier)).first()
    tier_id = db_tier.id if db_tier else None
    
    # Generate random 10-digit account number
    account_number = "".join([str(random.randint(0, 9)) for _ in range(10)])
    
    new_user = models.User(
        email=user_in.email,
        account_number=account_number,
        hashed_password=hashed_pwd,
        role="user",
        tier=user_in.tier,
        tier_id=tier_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Assign regular user role
    reg_role = db.query(models.Role).filter(models.Role.name == "Regular User").first()
    if reg_role:
        new_user.roles.append(reg_role)
        db.commit()
        db.refresh(new_user)
        
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not user or not auth.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    user_roles = [r.name for r in user.roles]
    primary_role = user_roles[0] if user_roles else user.role
    tier_name = user.current_tier.name.lower() if user.current_tier else (user.tier or "starter")
    
    access_token = auth.create_access_token(
        data={"user_id": user.id, "email": user.email, "role": primary_role}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": primary_role,
        "tier": tier_name
    }

@app.get("/api/auth/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(deps.get_current_user)):
    tier_name = current_user.current_tier.name.lower() if current_user.current_tier else (current_user.tier or "starter")
    current_user.tier = tier_name
    return current_user


# ADMIN ROUTES
@app.get("/api/admin/stats", response_model=schemas.AdminStats)
def get_admin_stats(db: Session = Depends(get_db), current_admin: models.User = Depends(deps.get_current_admin)):
    total = db.query(models.User).count()
    admins = db.query(models.User).join(models.user_roles).join(models.Role).filter(models.Role.name.in_(["Admin", "Maker Admin", "Checker Admin"])).count()
    users = total - admins
    
    # Generate mock system performance metrics
    return {
        "total_users": total,
        "admin_users": admins,
        "regular_users": users,
        "system_status": "Healthy",
        "memory_usage": "248MB / 1.95GB (12%)"
    }

@app.get("/api/admin/users", response_model=List[schemas.UserAdminView])
def list_users(db: Session = Depends(get_db), current_admin: models.User = Depends(deps.get_current_admin)):
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    for u in users:
        u.tier = u.current_tier.name.lower() if u.current_tier else (u.tier or "starter")
        u.tier_id = u.current_tier.id if u.current_tier else None
    return users

@app.put("/api/admin/users/{user_id}/role", response_model=schemas.UserAdminView)
def update_user_role(user_id: int, role_data: schemas.UserUpdateRole, db: Session = Depends(get_db), current_admin: models.User = Depends(deps.get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
        
    db_role = db.query(models.Role).filter(models.Role.name.ilike(role_data.role)).first()
    if not db_role:
        db_role = db.query(models.Role).filter(models.Role.name == "Regular User").first()
        
    user.roles = [db_role] if db_role else []
    user.role = role_data.role
    db.commit()
    db.refresh(user)
    
    user.tier = user.current_tier.name.lower() if user.current_tier else (user.tier or "starter")
    user.tier_id = user.current_tier.id if user.current_tier else None
    return user

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: models.User = Depends(deps.get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    db.delete(user)
    db.commit()
    return {"message": f"User {user.email} successfully deleted"}

@app.get("/api/users/resolve-account/{account_number}", response_model=schemas.UserOut)
def resolve_account(account_number: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.account_number == account_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.tier = user.current_tier.name.lower() if user.current_tier else (user.tier or "starter")
    user.tier_id = user.current_tier.id if user.current_tier else None
    return user

@app.put("/api/users/me/tier", response_model=schemas.UserOut)
def update_my_tier(tier_data: schemas.UserUpdateTier, db: Session = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    is_admin = db.query(models.Role).join(models.user_roles).filter(
        models.user_roles.c.user_id == current_user.id,
        models.Role.name.in_(["Admin", "Maker Admin", "Checker Admin"])
    ).first()
    if is_admin or current_user.role == "admin":
        raise HTTPException(status_code=400, detail="Admin users do not have subscription tiers")
        
    db_tier = db.query(models.Tier).filter(models.Tier.name.ilike(tier_data.tier)).first()
    if not db_tier:
        raise HTTPException(status_code=400, detail="Invalid tier selection")
        
    current_user.tier_id = db_tier.id
    current_user.tier = db_tier.name.lower()
    db.commit()
    db.refresh(current_user)
    return current_user

@app.put("/api/admin/users/{user_id}/tier", response_model=schemas.UserAdminView)
def update_user_tier(user_id: int, tier_data: schemas.UserUpdateTier, db: Session = Depends(get_db), current_admin: models.User = Depends(deps.get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    is_admin = db.query(models.Role).join(models.user_roles).filter(
        models.user_roles.c.user_id == user.id,
        models.Role.name.in_(["Admin", "Maker Admin", "Checker Admin"])
    ).first()
    if is_admin or user.role == "admin":
        raise HTTPException(status_code=400, detail="Admin users do not have subscription tiers")
        
    db_tier = db.query(models.Tier).filter(models.Tier.name.ilike(tier_data.tier)).first()
    if not db_tier:
        raise HTTPException(status_code=400, detail="Invalid tier value")
        
    user.tier_id = db_tier.id
    user.tier = db_tier.name.lower()
    db.commit()
    db.refresh(user)
    
    user.tier_id = db_tier.id
    return user


# DYNAMIC TIERS & FEATURES MANAGEMENT
@app.get("/api/tiers", response_model=List[schemas.TierOut])
def get_tiers(db: Session = Depends(get_db)):
    return db.query(models.Tier).all()

@app.post("/api/admin/tiers", response_model=schemas.TierOut)
def create_tier(tier_in: schemas.TierCreate, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("manage_tiers"))):
    db_tier = models.Tier(name=tier_in.name, price=tier_in.price, description=tier_in.description)
    db.add(db_tier)
    db.commit()
    db.refresh(db_tier)
    return db_tier

@app.put("/api/admin/tiers/{tier_id}", response_model=schemas.TierOut)
def update_tier(tier_id: int, tier_in: schemas.TierUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("manage_tiers"))):
    db_tier = db.query(models.Tier).filter(models.Tier.id == tier_id).first()
    if not db_tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    db_tier.name = tier_in.name
    db_tier.price = tier_in.price
    db_tier.description = tier_in.description
    db.commit()
    db.refresh(db_tier)
    return db_tier

@app.delete("/api/admin/tiers/{tier_id}")
def delete_tier(tier_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("manage_tiers"))):
    db_tier = db.query(models.Tier).filter(models.Tier.id == tier_id).first()
    if not db_tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    db.query(models.User).filter(models.User.tier_id == tier_id).update({models.User.tier_id: None, models.User.tier: 'starter'})
    db.delete(db_tier)
    db.commit()
    return {"message": "Tier deleted successfully"}

@app.get("/api/admin/features", response_model=List[schemas.FeatureOut])
def list_features(db: Session = Depends(get_db), current_user: models.User = Depends(deps.get_current_admin)):
    return db.query(models.Feature).all()

@app.post("/api/admin/features", response_model=schemas.FeatureOut)
def create_feature(feat_in: schemas.FeatureCreate, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("manage_tiers"))):
    db_feat = models.Feature(name=feat_in.name, code=feat_in.code, description=feat_in.description)
    db.add(db_feat)
    db.commit()
    db.refresh(db_feat)
    return db_feat

@app.put("/api/admin/tiers/{tier_id}/features", response_model=schemas.TierOut)
def update_tier_features(tier_id: int, data: schemas.TierFeaturesUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("manage_tiers"))):
    db_tier = db.query(models.Tier).filter(models.Tier.id == tier_id).first()
    if not db_tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    features = db.query(models.Feature).filter(models.Feature.id.in_(data.feature_ids)).all()
    db_tier.features = features
    db.commit()
    db.refresh(db_tier)
    return db_tier


# MAKER-CHECKER SYSTEM
@app.post("/api/admin/requests", response_model=schemas.ApprovalRequestOut)
def create_approval_request(req_in: schemas.ApprovalRequestCreate, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("make_request"))):
    db_req = models.ApprovalRequest(
        request_type=req_in.request_type,
        payload=req_in.payload,
        status="pending",
        maker_id=current_user.id
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req

@app.get("/api/admin/requests", response_model=List[schemas.ApprovalRequestOut])
def list_approval_requests(db: Session = Depends(get_db), current_user: models.User = Depends(deps.get_current_admin)):
    requests = db.query(models.ApprovalRequest).order_by(models.ApprovalRequest.id.desc()).all()
    res = []
    for r in requests:
        maker_email = db.query(models.User.email).filter(models.User.id == r.maker_id).scalar()
        checker_email = db.query(models.User.email).filter(models.User.id == r.checker_id).scalar() if r.checker_id else None
        res.append(
            schemas.ApprovalRequestOut(
                id=r.id,
                request_type=r.request_type,
                payload=r.payload,
                status=r.status,
                maker_id=r.maker_id,
                checker_id=r.checker_id,
                created_at=r.created_at,
                actioned_at=r.actioned_at,
                rejection_reason=r.rejection_reason,
                maker_email=maker_email,
                checker_email=checker_email
            )
        )
    return res

@app.post("/api/admin/requests/{request_id}/approve", response_model=schemas.ApprovalRequestOut)
def approve_request(request_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("approve_request"))):
    db_req = db.query(models.ApprovalRequest).filter(models.ApprovalRequest.id == request_id).first()
    if not db_req:
        raise HTTPException(status_code=404, detail="Request not found")
    if db_req.status != "pending":
        raise HTTPException(status_code=400, detail="Request is already actioned")
    if db_req.maker_id == current_user.id:
        raise HTTPException(status_code=400, detail="Maker cannot approve their own request")
        
    payload = json.loads(db_req.payload)
    if db_req.request_type == "change_user_tier":
        user_id = payload.get("user_id")
        target_tier = payload.get("tier")
        target_user = db.query(models.User).filter(models.User.id == user_id).first()
        if target_user:
            db_tier = db.query(models.Tier).filter(models.Tier.name.ilike(target_tier)).first()
            if db_tier:
                target_user.tier_id = db_tier.id
                target_user.tier = db_tier.name.lower()
            else:
                target_user.tier = target_tier
            db.commit()
    elif db_req.request_type == "update_tier_features":
        tier_id = payload.get("tier_id")
        feature_ids = payload.get("feature_ids")
        db_tier = db.query(models.Tier).filter(models.Tier.id == tier_id).first()
        if db_tier:
            features = db.query(models.Feature).filter(models.Feature.id.in_(feature_ids)).all()
            db_tier.features = features
            db.commit()
    elif db_req.request_type == "create_tier":
        name = payload.get("name")
        price = payload.get("price", 0.0)
        desc = payload.get("description", "")
        db_tier = models.Tier(name=name, price=price, description=desc)
        db.add(db_tier)
        db.commit()
    elif db_req.request_type == "update_tier":
        tier_id = payload.get("tier_id")
        name = payload.get("name")
        price = payload.get("price")
        desc = payload.get("description", "")
        db_tier = db.query(models.Tier).filter(models.Tier.id == tier_id).first()
        if db_tier:
            db_tier.name = name
            db_tier.price = price
            db_tier.description = desc
            db.commit()
    elif db_req.request_type == "delete_tier":
        tier_id = payload.get("tier_id")
        db_tier = db.query(models.Tier).filter(models.Tier.id == tier_id).first()
        if db_tier:
            db.query(models.User).filter(models.User.tier_id == tier_id).update({models.User.tier_id: None, models.User.tier: 'starter'})
            db.delete(db_tier)
            db.commit()
    elif db_req.request_type == "create_feature":
        name = payload.get("name")
        code = payload.get("code")
        desc = payload.get("description", "")
        db_feat = models.Feature(name=name, code=code, description=desc)
        db.add(db_feat)
        db.commit()
    elif db_req.request_type == "update_global_aml":
        # Make internal request to AML service
        try:
            resp = requests.post("http://aml-service:8002/api/aml/internal/global", json=payload, timeout=5)
            resp.raise_for_status()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update global AML rule: {str(e)}")
    elif db_req.request_type == "update_tier_aml":
        # Make internal request to AML service
        try:
            resp = requests.post("http://aml-service:8002/api/aml/internal/tier", json=payload, timeout=5)
            resp.raise_for_status()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update tier AML rule: {str(e)}")
        
    db_req.status = "approved"
    db_req.checker_id = current_user.id
    db_req.actioned_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_req)
    
    maker_email = db.query(models.User.email).filter(models.User.id == db_req.maker_id).scalar()
    checker_email = current_user.email
    return schemas.ApprovalRequestOut(
        id=db_req.id,
        request_type=db_req.request_type,
        payload=db_req.payload,
        status=db_req.status,
        maker_id=db_req.maker_id,
        checker_id=db_req.checker_id,
        created_at=db_req.created_at,
        actioned_at=db_req.actioned_at,
        rejection_reason=db_req.rejection_reason,
        maker_email=maker_email,
        checker_email=checker_email
    )

@app.post("/api/admin/requests/{request_id}/reject", response_model=schemas.ApprovalRequestOut)
def reject_request(request_id: int, action: schemas.ApprovalRequestAction, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("approve_request"))):
    db_req = db.query(models.ApprovalRequest).filter(models.ApprovalRequest.id == request_id).first()
    if not db_req:
        raise HTTPException(status_code=404, detail="Request not found")
    if db_req.status != "pending":
        raise HTTPException(status_code=400, detail="Request is already actioned")
    if db_req.maker_id == current_user.id:
        raise HTTPException(status_code=400, detail="Maker cannot reject their own request")
        
    db_req.status = "rejected"
    db_req.checker_id = current_user.id
    db_req.actioned_at = datetime.datetime.utcnow()
    db_req.rejection_reason = action.rejection_reason
    db.commit()
    db.refresh(db_req)
    
    maker_email = db.query(models.User.email).filter(models.User.id == db_req.maker_id).scalar()
    checker_email = current_user.email
    return schemas.ApprovalRequestOut(
        id=db_req.id,
        request_type=db_req.request_type,
        payload=db_req.payload,
        status=db_req.status,
        maker_id=db_req.maker_id,
        checker_id=db_req.checker_id,
        created_at=db_req.created_at,
        actioned_at=db_req.actioned_at,
        rejection_reason=db_req.rejection_reason,
        maker_email=maker_email,
        checker_email=checker_email
    )

# RBAC MANAGEMENT ROUTES
@app.get("/api/admin/roles", response_model=List[schemas.RoleOut])
def get_roles(db: Session = Depends(get_db), current_user: models.User = Depends(deps.get_current_admin)):
    return db.query(models.Role).all()

@app.get("/api/admin/permissions", response_model=List[schemas.PermissionOut])
def get_permissions(db: Session = Depends(get_db), current_user: models.User = Depends(deps.get_current_admin)):
    return db.query(models.Permission).all()

@app.put("/api/admin/roles/{role_id}/permissions", response_model=schemas.RoleOut)
def update_role_permissions(role_id: int, data: schemas.RolePermissionsUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("manage_rbac"))):
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    permissions = db.query(models.Permission).filter(models.Permission.id.in_(data.permission_ids)).all()
    db_role.permissions = permissions
    db.commit()
    db.refresh(db_role)
    return db_role

@app.put("/api/admin/users/{user_id}/roles", response_model=schemas.UserAdminView)
def update_user_roles(user_id: int, data: schemas.UserRolesUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(deps.check_permission("manage_rbac"))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot edit your own roles")
    roles = db.query(models.Role).filter(models.Role.id.in_(data.role_ids)).all()
    user.roles = roles
    db.commit()
    db.refresh(user)
    user.tier = user.current_tier.name.lower() if user.current_tier else (user.tier or "starter")
    user.tier_id = user.current_tier.id if user.current_tier else None
    return user

