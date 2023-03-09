import logging
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

from .user_service import get_user_from_db

logger = logging.getLogger("django.server")


def verified_phone_required(func):
    """
    This decorator function restricts access to all other Telegram commands
    (except /start, /set_phone and /help) unless user has a verified phone number.
    ----------
    :param func: some function that acts like a command handler
    """

    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext):
        user = await get_user_from_db(update.effective_user.id)

        if not user:
            logger.info(f"User {update.effective_user.username} not found in DB")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text='Type /start at first and verify you phone number'
            )

        if user.hasPhoneNumber():
            await func(update, context)
        else:
            logger.info(f"User {update.effective_user.username} don't have access to this function: {func.__name__}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="You don't have a verified phone number!"
            )

    return wrapper
