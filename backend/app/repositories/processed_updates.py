from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.processed_update import ProcessedUpdate


class ProcessedUpdateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(
        self,
        update_id: int,
    ) -> bool:
        result = await self._session.execute(
            select(ProcessedUpdate.update_id).where(
                ProcessedUpdate.update_id == update_id
            )
        )

        return result.scalar_one_or_none() is not None

    async def create(
        self,
        update_id: int,
        telegram_id: int | None = None,
    ) -> ProcessedUpdate:
        processed_update = ProcessedUpdate(
            update_id=update_id,
            telegram_id=telegram_id,
        )

        self._session.add(processed_update)
        await self._session.flush()

        return processed_update