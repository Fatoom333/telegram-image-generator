from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        action: str,
        actor_telegram_id: int | None = None,
        target_telegram_id: int | None = None,
        payload: dict | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_telegram_id=actor_telegram_id,
            target_telegram_id=target_telegram_id,
            action=action,
            payload=payload or {},
        )

        self._session.add(log)
        await self._session.flush()

        return log

    async def list_by_target(
        self,
        target_telegram_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        result = await self._session.execute(
            select(AuditLog)
            .where(AuditLog.target_telegram_id == target_telegram_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())
