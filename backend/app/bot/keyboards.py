from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.core.config import settings


def start_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Открыть Mini App",
                    web_app=WebAppInfo(url=settings.mini_app_url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Помощь",
                    callback_data="help",
                )
            ],
        ]
    )


def help_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Открыть Mini App",
                    web_app=WebAppInfo(url=settings.mini_app_url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="start",
                )
            ],
        ]
    )