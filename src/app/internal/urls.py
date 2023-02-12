from django.urls import path

from .transport.bot.handlers import TelegramAPIView
from .transport.rest.handlers import WebAPIView  

# API Calls Go Here 
urlpatterns = [
    path("telegram", TelegramAPIView.as_view(), name="telegram_webhook"),
    path("me/<int:tlg_id>/", WebAPIView.as_view(), name="web_api")
]