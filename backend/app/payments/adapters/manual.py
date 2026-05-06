from app.payments.base import CreatePaymentInput, CreatePaymentResult, PaymentAdapter


class ManualPaymentAdapter(PaymentAdapter):
    provider_name = "manual"

    async def create_payment(
        self,
        data: CreatePaymentInput,
    ) -> CreatePaymentResult:
        # Manual provider — это MVP-заглушка.
        #
        # Здесь не создаётся настоящая платёжная ссылка.
        # Покупка создаётся в БД, а админ потом вручную подтверждает её.
        #
        # Frontend может показать пользователю текст:
        # "Заявка создана. Администратор начислит кредиты после проверки оплаты."
        return CreatePaymentResult(
            provider_payment_id=None,
            payment_url=None,
        )
