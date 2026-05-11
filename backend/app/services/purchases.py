from uuid import UUID
import httpx
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.purchase import Purchase, PurchaseStatus
from app.payments.base import CreatePaymentInput
from app.payments.catalog import PaymentCatalog, PaymentTariff
from app.payments.registry import PaymentRegistry
from app.repositories.purchases import PurchaseRepository
from app.repositories.users import UserRepository
from app.services.audit_logs import AuditLogService
from app.services.credits import CreditService
from app.services.exceptions import PurchaseAlreadyProcessedError, PurchaseNotFoundError, UserNotFoundError


class PurchaseService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._purchases = PurchaseRepository(session)
        self._credits = CreditService(session)
        self._audit_logs = AuditLogService(session)
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

        await self._audit_logs.log(
            action="purchase.created",
            actor_telegram_id=telegram_id,
            target_telegram_id=telegram_id,
            payload={
                "purchase_id": str(purchase.id),
                "tariff_id": tariff_id,
                "provider": provider,
                "provider_payment_id": purchase.provider_payment_id,
                "amount_rub": purchase.amount_rub,
                "credits": purchase.credits,
                "status": purchase.status.value,
            },
        )

        return purchase

    async def approve_purchase(
            self,
            purchase_id: UUID,
            actor_telegram_id: int | None = None,
            source: str = "system",
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

        await self._credits.purchase(
            telegram_id=purchase.telegram_id,
            amount=purchase.credits,
            reason=f"Purchase {purchase.id}",
        )

        await self._audit_logs.log(
            action="purchase.succeeded",
            actor_telegram_id=actor_telegram_id,
            target_telegram_id=purchase.telegram_id,
            payload={
                "purchase_id": str(purchase.id),
                "provider": purchase.provider,
                "provider_payment_id": purchase.provider_payment_id,
                "amount_rub": purchase.amount_rub,
                "credits": purchase.credits,
                "source": source,
            },
        )

        return purchase

    async def fail_purchase(
            self,
            purchase_id: UUID,
            actor_telegram_id: int | None = None,
            source: str = "system",
    ) -> Purchase:
        purchase = await self._purchases.get_by_id(purchase_id)
        if purchase is None:
            raise PurchaseNotFoundError

        if purchase.status == PurchaseStatus.SUCCEEDED:
            raise PurchaseAlreadyProcessedError

        purchase = await self._purchases.update_status(
            purchase=purchase,
            status=PurchaseStatus.FAILED,
        )

        await self._audit_logs.log(
            action="purchase.failed",
            actor_telegram_id=actor_telegram_id,
            target_telegram_id=purchase.telegram_id,
            payload={
                "purchase_id": str(purchase.id),
                "provider": purchase.provider,
                "provider_payment_id": purchase.provider_payment_id,
                "amount_rub": purchase.amount_rub,
                "credits": purchase.credits,
                "source": source,
            },
        )

        return purchase

    async def handle_yookassa_webhook(self, payload: dict[str, Any]) -> None:
        event = payload.get("event")
        payment_object = payload.get("object")

        if not isinstance(payment_object, dict):
            return

        provider_payment_id = payment_object.get("id")

        if not isinstance(provider_payment_id, str):
            return

        if event not in {"payment.succeeded", "payment.canceled"}:
            return

        verified_payment = await self._get_yookassa_payment(provider_payment_id)

        if verified_payment.get("id") != provider_payment_id:
            return

        purchase = await self._purchases.get_by_provider_payment_id(
            provider="yookassa",
            provider_payment_id=provider_payment_id,
        )

        if purchase is None:
            return

        status = verified_payment.get("status")
        paid = verified_payment.get("paid") is True

        if status == "succeeded" and paid:
            if purchase.status != PurchaseStatus.SUCCEEDED:
                await self.approve_purchase(
                    purchase_id=purchase.id,
                    source="yookassa_webhook",
                )

            return

        if status == "canceled":
            if purchase.status != PurchaseStatus.SUCCEEDED:
                await self.fail_purchase(
                    purchase_id=purchase.id,
                    source="yookassa_webhook",
                )

    async def _get_yookassa_payment(self, payment_id: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"https://api.yookassa.ru/v3/payments/{payment_id}",
                    auth=(settings.yookassa_shop_id, settings.yookassa_secret_key),
                )
        except httpx.HTTPError:
            return {}

        if response.status_code >= 400:
            return {}

        body = response.json()

        if not isinstance(body, dict):
            return {}

        return body

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
