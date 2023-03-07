from functools import wraps
import logging

from telegram import Update
from telegram.ext import CallbackContext
from .user_service import get_user_from_db


logger = logging.getLogger("django.server")

def verified_phone_required(func):
    """
    This decorator function restricts access to all other Telegram commands
    (except /start and /set_phone) unless user has a verified phone number.
    ----------
    :param func: some function that acts like a command handler
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        if get_user_from_db(update.effective_user.id).hasPhoneNumber():
            func(update, context)
        else:
            logger.info(f"User {update.effective_user.username} don't have access to this function: {func.__name__}")
            update.message.reply_text("You don't have a verified phone number!")

    return wrapper