from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.purchase import Purchase, PurchaseStatus
from app.payments.base import CreatePaymentInput
from app.payments.catalog import PaymentCatalog, PaymentTariff
from app.payments.registry import PaymentRegistry
from app.repositories.purchases import PurchaseRepository
from app.repositories.users import UserRepository
from app.services.credits import CreditService
from app.services.exceptions import PurchaseAlreadyProcessedError, PurchaseNotFoundError, UserNotFoundError


class PurchaseService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._purchases = PurchaseRepository(session)
        self._credits = CreditService(session)
        self._payment_catalog = PaymentCatalog()
        self._payment_registry = PaymentRegistry()

    async def list_tariffs(self) -> list[PaymentTariff]:
        return self._payment_catalog.list_tariffs()

    async def create_purchase(
            self,
            telegram_id: int,
            tariff_id: str,
            provider: str,
    ) -> Purchase:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        tariff = self._payment_catalog.get_tariff(tariff_id)
        adapter = self._payment_registry.get_adapter(provider)

        purchase = await self._purchases.create(
            telegram_id=telegram_id,
            amount_rub=tariff.amount_rub,
            credits=tariff.credits,
            provider=provider,
            status=PurchaseStatus.CREATED,
        )

        payment_result = await adapter.create_payment(
            CreatePaymentInput(
                purchase_id=purchase.id,
                telegram_id=telegram_id,
                amount_rub=tariff.amount_rub,
                credits=tariff.credits,
                description=tariff.title,
            )
        )

        purchase = await self._purchases.set_provider_data(
            purchase=purchase,
            provider_payment_id=payment_result.provider_payment_id,
            payment_url=payment_result.payment_url,
        )

        return purchase

    async def approve_purchase(
            self,
            purchase_id: UUID,
    ) -> Purchase:
        purchase = await self._purchases.get_by_id(purchase_id)

        if purchase is None:
            raise PurchaseNotFoundError

        if purchase.status == PurchaseStatus.SUCCEEDED:
            raise PurchaseAlreadyProcessedError

        purchase = await self._purchases.update_status(
            purchase=purchase,
            status=PurchaseStatus.SUCCEEDED,
        )

        await self._credits.grant(
            telegram_id=purchase.telegram_id,
            amount=purchase.credits,
            reason=f"Purchase {purchase.id}",
        )

        return purchase

    async def fail_purchase(
            self,
            purchase_id: UUID,
    ) -> Purchase:
        purchase = await self._purchases.get_by_id(purchase_id)

        if purchase is None:
            raise PurchaseNotFoundError

        if purchase.status == PurchaseStatus.SUCCEEDED:
            raise PurchaseAlreadyProcessedError

        return await self._purchases.update_status(
            purchase=purchase,
            status=PurchaseStatus.FAILED,
        )

    async def list_user_purchases(
            self,
            telegram_id: int,
            limit: int = 20,
            offset: int = 0,
    ) -> list[Purchase]:
        user = await self._users.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundError

        return await self._purchases.list_by_user(
            telegram_id=telegram_id,
            limit=limit,
            offset=offset,
        )

    async def list_payment_providers(self):
        return self._payment_registry.list_providers()
