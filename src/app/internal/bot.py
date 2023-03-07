from typing import Tuple

from django.conf import settings
from telegram import Bot
from telegram.ext import CommandHandler, Dispatcher

from .ngrok_parser import parse_public_url
from .transport.bot.handlers import (
    me, 
    set_phone, 
    start,
    get_help
)


def start_webhook_bot():
    """
    This function creates a new instance of Telegram Bot
    and corresponding Dispatcher
    ----------
    :return: new instance of Tlg Bot and Dispatcher
    """
    bot = Bot(settings.TLG_TOKEN)
    dispatcher = Dispatcher(bot, None, workers=2)

    setup_dispatcher_handlers(dispatcher)
    set_bot_webhook(bot)

    return (bot, dispatcher)


def setup_dispatcher_handlers(dispatcher):
    """
    Creates handlers for specified dispatcher.
    Each handler represents a single telegram command.
    ----------
    :param dispatcher: Telegram Bot dispatcher
    """
    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CommandHandler("set_phone", set_phone))
    dispatcher.add_handler(CommandHandler("me", me))
    
    dispatcher.add_handler(CommandHandler("help", get_help))


def set_bot_webhook(bot):
    """
    Sets a webhook to recieve incoming Telegram updates.

    Since we don't have an available IP in global net, we have to
    use Ngrok as a Proxy to recieve HTTPS POST requests from Telegram.
    ----------
    :param bot: Telegram Bot instance
    """
    url = parse_public_url()
    bot.set_webhook(url=f"{url}/api/telegram")
