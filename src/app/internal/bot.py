import logging

from django.conf import settings
from telegram.ext import AIORateLimiter, ApplicationBuilder, CommandHandler

from .ngrok_parser import parse_ngrok_url
from .transport.bot.handlers import (
    add_fav,
    check_payable,
    del_fav,
    get_help,
    list_fav,
    list_inter,
    me,
    send_to,
    set_password,
    set_phone,
    start,
    state_payable,
)

logger = logging.getLogger("django.server")


def get_bot_application():
    """
    This function creates default
    Telegram Bot Application and sets up
    command handlers.
    :return: Bot Application instance
    """
    application = ApplicationBuilder().token(settings.TLG_TOKEN).rate_limiter(AIORateLimiter()).build()

    setup_application_handlers(application)

    return application


def start_polling_bot():
    """
    Starts a new instanse of Telegram Bot
    Application in polling mode
    """
    application = get_bot_application()
    logger.info("Started")
    application.run_polling()


def start_webhook_bot():
    """
    This function starts a new instance of
    Telegram Bot Application with webhook.
    """
    application = get_bot_application()

    set_bot_webhook(application)


def setup_application_handlers(application):
    """
    Creates command handlers for specified Bot Application.
    Each handler represents a single Telegram command.
    ----------
    :param application: Bot Application instance
    """
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", get_help))
    application.add_handler(CommandHandler("set_phone", set_phone))
    application.add_handler(CommandHandler("me", me))

    application.add_handler(CommandHandler("list_fav", list_fav))
    application.add_handler(CommandHandler("add_fav", add_fav))
    application.add_handler(CommandHandler("del_fav", del_fav))

    application.add_handler(CommandHandler("check_card", check_payable))
    application.add_handler(CommandHandler("check_account", check_payable))

    application.add_handler(CommandHandler("send_to_user", send_to))
    application.add_handler(CommandHandler("send_to_account", send_to))
    application.add_handler(CommandHandler("send_to_card", send_to))

    application.add_handler(CommandHandler("list_inter", list_inter))

    application.add_handler(CommandHandler("state_card", state_payable))
    application.add_handler(CommandHandler("state_account", state_payable))

    application.add_handler(CommandHandler("set_password", set_password))


def set_bot_webhook(application):
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
