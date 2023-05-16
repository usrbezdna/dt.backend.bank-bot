import logging
from functools import wraps
from typing import Callable
from app.internal.api_v1.users.presentation.bot.telegram_messages import USER_NOT_FOUND_MSG, NO_VERIFIED_PN


from telegram import Update
from telegram.ext import ContextTypes

from app.internal.api_v1.users.db.repositories import UserRepository
from app.internal.api_v1.users.db.exceptions import UserNotFoundException

from asgiref.sync import sync_to_async

logger = logging.getLogger("django.server")



def verified_phone_required(func : Callable):
    """
    This is utility function just for Telegram usage. It restricts access 
    to all other Telegram commands (except /start, /set_phone and /help) 
    unless user has a verified phone number.
    ----------

    :param func: some function that acts like a command handler
    """

    @wraps(func)
    async def wrapper(self_of_wrapped, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user_repo = UserRepository()

        chat_id, user_id = update.effective_chat.id, update.effective_user.id
        try:
            user_phone_number : str = await sync_to_async(user_repo.get_user_field_by_id)(
                tlg_id=update.effective_user.id, field_name="phone_number"
            )

        except UserNotFoundException:
            logger.info(f'User with ID {user_id} was not found in DB')
            await context.bot.send_message(chat_id=chat_id, text=USER_NOT_FOUND_MSG)
        
        if user_phone_number:
            await func(self_of_wrapped, update, context)
        else:
            logger.info(f"User with {user_id} ID don't have access to this function: {func.__name__}")
            await context.bot.send_message(chat_id=chat_id, text=NO_VERIFIED_PN)

    return wrapper
