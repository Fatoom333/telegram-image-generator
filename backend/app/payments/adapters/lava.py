from app.core.config import settings
from app.payments.base import CreatePaymentInput, CreatePaymentResult, PaymentAdapter


class LavaPaymentAdapter(PaymentAdapter):
    provider_name = "lava"

    def __init__(self) -> None:
        self._api_key = settings.lava_api_key

    async def create_payment(
        self,
        data: CreatePaymentInput,
    ) -> CreatePaymentResult:
        # TODO: здесь позже будет реальный запрос к Lava API.
        #
        # Ожидаемая логика:
        # 1. Отправить purchase_id, amount_rub, description в Lava.
        # 2. Получить payment_url.
        # 3. Получить provider_payment_id.
        # 4. Вернуть их в PaymentService.
        #
        # Пока оставляем заглушку, чтобы архитектура уже поддерживала Lava.
        raise NotImplementedError("Lava payment adapter is not implemented yet")
