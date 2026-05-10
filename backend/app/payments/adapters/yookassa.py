from decimal import Decimal
from uuid import uuid4

import httpx

from app.core.config import settings
from app.payments.base import CreatePaymentInput, CreatePaymentResult, PaymentAdapter
from app.services.exceptions import PaymentProviderError


class YooKassaPaymentAdapter(PaymentAdapter):
    provider_name = "yookassa"

    async def create_payment(
        self,
        data: CreatePaymentInput,
    ) -> CreatePaymentResult:
        return_url = settings.yookassa_return_url or settings.mini_app_url
        idempotence_key = str(uuid4())

        payload = {
            "amount": {
                "value": self._format_amount(data.amount_rub),
                "currency": "RUB",
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "description": data.description,
            "metadata": {
                "purchase_id": str(data.purchase_id),
                "telegram_id": str(data.telegram_id),
                "credits": str(data.credits),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    "https://api.yookassa.ru/v3/payments",
                    json=payload,
                    auth=(settings.yookassa_shop_id, settings.yookassa_secret_key),
                    headers={
                        "Idempotence-Key": idempotence_key,
                        "Content-Type": "application/json",
                    },
                )
        except httpx.HTTPError as exc:
            raise PaymentProviderError("YooKassa request failed") from exc

        if response.status_code >= 400:
            raise PaymentProviderError(
                f"YooKassa returned {response.status_code}: {response.text}",
            )

        body = response.json()

        provider_payment_id = body.get("id")
        confirmation = body.get("confirmation") or {}
        payment_url = confirmation.get("confirmation_url")

        if not provider_payment_id:
            raise PaymentProviderError("YooKassa response does not contain payment id")

        if not payment_url:
            raise PaymentProviderError("YooKassa response does not contain confirmation_url")

        return CreatePaymentResult(
            provider_payment_id=provider_payment_id,
            payment_url=payment_url,
        )

    @staticmethod
    def _format_amount(amount_rub: int) -> str:
        return f"{Decimal(amount_rub):.2f}"