import datetime
from typing import Optional
from pydantic import BaseModel

class TransferMoneyRequest(BaseModel):
    recipient_account_number: str
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
