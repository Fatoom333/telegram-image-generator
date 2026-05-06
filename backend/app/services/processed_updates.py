from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.processed_updates import ProcessedUpdateRepository
from app.services.exceptions import DuplicateUpdateError


class ProcessedUpdateService:
    def __init__(self, session: AsyncSession) -> None:
        self._processed_updates = ProcessedUpdateRepository(session)

    async def ensure_not_processed(
        self,
        update_id: int,
    ) -> None:
        exists = await self._processed_updates.exists(update_id)

        if exists:
            raise DuplicateUpdateError

    async def mark_processed(
        self,
        update_id: int,
        telegram_id: int | None = None,
    ) -> None:
        await self._processed_updates.create(
            update_id=update_id,
            telegram_id=telegram_id,
        )

    async def process_once(
        self,
        update_id: int,
        telegram_id: int | None = None,
    ) -> None:
        await self.ensure_not_processed(update_id)
        await self.mark_processed(
            update_id=update_id,
            telegram_id=telegram_id,
        )
