from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BalanceResponse(BaseModel):
    credits: int


class CreditTransactionResponse(BaseModel):
    id: UUID
    type: str
    amount: int
    balance_after: int
    reason: str | None
    generation_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)