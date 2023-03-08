import asyncio
from typing import Tuple

from django.conf import settings
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, AIORateLimiter 

from .ngrok_parser import parse_public_url
from .transport.bot.handlers import (
    me, 
    set_phone, 
    start,
    get_help
)


def start_webhook_bot():
    """
    This function starts a new instance of 
    Telegram Bot Application with webhook.
    """
    application = ApplicationBuilder().token(settings.TLG_TOKEN).rate_limiter(AIORateLimiter()).build()

    setup_application_handlers(application)
    set_bot_webhook(application)


def setup_application_handlers(application):
    """
    Creates handlers for specified Bot Application.
    Each handler represents a single Telegram command.
    ----------
    :param application: Bot Application instance
    """
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", get_help))

    application.add_handler(CommandHandler("set_phone", set_phone))
    application.add_handler(CommandHandler("me", me))


def set_bot_webhook(application):
    """
    Sets a webhook to recieve incoming Telegram updates.

    Since we don't have an available IP in global net, we have to
    use Ngrok as a Proxy to recieve HTTPS POST requests from Telegram.
    ----------
    :param application: Bot Application instance
    """
    url = parse_public_url()

    print('Ready!')
    application.run_webhook(
            listen='0.0.0.0',
            port=settings.PORT,
            webhook_url=f'{url}',
            close_loop = False,
            drop_pending_updates=True
    )
