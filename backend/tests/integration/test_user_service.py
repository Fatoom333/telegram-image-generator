import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.credits import CreditRepository
from app.services.users import UserService


@pytest.mark.integration
async def test_get_or_create_user_creates_user_with_initial_credits(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    credit_repository = CreditRepository(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    transactions = await credit_repository.list_by_user(
        telegram_id=user.telegram_id,
    )

    assert user.telegram_id == 123456789
    assert user.credits == 3
    assert len(transactions) == 1
    assert transactions[0].amount == 3


@pytest.mark.integration
async def test_get_or_create_user_updates_existing_user(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="old_username",
        first_name="Old",
    )

    updated_user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="new_username",
        first_name="New",
    )

    assert updated_user.telegram_id == user.telegram_id
    assert updated_user.username == "new_username"
    assert updated_user.first_name == "New"