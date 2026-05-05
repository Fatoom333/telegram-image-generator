import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.bot.keyboards import start_inline_keyboard


router = Router()


START_TEXT = (
    "Привет! 👋\n\n"
    "Я бот для генерации изображений через Telegram Mini App.\n\n"
    "Что можно будет делать в приложении:\n"
    "• писать текстовый prompt;\n"
    "• добавлять изображения-референсы;\n"
    "• получать готовые изображения;\n"
    "• смотреть баланс кредитов;\n"
    "• смотреть историю генераций;\n"
    "• пополнять баланс.\n\n"
    "Нажми кнопку ниже, чтобы открыть Mini App."
)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    cleanup_message = await message.answer(
        text="Обновляю меню...",
        reply_markup=ReplyKeyboardRemove(),
    )

    await asyncio.sleep(0.3)

    try:
        await cleanup_message.delete()
    except TelegramBadRequest:
        pass

    await message.answer(
        text=START_TEXT,
        reply_markup=start_inline_keyboard(),
    )


@router.callback_query(F.data == "start")
async def handle_start_callback(callback: CallbackQuery) -> None:
    message = callback.message

    if not isinstance(message, Message):
        await callback.answer()
        return

    await message.edit_text(
        text=START_TEXT,
        reply_markup=start_inline_keyboard(),
    )

    await callback.answer()