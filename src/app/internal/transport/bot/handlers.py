import logging
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction

from telegram import Update
from telegram.ext import (
    CallbackContext
)
from app.internal.models.user import User

import json


logger = logging.getLogger('django.server') 

class TelegramAPIView(APIView):
    """
    View for incoming Telegram updates received through webhook. 
    """
    def post(self, request):
        logger.info('Got new POST request from Telegram')
        process_request(request)
        return Response()


def process_request(request) -> None:
    """
    Function for processing requests.
    Actually it receives them and sends to Dispacther.
    ----------
    :param request: request from Telegram user
    """
    from django.apps import apps
    
    config_ = apps.get_app_config('app')

    data = json.loads(request.body.decode())
    update = Update.de_json(data, config_.TLG_BOT)
    config_.TLG_DISPATCHER.process_update(update)

@transaction.atomic
def start(update: Update, context: CallbackContext) -> None:
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
        last_name=user_data.last_name if user_data.last_name else '',
        phone_number=''
    )

    tlg_user.save()
    logger.info(f'User {user_data.username} was successfully saved to DB')

    update.message.reply_text(f'Hi {user_data.username}!\n'
    'Thanks for choosing this Banking Bot. He doesn\'t have '
    'much functions just yet, but this will be changed in '
    'future updates')