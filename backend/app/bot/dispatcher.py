from aiogram import Dispatcher

from app.bot.handlers import help as help_handler
from app.bot.handlers import start as start_handler


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(start_handler.router)
    dispatcher.include_router(help_handler.router)
    return dispatcher