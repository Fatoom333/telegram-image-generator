import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.credits import CreditRepository
from app.services.exceptions import NotEnoughCreditsError, TooManyInputImagesError
from app.services.generations import GenerationService
from app.services.users import UserService


@pytest.mark.integration
async def test_create_generation_spends_credits(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    generation_service = GenerationService(db_session)
    credit_repository = CreditRepository(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    generation = await generation_service.create_generation(
        telegram_id=user.telegram_id,
        prompt="cute corgi wizard",
        provider="nanobanano",
        model_name="nanobanano-v1",
        input_images_cnt=0,
    )

    transactions = await credit_repository.list_by_user(
        telegram_id=user.telegram_id,
    )

    x = transactions[-1].amount
    assert generation.telegram_id == user.telegram_id
    assert generation.status.value == "queued"
    assert generation.cost_credits == 1
    assert user.credits == 2

    assert len(transactions) == 2
    assert transactions[0].amount == -1



@pytest.mark.integration
async def test_create_generation_rejects_too_many_images(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    generation_service = GenerationService(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    with pytest.raises(TooManyInputImagesError):
        await generation_service.create_generation(
            telegram_id=user.telegram_id,
            prompt="cute corgi wizard",
            provider="nanobanano",
            model_name="nanobanano-v1",
            input_images_cnt=5,
        )


@pytest.mark.integration
async def test_create_generation_rejects_when_not_enough_credits(
    db_session: AsyncSession,
) -> None:
    user_service = UserService(db_session)
    generation_service = GenerationService(db_session)

    user = await user_service.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
    )

    user.credits = 0

    with pytest.raises(NotEnoughCreditsError):
        await generation_service.create_generation(
            telegram_id=user.telegram_id,
            prompt="cute corgi wizard",
            provider="nanobanano",
            model_name="nanobanano-v1",
            input_images_cnt=0,
        )
