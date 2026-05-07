from app.payments.adapters.lava import LavaPaymentAdapter
from app.payments.adapters.manual import ManualPaymentAdapter
from app.payments.base import PaymentAdapter
from app.services.exceptions import PaymentProviderNotFoundError


class PaymentRegistry:
    def __init__(self) -> None:
        # Здесь регистрируются платёжные адаптеры.
        #
        # Как добавить нового провайдера оплаты:
        # 1. Создай adapter в app/payments/adapters/.
        #    Например: sbp.py, yookassa.py, cryptomus.py.
        # 2. Adapter должен наследоваться от PaymentAdapter.
        # 3. У adapter должен быть provider_name.
        #    Например: provider_name = "sbp".
        # 4. Импортируй adapter здесь.
        # 5. Добавь его в self._adapters.
        #
        # provider_name должен совпадать с provider в PaymentCatalog.
        self._adapters: dict[str, PaymentAdapter] = {
            ManualPaymentAdapter.provider_name: ManualPaymentAdapter(),
            LavaPaymentAdapter.provider_name: LavaPaymentAdapter(),

            # Пример будущего adapter:
            # SbpPaymentAdapter.provider_name: SbpPaymentAdapter(),
        }

    def get_adapter(
        self,
        provider_name: str,
    ) -> PaymentAdapter:
        adapter = self._adapters.get(provider_name)

        if adapter is None:
            raise PaymentProviderNotFoundError

        return adapter
