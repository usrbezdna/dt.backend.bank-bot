from django.conf import settings

from .ngrok_parser import parse_public_url

from .transport.bot.handlers import start, set_phone, me

from telegram import Bot
from typing import Tuple

from telegram.ext import (Dispatcher, CommandHandler)



def start_webhook_bot() -> Tuple[Bot, Dispatcher]:
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

def setup_dispatcher_handlers(dispatcher : Dispatcher) -> None:
    """
    Creates handlers for specified dispatcher. 
    Each handler represents a single telegram command.
    ----------
    :param dispatcher: Telegram Bot dispatcher 
    """
    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(CommandHandler('set_phone', set_phone))
    dispatcher.add_handler(CommandHandler('me', me))

def set_bot_webhook(bot : Bot) -> None:
    """
    Sets a webhook to recieve incoming Telegram updates.

    Since we don't have an available IP in global net, we have to
    use Ngrok as a Proxy to recieve HTTPS POST requests from Telegram.
    ----------
    :param bot: Telegram Bot instance
    """
    url = parse_public_url()
    bot.set_webhook(url=f"{url}/api/telegram")
