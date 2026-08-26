import datetime
from typing import Optional
from pydantic import BaseModel

class AddMoneyRequest(BaseModel):
    amount: float

class TransactionOut(BaseModel):
    id: int
    user_id: int
    type: str
    amount: float
    status: str
    details: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class WalletOut(BaseModel):
    user_id: int
    balance: float

    class Config:
        from_attributes = True
