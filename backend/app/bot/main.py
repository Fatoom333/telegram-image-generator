import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers import help as help_handler
from app.bot.handlers import start as start_handler
from app.core.config import settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()

    dispatcher.include_router(start_handler.router)
    dispatcher.include_router(help_handler.router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
