import time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.purchase import PurchaseStatus
from app.repositories.credits import CreditRepository
from app.repositories.users import UserRepository
from app.services.exceptions import PaymentTariffNotFoundError, PurchaseAlreadyProcessedError
from app.services.purchases import PurchaseService
from app.services.users import UserService


@pytest.mark.integration
async def test_purchase_service_lists_tariffs(
    db_session: AsyncSession,
) -> None:
    purchase_service = PurchaseService(db_session)

    tariffs = await purchase_service.list_tariffs()

    assert len(tariffs) > 0
    assert any(tariff.id == "credits_50_manual" for tariff in tariffs)


@pytest.mark.integration
async def test_purchase_service_creates_manual_purchase(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    purchase_service = PurchaseService(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    purchase = await purchase_service.create_purchase(
        telegram_id=user.telegram_id,
        tariff_id="credits_50_manual",
    )

    assert purchase.telegram_id == user.telegram_id
    assert purchase.amount_rub == 99
    assert purchase.credits == 50
    assert purchase.provider == "manual"
    assert purchase.status == PurchaseStatus.CREATED
    assert purchase.provider_payment_id is None
    assert purchase.payment_url is None


@pytest.mark.integration
async def test_purchase_service_approves_purchase_and_grants_credits(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    user_repository = UserRepository(db_session)
    credit_repository = CreditRepository(db_session)
    purchase_service = PurchaseService(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    time.sleep(3)
    purchase = await purchase_service.create_purchase(
        telegram_id=user.telegram_id,
        tariff_id="credits_50_manual",
    )

    approved_purchase = await purchase_service.approve_purchase(purchase.id)

    updated_user = await user_repository.get_by_telegram_id(user.telegram_id)
    transactions = await credit_repository.list_by_user(user.telegram_id)

    assert updated_user is not None
    assert approved_purchase.status == PurchaseStatus.SUCCEEDED
    assert updated_user.credits == 53

    assert len(transactions) == 2
    assert transactions[0].amount == 50
    assert transactions[1].amount == 3


@pytest.mark.integration
async def test_purchase_service_rejects_unknown_tariff(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    purchase_service = PurchaseService(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    with pytest.raises(PaymentTariffNotFoundError):
        await purchase_service.create_purchase(
            telegram_id=user.telegram_id,
            tariff_id="unknown_tariff",
        )


@pytest.mark.integration
async def test_purchase_service_rejects_double_approve(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    purchase_service = PurchaseService(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    purchase = await purchase_service.create_purchase(
        telegram_id=user.telegram_id,
        tariff_id="credits_50_manual",
    )

    await purchase_service.approve_purchase(purchase.id)

    with pytest.raises(PurchaseAlreadyProcessedError):
        await purchase_service.approve_purchase(purchase.id)