from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TariffResponse(BaseModel):
    id: str
    title: str
    amount_rub: int
    credits: int
    provider: str


class PurchaseCreateRequest(BaseModel):
    tariff_id: str


class PurchaseResponse(BaseModel):
    id: UUID
    telegram_id: int
    amount_rub: int
    credits: int
    status: str
    provider: str
    provider_payment_id: str | None
    payment_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)