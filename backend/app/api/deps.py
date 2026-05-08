from datetime import timedelta

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram_init_data import (
    TelegramInitDataError,
    TelegramMiniAppUser,
    validate_telegram_init_data,
)
from app.core.config import settings
from app.core.database import get_db_session
from app.db.models.user import User
from app.services.users import UserService


async def get_current_telegram_user(
    x_telegram_init_data: str | None = Header(default=None),
) -> TelegramMiniAppUser:
    if x_telegram_init_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Telegram-Init-Data header",
        )

    try:
        return validate_telegram_init_data(
            init_data=x_telegram_init_data,
            bot_token=settings.telegram_bot_token,
            max_age=timedelta(hours=24),
        )
    except TelegramInitDataError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        ) from error


async def get_current_user(
    telegram_user: TelegramMiniAppUser = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    async with session.begin():
        user_service = UserService(session)
        user = await user_service.get_or_create_user(
            telegram_id=telegram_user.telegram_id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
        )

    return user

async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.telegram_id not in settings.admin_telegram_id_set:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user