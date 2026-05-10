from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GenerationAssetResponse(BaseModel):
    id: UUID
    role: str
    asset_type: str
    file_url: str | None = None
    mime_type: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerationResponse(BaseModel):
    id: UUID
    telegram_id: int
    prompt: str
    status: str
    provider: str | None
    model_name: str | None
    input_images_cnt: int
    cost_credits: int
    error_code: str | None
    error_message: str | None
    latency_ms: int | None
    created_at: datetime
    updated_at: datetime

    assets: list[GenerationAssetResponse] = Field(default_factory=list)

    # Временная совместимость со старым frontend, который ждёт images.
    images: list[GenerationAssetResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)