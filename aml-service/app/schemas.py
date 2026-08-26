from pydantic import BaseModel
from typing import List, Optional

class GlobalAMLRuleBase(BaseModel):
    action: str
    limit_amount: float

class GlobalAMLRuleCreate(GlobalAMLRuleBase):
    pass

class GlobalAMLRuleOut(GlobalAMLRuleBase):
    id: int
    class Config:
        from_attributes = True

class TierAMLRuleBase(BaseModel):
    tier_name: str
    action: str
    limit_amount: float

class TierAMLRuleCreate(TierAMLRuleBase):
    pass

class TierAMLRuleOut(TierAMLRuleBase):
    id: int
    class Config:
        from_attributes = True

class AMLLimitsOut(BaseModel):
    global_rules: List[GlobalAMLRuleOut]
    tier_rules: List[TierAMLRuleOut]

class UserLimitRequest(BaseModel):
    tier_name: str
    action: str

class UserLimitOut(BaseModel):
    action: str
    limit_amount: float
    source: str # "global" or "tier"
