from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GenerationImageResponse(BaseModel):
    id: UUID
    role: str
    file_url: str | None = None
    mime_type: str | None
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
    images: list[GenerationImageResponse] = []

    model_config = ConfigDict(from_attributes=True)