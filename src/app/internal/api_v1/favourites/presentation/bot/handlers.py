import logging
from typing import Any, List, Optional

from telegram import Update
from telegram.ext import ContextTypes

from app.internal.api_v1.favourites.db.exceptions import (
    FavouriteNotFoundException,
    InvalidIDArgumentException,
    SecondTimeAdditionException,
    UserNotInFavouritesException,
)
from app.internal.api_v1.favourites.domain.services import FavouriteService
from app.internal.api_v1.favourites.presentation.bot.telegram_messages import (
    ABSENT_ARG_FAV_MSG,
    ABSENT_FAV_MSG,
    ABSENT_FAV_USER,
    NOT_VALID_ID_MSG,
    RESTRICT_SECOND_TIME_ADD,
    RESTRICT_SELF_OPS,
    USER_NOT_IN_FAV,
    get_result_message_for_user_favourites,
    get_success_msg_for_deleted_fav,
    get_success_msg_for_new_fav,
)
from app.internal.api_v1.users.db.exceptions import UserNotFoundException
from app.internal.api_v1.users.db.models import User
from app.internal.api_v1.utils.domain.services import verified_phone_required

logger = logging.getLogger("django.server")


class TelegramFavouritesHandlers:
    def __init__(self, favourite_service: FavouriteService):
        self._favourite_service = favourite_service

    @verified_phone_required
    async def list_fav(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /list_fav command.
        Returns list of favourites users with max length 5
        or error message if user don't have any favs.
        ----------
        :param update: recieved Update object
        :param context: context object passed to the callback
        """

        favs_limit = 5
        user_id, chat_id = update.effective_user.id, update.effective_chat.id

        try:
            favs_list: List[User] = await self._favourite_service.get_limited_list_of_favourites(
                tlg_id=user_id, favs_limit=favs_limit
            )

        except FavouriteNotFoundException:
            logger.info(f"Unable to find favourites for user with ID: {user_id}")
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_FAV_MSG)

            return

        if len(favs_list) == 0:
            logger.info("User has a favorite object, but don't have any favourites users included")
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_FAV_MSG)

            return

        res_msg = get_result_message_for_user_favourites(favs_list)
        await context.bot.send_message(chat_id=chat_id, text=res_msg)

    @verified_phone_required
    async def del_fav(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /del_fav command.
        Deletes Telegram user from specified favourites.
        ----------
        :param update: recieved Update object
        :param context: context object
        """
        user_id, chat_id = update.effective_user.id, update.effective_chat.id
        command_data = update.message.text.split(" ")

        if len(command_data) != 2:
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_ARG_FAV_MSG)
            return

        another_user = await self.try_get_another_user(
            update=update, context=context, chat_id=chat_id, user_id=user_id, argument=command_data[1]
        )

        if another_user is None:
            return

        try:
            await self._favourite_service.try_del_fav_from_user(user_id, another_user)

        except UserNotInFavouritesException:
            await context.bot.send_message(chat_id=chat_id, text=USER_NOT_IN_FAV)
            return

        await context.bot.send_message(chat_id=chat_id, text=get_success_msg_for_deleted_fav(another_user))

    @verified_phone_required
    async def add_fav(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /add_fav command.
        Adds another Telegram user to the list of favourites.
        Accepts Telegram ID or username.
        ----------
        :param update: recieved Update object
        :param context: context object passed to the callback
        """
        user_id, chat_id = update.effective_user.id, update.effective_chat.id
        command_data = update.message.text.split(" ")

        if len(command_data) != 2:
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_ARG_FAV_MSG)
            return

        another_user = await self.try_get_another_user(
            update=update, context=context, chat_id=chat_id, user_id=user_id, argument=command_data[1]
        )

        if another_user is None:
            return

        try:
            await self._favourite_service.try_add_fav_to_user(user_id, another_user)

        except SecondTimeAdditionException:
            await context.bot.send_message(chat_id=chat_id, text=RESTRICT_SECOND_TIME_ADD)
            return

        await context.bot.send_message(chat_id=chat_id, text=get_success_msg_for_new_fav(another_user))

    async def try_get_another_user(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, argument: Any
    ) -> Optional[User]:
        """
        This function acts like a sublogic handler. It sends request to internal
        service and tries to get another_user User object.

        If request wasn't successful, this handler responds to Telegram User
        with error reason message.
        ----------

        :param update: recieved Update object
        :param context: context object passed to the callback

        :param chat_id: Telegram chat ID
        :param user_id: Telegram ID of user (favs owner)
        :param argument: Telegram ID or Username of another Telegram User

        :returns: User object or None

        """
        try:
            another_user: User = await self._favourite_service.get_another_user(argument)

        except InvalidIDArgumentException:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return None

        except UserNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_FAV_USER)
            return None

        if another_user.tlg_id == user_id:
            await context.bot.send_message(chat_id=chat_id, text=RESTRICT_SELF_OPS)
            return None

        return another_user
