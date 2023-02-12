import logging
from functools import wraps
from typing import Optional

from telegram import Update
from telegram.ext import CallbackContext

from app.models import User

logger = logging.getLogger("django.server")


def get_user_from_db(tlg_id: int) -> Optional[User]:
    """
    Returns Telegram user from Database or None
    (if this user doesn't exist)
    ----------
    :param tlg_id: Telegram user ID
    :return: Telegram User | None
    """
    user_option = User.objects.filter(tlg_id=tlg_id)
    if user_option.exists():
        return user_option[0]
    return None


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
