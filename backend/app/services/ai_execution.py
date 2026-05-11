import logging
from time import perf_counter
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import GenerateInput
from app.ai.registry import AIRegistry
from app.db.models.generation_image import GenerationImageRole
from app.repositories.generation_images import GenerationImageRepository
from app.services.exceptions import AIModelNotFoundError, AIProviderNotFoundError
from app.services.generations import GenerationService

logger = logging.getLogger(__name__)


class AIExecutionService:
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self._generation_service = GenerationService(session)
        self._generation_images = GenerationImageRepository(session)
        self._ai_registry = AIRegistry()

    async def execute_generation(
            self,
            generation_id: UUID,
    ) -> None:
        started_at = perf_counter()
        generation = await self._generation_service.get_generation(generation_id)

        try:
            if generation.provider is None:
                raise AIProviderNotFoundError

            if generation.model_name is None:
                raise AIModelNotFoundError

            await self._generation_service.mark_running(generation_id)

            input_assets = await self._generation_images.list_inputs_by_generation(
                generation_id=generation.id,
            )
            input_asset_paths = [
                asset.file_path
                for asset in input_assets
                if asset.role == GenerationImageRole.INPUT
            ]

            adapter = self._ai_registry.get_adapter(generation.provider)

            result = await adapter.generate(
                GenerateInput(
                    generation_id=generation.id,
                    prompt=generation.prompt,
                    input_asset_paths=input_asset_paths,
                    model_name=generation.model_name,
                )
            )

        except Exception as error:
            latency_ms = int((perf_counter() - started_at) * 1000)

            logger.exception(
                "Generation failed",
                extra={
                    "generation_id": str(generation.id),
                    "telegram_id": generation.telegram_id,
                    "provider": generation.provider,
                    "model_name": generation.model_name,
                },
            )

            await self._generation_service.mark_failed(
                generation_id=generation.id,
                error_code=_get_generation_error_code(error),
                error_message=str(error),
                latency_ms=latency_ms,
                refund_credits=True,
            )

            return

        latency_ms = int((perf_counter() - started_at) * 1000)

        await self._generation_service.mark_succeeded(
            generation_id=generation.id,
            output_assets=result.assets,
            latency_ms=latency_ms,
        )


def _get_generation_error_code(error: Exception) -> str:
    if isinstance(error, AIProviderNotFoundError):
        return "ai_provider_not_found"

    if isinstance(error, AIModelNotFoundError):
        return "ai_model_not_found"

    return "ai_provider_error"
