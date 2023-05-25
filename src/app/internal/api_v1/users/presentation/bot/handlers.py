import logging
from io import BytesIO

import boto3
from botocore.client import Config
from django.conf import settings
from django.core.files.images import ImageFile
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import is_valid_number
from phonenumbers.phonenumberutil import NumberParseException
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.api_v1.users.db.exceptions import UserNotFoundException
from app.internal.api_v1.users.domain.entities import UserSchema
from app.internal.api_v1.users.domain.services import UserService
from app.internal.api_v1.users.presentation.bot.telegram_messages import (
    ABSENT_PASSWORD_MSG,
    ABSENT_PN_MSG,
    HELP_MSG,
    INVALID_PN_MSG,
    NOT_INT_FORMAT_MSG,
    PASSWORD_UPDATED,
    USER_NOT_FOUND_MSG,
    get_info_for_me_handler,
    get_success_phone_msg,
    get_unique_start_msg,
)
from app.internal.api_v1.utils.s3.db.models import RemoteImage
from app.internal.api_v1.utils.s3.db.repositories import S3Repository
from app.internal.api_v1.utils.s3.domain.services import S3Service
from app.internal.api_v1.utils.telegram.domain.services import verified_phone_required

logger = logging.getLogger("django_stdout")


class TelegramUserHandlers:
    def __init__(self, user_service: UserService):
        self._user_service = user_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /start command.
        (Handlers usually take 2 arguments: update and context).
        ----------

        :param update: recieved Update object
        :param context: context object passed to the callback
        """
        telegram_user, chat_id = update.effective_user, update.effective_chat.id

        await self._user_service.asave_telegram_user_to_db(tlg_user=telegram_user)
        await context.bot.send_message(chat_id=chat_id, text=get_unique_start_msg(telegram_user.first_name))

    async def get_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /help command.
        Returns some info about currently supported commands.
        ----------

        :param update: recieved Update object
        :param context: context object passed to the callback
        """
        await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MSG)

    async def set_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /set_phone command.
        Supports phone validation and user existence checking.
        ----------
        :param update: recieved Update object
        :param context: context object passed to the callback
        """
        chat_id = update.effective_chat.id
        command_data = update.message.text.split(" ")

        if len(command_data) != 2:
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_PN_MSG)
            return

        phone_number = command_data[1]
        if not phone_number.startswith("+"):
            await context.bot.send_message(chat_id=chat_id, text=NOT_INT_FORMAT_MSG)
            return

        try:
            parsed_number = PhoneNumber.from_string(phone_number)

        except NumberParseException:
            logger.info("User did not provide a valid phone number and it caused ParseError")
            await context.bot.send_message(chat_id=chat_id, text=INVALID_PN_MSG)
            return

        if not is_valid_number(parsed_number):
            logger.info("Provided number was parsed, but is not valid anyway")
            await context.bot.send_message(chat_id=chat_id, text=INVALID_PN_MSG)
            return

        await self._user_service.aupdate_user_phone_number(
            tlg_id=update.effective_user.id, new_phone_number=parsed_number
        )
        await context.bot.send_message(chat_id=chat_id, text=get_success_phone_msg(parsed_number))

    @verified_phone_required
    async def me(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Hander for /me command.
        Returns full information about Telegram user.
        ----------

        :param update: recieved Update object
        :param context: context object passed to the callback
        """
        user_id, chat_id = update.effective_user.id, update.effective_chat.id

        try:
            user_from_db: UserSchema = await self._user_service.aget_user_by_id(tlg_id=user_id)

        except UserNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=USER_NOT_FOUND_MSG)
            return

        await context.bot.send_message(chat_id=chat_id, text=get_info_for_me_handler(user_from_db))

    @verified_phone_required
    async def set_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /set_password
        Allows user to set password.
        ----------
        :param update: recieved Update object
        :param context: context object
        """

        user_id, chat_id = update.effective_user.id, update.effective_chat.id
        command_data = update.message.text.split(" ")

        if len(command_data) != 2:
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_PASSWORD_MSG)
            return

        argument = command_data[1]

        await self._user_service.aupdate_user_password(tlg_id=user_id, new_password=argument)
        await context.bot.send_message(chat_id=chat_id, text=PASSWORD_UPDATED)
