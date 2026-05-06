import os
from uuid import uuid4

import pytest

from app.payments.adapters.lava import LavaPaymentAdapter
from app.payments.base import CreatePaymentInput


@pytest.mark.external
@pytest.mark.skipif(
    os.getenv("RUN_EXTERNAL_TESTS") != "true",
    reason="External tests are disabled",
)
@pytest.mark.skipif(
    not os.getenv("LAVA_API_KEY"),
    reason="LAVA_API_KEY is not configured",
)
async def test_lava_payment_adapter_creates_payment() -> None:
    adapter = LavaPaymentAdapter()

    result = await adapter.create_payment(
        CreatePaymentInput(
            purchase_id=uuid4(),
            telegram_id=123456789,
            amount_rub=99,
            credits=50,
            description="Test purchase: 50 credits",
        )
    )

    assert result.provider_payment_id is not None
    assert result.payment_url is not None