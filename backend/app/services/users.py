from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.credit_transaction import CreditTransactionType
from app.db.models.user import User
from app.repositories.credits import CreditRepository
from app.repositories.users import UserRepository


class UserService:
    INITIAL_CREDITS = 30

    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._credits = CreditRepository(session)

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
    ) -> User:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is not None:
            return await self._users.update_profile(
                user=user,
                username=username,
                first_name=first_name,
            )

        user = await self._users.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            initial_credits=0,
        )

        await self._credits.create_transaction(
            user=user,
            type=CreditTransactionType.GRANT,
            amount=self.INITIAL_CREDITS,
            reason="Initial free credits",
        )

        return user

    async def get_user(
        self,
        telegram_id: int,
    ) -> User | None:
        return await self._users.get_by_telegram_id(telegram_id)

    async def ban_user(
        self,
        telegram_id: int,
    ) -> User | None:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        return await self._users.set_banned(
            user=user,
            is_banned=True,
        )

    async def unban_user(
        self,
        telegram_id: int,
    ) -> User | None:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        return await self._users.set_banned(
            user=user,
            is_banned=False,
        )