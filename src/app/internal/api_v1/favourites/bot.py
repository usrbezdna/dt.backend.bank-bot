from telegram.ext import Application, CommandHandler

from app.internal.api_v1.favourites.db.repositories import FavouriteRepository
from app.internal.api_v1.favourites.domain.services import FavouriteService
from app.internal.api_v1.favourites.presentation.bot.handlers import TelegramFavouritesHandlers
from app.internal.api_v1.users.db.repositories import UserRepository


def register_telegram_favourite_handlers(application: Application) -> None:
    """
    Registers handlers for favs part of Telegram bot
    """

    user_repo = UserRepository()

    fav_repo = FavouriteRepository(user_repo=user_repo)
    fav_service = FavouriteService(fav_repo=fav_repo)

    fav_handlers = TelegramFavouritesHandlers(favourite_service=fav_service)

    application.add_handler(CommandHandler("list_fav", fav_handlers.list_fav))
    application.add_handler(CommandHandler("add_fav", fav_handlers.add_fav))
    application.add_handler(CommandHandler("del_fav", fav_handlers.del_fav))
