from fastapi import APIRouter

from app.ai.model_catalog import ModelCatalog
from app.schemas.ai_models import AIModelResponse


router = APIRouter(prefix="/ai/models", tags=["ai-models"])


@router.get("", response_model=list[AIModelResponse])
async def list_ai_models() -> list:
    catalog = ModelCatalog()

    return catalog.list_models()
