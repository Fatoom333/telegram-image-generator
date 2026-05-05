from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import help_inline_keyboard


router = Router()


HELP_TEXT = (
    "FAQ и помощь ❓\n\n"
    "1. Как создать изображение?\n"
    "Открой Mini App, введи prompt и нажми кнопку генерации.\n\n"
    "2. Можно ли использовать референсы?\n"
    "Да, можно добавить до 4 изображений-референсов.\n\n"
    "3. Что такое кредиты?\n"
    "Кредиты — внутренняя валюта сервиса. Каждая генерация стоит определённое количество кредитов.\n\n"
    "4. Что делать, если кредиты закончились?\n"
    "Открой раздел пополнения в Mini App. В MVP пополнение может работать вручную через администратора.\n\n"
    "5. Почему генерация может долго выполняться?\n"
    "Изображения создаются через внешние AI-провайдеры. Иногда очередь или сама модель могут отвечать дольше обычного.\n\n"
    "6. Что делать при ошибке генерации?\n"
    "Если ошибка техническая, кредиты должны быть возвращены автоматически."
)


@router.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    await message.answer(
        text=HELP_TEXT,
        reply_markup=help_inline_keyboard(),
    )


@router.callback_query(F.data == "help")
async def handle_help_callback(callback: CallbackQuery) -> None:
    message = callback.message

    if not isinstance(message, Message):
        await callback.answer()
        return

    await message.edit_text(
        text=HELP_TEXT,
        reply_markup=help_inline_keyboard(),
    )

    await callback.answer()