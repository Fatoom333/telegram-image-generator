from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self._session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        initial_credits: int = 0,
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            credits=initial_credits,
        )

        self._session.add(user)
        await self._session.flush()

        return user

    async def update_profile(
        self,
        user: User,
        username: str | None,
        first_name: str | None,
    ) -> User:
        user.username = username
        user.first_name = first_name

        await self._session.flush()

        return user

    async def set_banned(
        self,
        user: User,
        is_banned: bool,
    ) -> User:
        user.is_banned = is_banned

        await self._session.flush()

        return user

    async def update_credits(
        self,
        user: User,
        credits: int,
    ) -> User:
        user.credits = credits

        await self._session.flush()

        return user