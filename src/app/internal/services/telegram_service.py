import logging
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

from app.internal.transport.bot.telegram_messages import ME_WITH_NO_USER, NO_VERIFIED_PN

from .user_service import get_user_by_id

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
        user = await get_user_by_id(update.effective_user.id)

        if not user:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=ME_WITH_NO_USER
            )
            return

        if user.hasPhoneNumber():
            await func(update, context)
        else:
            logger.info(f"User with {update.effective_user.id} ID don't have access to this function: {func.__name__}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=NO_VERIFIED_PN)

    return wrapper
