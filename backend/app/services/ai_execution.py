from time import perf_counter
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import GenerateInput
from app.ai.registry import AIRegistry
from app.db.models.generation_image import GenerationImageRole
from app.repositories.generation_images import GenerationImageRepository
from app.services.exceptions import AIModelNotFoundError, AIProviderError, AIProviderNotFoundError
from app.services.generations import GenerationService


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

        try:
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

            await self._generation_service.mark_failed(
                generation_id=generation.id,
                error_code="ai_provider_error",
                error_message=str(error),
                latency_ms=latency_ms,
                refund_credits=True,
            )

            raise AIProviderError from error

        latency_ms = int((perf_counter() - started_at) * 1000)

        await self._generation_service.mark_succeeded(
            generation_id=generation.id,
            output_assets=result.assets,
            latency_ms=latency_ms,
        )
