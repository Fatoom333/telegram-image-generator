from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.model_catalog import ModelCatalog
from app.db.models.generation import Generation, GenerationStatus
from app.db.models.generation_image import GenerationImageRole
from app.repositories.generation_images import GenerationImageRepository
from app.repositories.generations import GenerationRepository
from app.repositories.users import UserRepository
from app.services.credits import CreditService
from app.services.exceptions import (
    EmptyPromptError,
    GenerationNotFoundError,
    TooManyInputImagesError,
    UserBannedError,
    UserNotFoundError,
)


class GenerationService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._generations = GenerationRepository(session)
        self._generation_images = GenerationImageRepository(session)
        self._credits = CreditService(session)
        self._model_catalog = ModelCatalog()

    async def create_generation(
            self,
            telegram_id: int,
            prompt: str,
            provider: str | None = None,
            model_name: str | None = None,
            input_images_cnt: int = 0,
    ) -> Generation:
        normalized_prompt = prompt.strip()

        if not normalized_prompt:
            raise EmptyPromptError

        selected_model = self._resolve_model(
            provider=provider,
            model_name=model_name,
        )

        if input_images_cnt > selected_model.max_input_images:
            raise TooManyInputImagesError

        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        if user.is_banned:
            raise UserBannedError

        cost = self._model_catalog.calculate_cost(
            provider=selected_model.provider,
            model_name=selected_model.model_name,
            input_images_cnt=input_images_cnt,
        )

        generation = await self._generations.create(
            telegram_id=telegram_id,
            prompt=normalized_prompt,
            cost_credits=cost,
            input_images_cnt=input_images_cnt,
            provider=selected_model.provider,
            model_name=selected_model.model_name,
            status=GenerationStatus.QUEUED,
        )

        await self._credits.spend(
            user=user,
            amount=cost,
            generation_id=generation.id,
            reason="Image generation",
        )

        return generation

    async def get_generation_for_user(
        self,
        generation_id: UUID,
        telegram_id: int,
    ) -> Generation:
        generation = await self._generations.get_by_id_for_user(
            generation_id=generation_id,
            telegram_id=telegram_id,
        )

        if generation is None:
            raise GenerationNotFoundError

        return generation

    async def get_generation(
        self,
        generation_id: UUID,
    ) -> Generation:
        generation = await self._generations.get_by_id(generation_id)

        if generation is None:
            raise GenerationNotFoundError

        return generation

    async def list_user_generations(
        self,
        telegram_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Generation]:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        return await self._generations.list_by_user(
            telegram_id=telegram_id,
            limit=limit,
            offset=offset,
        )

    async def mark_running(
        self,
        generation_id: UUID,
    ) -> Generation:
        generation = await self.get_generation(generation_id)

        return await self._generations.set_running(generation)

    async def mark_succeeded(
        self,
        generation_id: UUID,
        output_image_paths: list[str],
        latency_ms: int,
    ) -> Generation:
        generation = await self.get_generation(generation_id)

        for file_path in output_image_paths:
            await self._generation_images.create(
                generation_id=generation.id,
                role=GenerationImageRole.OUTPUT,
                file_path=file_path,
            )

        return await self._generations.set_succeeded(
            generation=generation,
            latency_ms=latency_ms,
        )

    async def mark_failed(
        self,
        generation_id: UUID,
        error_code: str,
        error_message: str,
        latency_ms: int | None = None,
        refund_credits: bool = True,
    ) -> Generation:
        generation = await self.get_generation(generation_id)

        failed_generation = await self._generations.set_failed(
            generation=generation,
            error_code=error_code,
            error_message=error_message,
            latency_ms=latency_ms,
        )

        if refund_credits and generation.cost_credits > 0:
            user = await self._users.get_by_telegram_id(generation.telegram_id)

            if user is not None:
                await self._credits.refund(
                    user=user,
                    amount=generation.cost_credits,
                    generation_id=generation.id,
                    reason="Generation failed",
                )

        return failed_generation

    def _resolve_model(
        self,
        provider: str | None,
        model_name: str | None,
    ):
        if provider is None and model_name is None:
            return self._model_catalog.get_default_model()

        if provider is None or model_name is None:
            return self._model_catalog.get_default_model()

        return self._model_catalog.get_model(
            provider=provider,
            model_name=model_name,
        )

    async def add_input_images(
            self,
            generation_id: UUID,
            input_image_paths: list[str],
    ) -> None:
        generation = await self.get_generation(generation_id)

        for file_path in input_image_paths:
            await self._generation_images.create(
                generation_id=generation.id,
                role=GenerationImageRole.INPUT,
                file_path=file_path,
            )