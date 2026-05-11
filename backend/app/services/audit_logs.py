from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_log import AuditLog
from app.repositories.audit_logs import AuditLogRepository


class AuditLogService:
    def __init__(self, session: AsyncSession) -> None:
        self._audit_logs = AuditLogRepository(session)

    async def log(
            self,
            action: str,
            actor_telegram_id: int | None = None,
            target_telegram_id: int | None = None,
            payload: dict[str, Any] | None = None,
    ) -> AuditLog:
        return await self._audit_logs.create(
            action=action,
            actor_telegram_id=actor_telegram_id,
            target_telegram_id=target_telegram_id,
            payload=payload,
        )
