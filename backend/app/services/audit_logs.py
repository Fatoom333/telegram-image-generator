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
        payload: dict | None = None,
    ) -> AuditLog:
        return await self._audit_logs.create(
            action=action,
            actor_telegram_id=actor_telegram_id,
            target_telegram_id=target_telegram_id,
            payload=payload,
        )

    async def log_admin_action(
        self,
        action: str,
        admin_telegram_id: int,
        target_telegram_id: int | None = None,
        payload: dict | None = None,
    ) -> AuditLog:
        return await self.log(
            action=action,
            actor_telegram_id=admin_telegram_id,
            target_telegram_id=target_telegram_id,
            payload=payload,
        )

    async def list_user_audit_logs(
        self,
        target_telegram_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        return await self._audit_logs.list_by_target(
            target_telegram_id=target_telegram_id,
            limit=limit,
            offset=offset,
        )
