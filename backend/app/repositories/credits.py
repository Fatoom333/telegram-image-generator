from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.credit_transaction import CreditTransaction, CreditTransactionType
from app.db.models.user import User


class CreditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_transaction(
        self,
        user: User,
        type: CreditTransactionType,
        amount: int,
        reason: str | None = None,
        generation_id: UUID | None = None,
    ) -> CreditTransaction:
        user.credits += amount

        transaction = CreditTransaction(
            telegram_id=user.telegram_id,
            generation_id=generation_id,
            type=type,
            amount=amount,
            balance_after=user.credits,
            reason=reason,
        )

        self._session.add(transaction)
        await self._session.flush()

        return transaction

    async def list_by_user(
        self,
        telegram_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CreditTransaction]:
        result = await self._session.execute(
            select(CreditTransaction)
            .where(CreditTransaction.telegram_id == telegram_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())