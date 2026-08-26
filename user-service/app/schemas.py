import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

class PermissionOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionOut] = []

    class Config:
        from_attributes = True

class FeatureOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class FeatureCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class TierOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    features: List[FeatureOut] = []

    class Config:
        from_attributes = True

class TierCreate(BaseModel):
    name: str
    price: float = 0.0
    description: Optional[str] = None

class TierUpdate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class TierFeaturesUpdate(BaseModel):
    feature_ids: List[int]

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    tier: Optional[str] = "starter"

class UserLogin(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    account_number: Optional[str] = None
    role: str
    tier: Optional[str] = None
    tier_id: Optional[int] = None
    is_active: bool
    created_at: datetime.datetime
    roles: List[RoleOut] = []

    class Config:
        from_attributes = True

class UserUpdateRole(BaseModel):
    role: str

class UserUpdateTier(BaseModel):
    tier: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    tier: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None

class CandleData(BaseModel):
    time: int  # Unix timestamp in seconds
    open: float
    high: float
    low: float
    close: float
    volume: float

class AdminStats(BaseModel):
    total_users: int
    admin_users: int
    regular_users: int
    system_status: str
    memory_usage: str

class UserAdminView(BaseModel):
    id: int
    account_number: Optional[str] = None
    email: str
    role: str
    tier: Optional[str] = None
    tier_id: Optional[int] = None
    is_active: bool
    created_at: datetime.datetime
    roles: List[RoleOut] = []

    class Config:
        from_attributes = True

class ApprovalRequestCreate(BaseModel):
    request_type: str # e.g. "change_user_tier", "update_tier_features", "create_tier"
    payload: str # JSON-encoded parameters

class ApprovalRequestAction(BaseModel):
    rejection_reason: Optional[str] = None

class ApprovalRequestOut(BaseModel):
    id: int
    request_type: str
    payload: str
    status: str
    maker_id: int
    checker_id: Optional[int] = None
    created_at: datetime.datetime
    actioned_at: Optional[datetime.datetime] = None
    rejection_reason: Optional[str] = None
    maker_email: Optional[str] = None
    checker_email: Optional[str] = None

    class Config:
        from_attributes = True

class RolePermissionsUpdate(BaseModel):
    permission_ids: List[int]

class UserRolesUpdate(BaseModel):
    role_ids: List[int]
