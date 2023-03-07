import json
import logging

from django.db import transaction
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.models.user import User
from app.internal.services.user_service import (
    get_user_from_db,
    save_user_to_db,
    update_user_phone_number
)

from app.internal.services.telegram_service import (
    verified_phone_required
)

from .telegram_messages import (
    HELP_MSG,
    ABSENT_PN_MSG,
    INVALID_PN_MSG,
    NOT_INT_FORMAT_MSG,
    get_success_phone_msg,
    get_unique_start_msg,
)

logger = logging.getLogger("django.server")


class TelegramAPIView(APIView):
    """
    View for incoming Telegram updates received through webhook.
    """

    def post(self, request):
        logger.info("Got new POST request from Telegram")
        process_request(request)
        return Response()


def process_request(request):
    """
    Function for processing requests.
    Actually it receives them and sends to Dispacther.
    ----------
    :param request: request from Telegram user
    """
    from django.apps import apps

    config_ = apps.get_app_config("app")

    data = json.loads(request.body.decode())
    update = Update.de_json(data, config_.TLG_BOT)
    config_.TLG_DISPATCHER.process_update(update)


def start(update, context):
    """
    Handler for /start command.
    (Handlers usually take 2 arguments: update and context).
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback

    """
    user_data = update.effective_user

    tlg_user = User(
        tlg_id=user_data.id,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name if user_data.last_name else "",
        phone_number="",
    )

    save_user_to_db(tlg_user)
    update.message.reply_text(get_unique_start_msg(user_data.username))


def get_help(update, context):
    """
    Handler for /help command.
    Returns some info about currently supported commands.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    update.message.reply_text(HELP_MSG)


def set_phone(update, context):
    """
    Handler for /set_phone command.
    Supports phone validation and user existence checking.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    user_data = update.effective_user
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:
        user_from_db = get_user_from_db(user_data.id)
        phone_number = command_data[1]

        if phone_number.startswith("+"):
            try:
                parsed_number = PhoneNumber.from_string(phone_number)

                update_user_phone_number(user_from_db, parsed_number)
                update.message.reply_text(get_success_phone_msg(parsed_number))

            except NumberParseException:
                logger.info("User did not provide a valid phone number")
                update.message.reply_text(INVALID_PN_MSG)

            finally:
                return

        update.message.reply_text(NOT_INT_FORMAT_MSG)
        return
    update.message.reply_text(ABSENT_PN_MSG)


@verified_phone_required
def me(update, context):
    """
    Hander for /me command.
    Returns full information about Telegram user.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    user_id = update.effective_user.id
    user_from_db = get_user_from_db(user_id)

    update.message.reply_text("Here is some info about you:\n\n" f"{str(user_from_db)}")
