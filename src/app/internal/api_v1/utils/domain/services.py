import logging
from functools import wraps

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.api_v1.users.db.repositories import UserRepository
from app.internal.api_v1.users.domain.services import UserService
from app.internal.api_v1.utils.presentation.bot.telegram_messages import NO_VERIFIED_PN

logger = logging.getLogger("django.server")


def verified_phone_required(func):
    """
    This decorator function restricts access to all other Telegram commands
    (except /start, /set_phone and /help) unless user has a verified phone number.
    ----------
    :param func: some function that acts like a command handler
    """

    user_repo = UserRepository()

    @wraps(func)
    async def wrapper(_self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_phone_number = await sync_to_async(user_repo.get_user_field_by_id)(
            tlg_id=update.effective_user.id, field_name="phone_number"
        )

        if user_phone_number:
            await func(_self, update, context)
        else:
            logger.info(f"User with {update.effective_user.id} ID don't have access to this function: {func.__name__}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=NO_VERIFIED_PN)

    return wrapper
