from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.generation_image import GenerationImage, GenerationImageRole


class GenerationImageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        generation_id: UUID,
        role: GenerationImageRole,
        file_path: str,
        telegram_file_id: str | None = None,
        mime_type: str | None = None,
    ) -> GenerationImage:
        image = GenerationImage(
            generation_id=generation_id,
            role=role,
            file_path=file_path,
            telegram_file_id=telegram_file_id,
            mime_type=mime_type,
        )

        self._session.add(image)
        await self._session.flush()

        return image

    async def list_by_generation(
        self,
        generation_id: UUID,
    ) -> list[GenerationImage]:
        result = await self._session.execute(
            select(GenerationImage)
            .where(GenerationImage.generation_id == generation_id)
            .order_by(GenerationImage.created_at.asc())
        )

        return list(result.scalars().all())

    async def list_outputs_by_generation(
        self,
        generation_id: UUID,
    ) -> list[GenerationImage]:
        result = await self._session.execute(
            select(GenerationImage)
            .where(
                GenerationImage.generation_id == generation_id,
                GenerationImage.role == GenerationImageRole.OUTPUT,
            )
            .order_by(GenerationImage.created_at.asc())
        )

        return list(result.scalars().all())
