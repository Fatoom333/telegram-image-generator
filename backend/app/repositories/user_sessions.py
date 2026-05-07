from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user_session import UserSession


class UserSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(
        self,
        telegram_id: int,
    ) -> UserSession | None:
        result = await self._session.execute(
            select(UserSession).where(UserSession.telegram_id == telegram_id)
        )

        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
    ) -> UserSession:
        session = await self.get_by_telegram_id(telegram_id)

        if session is not None:
            return session

        session = UserSession(
            telegram_id=telegram_id,
            state="idle",
            payload={},
        )

        self._session.add(session)
        await self._session.flush()

        return session

    async def update(
        self,
        session: UserSession,
        state: str,
        payload: dict | None = None,
    ) -> UserSession:
        session.state = state
        session.payload = payload or {}

        await self._session.flush()

        return session

    async def reset(
        self,
        session: UserSession,
    ) -> UserSession:
        session.state = "idle"
        session.payload = {}

        await self._session.flush()

        return session