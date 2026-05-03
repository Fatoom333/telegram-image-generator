from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.purchase import Purchase, PurchaseStatus


class PurchaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        telegram_id: int,
        amount_rub: int,
        credits: int,
        provider: str,
        status: PurchaseStatus = PurchaseStatus.CREATED,
    ) -> Purchase:
        purchase = Purchase(
            telegram_id=telegram_id,
            amount_rub=amount_rub,
            credits=credits,
            provider=provider,
            status=status,
        )

        self._session.add(purchase)
        await self._session.flush()

        return purchase

    async def get_by_id(self, purchase_id: UUID) -> Purchase | None:
        result = await self._session.execute(
            select(Purchase).where(Purchase.id == purchase_id)
        )

        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        telegram_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Purchase]:
        result = await self._session.execute(
            select(Purchase)
            .where(Purchase.telegram_id == telegram_id)
            .order_by(Purchase.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        purchase: Purchase,
        status: PurchaseStatus,
    ) -> Purchase:
        purchase.status = status

        await self._session.flush()

        return purchase
