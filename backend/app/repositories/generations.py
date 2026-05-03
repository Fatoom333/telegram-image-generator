from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.generation import Generation, GenerationStatus


class GenerationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        telegram_id: int,
        prompt: str,
        cost_credits: int,
        input_images_cnt: int,
        provider: str | None = None,
        model_name: str | None = None,
        status: GenerationStatus = GenerationStatus.CREATED,
    ) -> Generation:
        generation = Generation(
            telegram_id=telegram_id,
            prompt=prompt,
            status=status,
            provider=provider,
            model_name=model_name,
            input_images_cnt=input_images_cnt,
            cost_credits=cost_credits,
        )

        self._session.add(generation)
        await self._session.flush()

        return generation

    async def get_by_id(self, generation_id: UUID) -> Generation | None:
        result = await self._session.execute(
            select(Generation)
            .where(Generation.id == generation_id)
            .options(selectinload(Generation.images))
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_user(
        self,
        generation_id: UUID,
        telegram_id: int,
    ) -> Generation | None:
        result = await self._session.execute(
            select(Generation)
            .where(
                Generation.id == generation_id,
                Generation.telegram_id == telegram_id,
            )
            .options(selectinload(Generation.images))
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        telegram_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Generation]:
        result = await self._session.execute(
            select(Generation)
            .where(Generation.telegram_id == telegram_id)
            .order_by(Generation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        generation: Generation,
        status: GenerationStatus,
        error_code: str | None = None,
        error_message: str | None = None,
        latency_ms: int | None = None,
    ) -> Generation:
        generation.status = status
        generation.error_code = error_code
        generation.error_message = error_message
        generation.latency_ms = latency_ms

        await self._session.flush()

        return generation

    async def set_running(
        self,
        generation: Generation,
    ) -> Generation:
        generation.status = GenerationStatus.RUNNING

        await self._session.flush()

        return generation

    async def set_succeeded(
        self,
        generation: Generation,
        latency_ms: int,
    ) -> Generation:
        generation.status = GenerationStatus.SUCCEEDED
        generation.error_code = None
        generation.error_message = None
        generation.latency_ms = latency_ms

        await self._session.flush()

        return generation

    async def set_failed(
        self,
        generation: Generation,
        error_code: str,
        error_message: str,
        latency_ms: int | None = None,
    ) -> Generation:
        generation.status = GenerationStatus.FAILED
        generation.error_code = error_code
        generation.error_message = error_message
        generation.latency_ms = latency_ms

        await self._session.flush()

        return generation
