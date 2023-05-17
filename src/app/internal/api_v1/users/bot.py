from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .db.repositories import UserRepository
from .domain.services import UserService
from .presentation.bot.handlers import TelegramUserHandlers


def register_telegram_user_handlers(application: Application) -> None:
    """
    Registers handlers for user part of Telegram bot
    """

    user_repo = UserRepository()
    user_service = UserService(user_repo=user_repo)
    user_handlers = TelegramUserHandlers(user_service=user_service)

    application.add_handler(CommandHandler("start", user_handlers.start))

    application.add_handler(
        MessageHandler(filters.Regex(r'help') | filters.CaptionRegex("help"), user_handlers.get_help))

    application.add_handler(CommandHandler("me", user_handlers.me))

    application.add_handler(CommandHandler("set_phone", user_handlers.set_phone))
    application.add_handler(CommandHandler("set_password", user_handlers.set_password))
