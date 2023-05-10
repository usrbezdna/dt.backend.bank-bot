import logging

from django.conf import settings

from telegram.ext import (
    AIORateLimiter, ApplicationBuilder, 
    CommandHandler, Application
)
    
from .ngrok_parser import parse_ngrok_url

from app.internal.api_v1.users.presentation.bot.handlers import TelegramUserHandlers
from app.internal.api_v1.users.db.repositories import UserRepository
from app.internal.api_v1.users.domain.services import UserService


from app.internal.api_v1.favourites.presentation.bot.handlers import TelegramFavouritesHandlers
from app.internal.api_v1.favourites.db.repositories import FavouriteRepository
from app.internal.api_v1.favourites.domain.services import FavouriteService

from app.internal.api_v1.utils.presentation.bot.handlers import TelegramPaymentHandlers

from app.internal.api_v1.accounts.db.repositories import AccountRepository
from app.internal.api_v1.accounts.domain.services import AccountService

from app.internal.api_v1.cards.db.repositories import CardRepository
from app.internal.api_v1.cards.domain.services import CardService

from app.internal.api_v1.transactions.db.repositories import TransactionRepository
from app.internal.api_v1.transactions.domain.services import TransactionService


logger = logging.getLogger("django.server")


def get_bot_application() -> Application:
    """
    This function creates default
    Telegram Bot Application and sets up
    command handlers.
    :return: Bot Application instance
    """
    application = ApplicationBuilder().\
        token(settings.TLG_TOKEN).\
        rate_limiter(AIORateLimiter()).\
        build()

    setup_application_handlers(application)

    return application


def start_polling_bot():
    """
    Starts a new instanse of Telegram Bot
    Application in polling mode
    """
    application : Application = get_bot_application()

    logger.info("Started")
    application.run_polling()


def start_webhook_bot():
    """
    This function starts a new instance of
    Telegram Bot Application with webhook.
    """
    application : Application = get_bot_application()

    set_bot_webhook(application)


def setup_application_handlers(application : Application):
    """
    Creates command handlers for specified Bot Application.
    Each handler represents a single Telegram command.
    ----------
    :param application: Bot Application instance
    """

    user_repo = UserRepository()
    user_service = UserService(user_repo=user_repo)
    user_handlers = TelegramUserHandlers(user_service=user_service)

    application.add_handler(CommandHandler("start", user_handlers.start))
    application.add_handler(CommandHandler("help", user_handlers.get_help))
    application.add_handler(CommandHandler("me", user_handlers.me))
    application.add_handler(CommandHandler("set_phone", user_handlers.set_phone))
    application.add_handler(CommandHandler("set_password", user_handlers.set_password))


    fav_repo = FavouriteRepository(user_repo=user_repo)
    fav_service = FavouriteService(fav_repo=fav_repo)
    fav_handlers = TelegramFavouritesHandlers(favourite_service=fav_service)

    application.add_handler(CommandHandler("list_fav", fav_handlers.list_fav))
    application.add_handler(CommandHandler("add_fav", fav_handlers.add_fav))
    application.add_handler(CommandHandler("del_fav", fav_handlers.del_fav))
    

    account_repo = AccountRepository()
    account_service = AccountService(account_repo=account_repo)


    card_repo = CardRepository()
    card_service = CardService(card_repo=card_repo)

    
    tx_repo = TransactionRepository()
    tx_service = TransactionService(tx_repo=tx_repo)

    payment_handlers = TelegramPaymentHandlers(
        user_service=user_service,
        fav_service=fav_service,

        account_service=account_service,
        card_service=card_service,

        tx_service=tx_service
    )

    application.add_handler(CommandHandler("check_card", payment_handlers.check_payable))
    application.add_handler(CommandHandler("check_account", payment_handlers.check_payable))

    application.add_handler(CommandHandler("send_to_user", payment_handlers.send_to))
    application.add_handler(CommandHandler("send_to_account", payment_handlers.send_to))
    application.add_handler(CommandHandler("send_to_card", payment_handlers.send_to))


    application.add_handler(CommandHandler("list_inter", payment_handlers.list_inter))

    application.add_handler(CommandHandler("state_card", payment_handlers.state_payable))
    application.add_handler(CommandHandler("state_account", payment_handlers.state_payable))

    

def set_bot_webhook(application : Application):
    """
    Sets a webhook to recieve incoming Telegram updates.
    Tries to use WEBHOOK_URL from .env file.

    If we don't have an available IP in global net, we have to
    use Ngrok as a Proxy to recieve HTTPS POST requests from Telegram.
    ----------
    :param application: Bot Application instance
    """

    url = settings.WEBHOOK_URL
    if not url:
        url = parse_ngrok_url()

    logger.info("Started")
    application.run_webhook(
        listen="0.0.0.0",
        port=settings.WEBHOOK_PORT,
        url_path="webhook",
        webhook_url=f"{url}",
        close_loop=False,
        drop_pending_updates=True,
    )
