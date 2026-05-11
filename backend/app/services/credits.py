from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.credit_transaction import CreditTransaction, CreditTransactionType
from app.db.models.user import User
from app.repositories.credits import CreditRepository
from app.repositories.users import UserRepository
from app.services.audit_logs import AuditLogService
from app.services.exceptions import NotEnoughCreditsError, UserNotFoundError


class CreditService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._credits = CreditRepository(session)
        self._audit_logs = AuditLogService(session)

    async def get_balance(
            self,
            telegram_id: int,
    ) -> int:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        return user.credits

    async def list_transactions(
            self,
            telegram_id: int,
            limit: int = 50,
            offset: int = 0,
    ) -> list[CreditTransaction]:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        return await self._credits.list_by_user(
            telegram_id=telegram_id,
            limit=limit,
            offset=offset,
        )

    async def spend(
            self,
            user: User,
            amount: int,
            generation_id: UUID | None = None,
            reason: str | None = None,
    ) -> None:
        if amount <= 0:
            raise ValueError("Spend amount must be positive")

        if user.credits < amount:
            raise NotEnoughCreditsError

        await self._credits.create_transaction(
            user=user,
            type=CreditTransactionType.SPEND,
            amount=-amount,
            reason=reason,
            generation_id=generation_id,
        )

    async def refund(
            self,
            telegram_id: int,
            amount: int,
            reason: str | None = None,
            actor_telegram_id: int | None = None,
            source: str = "system",
            payload: dict | None = None,
    ) -> None:
        if amount <= 0:
            raise ValueError("Refund amount must be positive")

        user = await self._users.get_by_telegram_id(telegram_id)
        if user is None:
            raise UserNotFoundError

        balance_before = user.credits

        await self._credits.create_transaction(
            user=user,
            type=CreditTransactionType.REFUND,
            amount=amount,
            reason=reason,
        )

        await self._audit_logs.log(
            action="credits.refunded",
            actor_telegram_id=actor_telegram_id,
            target_telegram_id=telegram_id,
            payload={
                "amount": amount,
                "reason": reason,
                "source": source,
                "balance_before": balance_before,
                "balance_after": user.credits,
                **(payload or {}),
            },
        )

    async def grant(
            self,
            telegram_id: int,
            amount: int,
            reason: str | None = None,
    ) -> None:
        if amount <= 0:
            raise ValueError("Grant amount must be positive")

        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        await self._credits.create_transaction(
            user=user,
            type=CreditTransactionType.GRANT,
            amount=amount,
            reason=reason,
        )

    async def purchase(
            self,
            telegram_id: int,
            amount: int,
            reason: str | None = None,
    ) -> None:
        if amount <= 0:
            raise ValueError("Purchase amount must be positive")

        user = await self._users.get_by_telegram_id(telegram_id)
        if user is None:
            raise UserNotFoundError

        await self._credits.create_transaction(
            user=user,
            type=CreditTransactionType.PURCHASE,
            amount=amount,
            reason=reason,
        )

    async def admin_adjust(
            self,
            telegram_id: int,
            amount: int,
            reason: str | None = None,
            actor_telegram_id: int | None = None,
    ) -> None:
        if amount == 0:
            raise ValueError("Adjustment amount must not be zero")

        user = await self._users.get_by_telegram_id(telegram_id)
        if user is None:
            raise UserNotFoundError

        if user.credits + amount < 0:
            raise NotEnoughCreditsError

        balance_before = user.credits

        await self._credits.create_transaction(
            user=user,
            type=CreditTransactionType.ADMIN_ADJUSTMENT,
            amount=amount,
            reason=reason,
        )

        await self._audit_logs.log(
            action="credits.admin_adjusted",
            actor_telegram_id=actor_telegram_id,
            target_telegram_id=telegram_id,
            payload={
                "amount": amount,
                "reason": reason,
                "balance_before": balance_before,
                "balance_after": user.credits,
            },
        )
