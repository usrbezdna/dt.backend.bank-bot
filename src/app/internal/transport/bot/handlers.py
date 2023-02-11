from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView

from telegram import Update
from django.conf import settings

from telegram.ext import (
    CallbackContext
)

from django.views.decorators.csrf import csrf_exempt

import json

class TelegramAPIView(APIView):
    def post(self, request):
        match_and_process(request)
        return Response()

@csrf_exempt
def match_and_process(request):
    
    data = json.loads(request.body.decode())
    update = Update.de_json(data, settings.TLG_BOT)
    settings.TLG_DISPATCHER.process_update(update)


def start(update: Update, context: CallbackContext):
    text = 'Welcome!'
    update.message.reply_text(text=text)