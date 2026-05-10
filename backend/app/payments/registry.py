from dataclasses import dataclass

from app.payments.adapters.yookassa import YooKassaPaymentAdapter
from app.payments.base import PaymentAdapter
from app.services.exceptions import PaymentProviderNotFoundError


@dataclass(frozen=True)
class PaymentProvider:
    id: str
    title: str


class PaymentRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, PaymentAdapter] = {
            YooKassaPaymentAdapter.provider_name: YooKassaPaymentAdapter(),
        }

        self._providers: dict[str, PaymentProvider] = {
            "yookassa": PaymentProvider(
                id="yookassa",
                title="ЮKassa",
            ),
        }

    def get_adapter(self, provider_name: str) -> PaymentAdapter:
        adapter = self._adapters.get(provider_name)

        if adapter is None:
            raise PaymentProviderNotFoundError

        return adapter

    def list_providers(self) -> list[PaymentProvider]:
        return list(self._providers.values())
