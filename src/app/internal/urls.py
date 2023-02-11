from django.urls import path

from .transport.bot.handlers import TelegramAPIView

# API Calls Go Here 
urlpatterns = [
    path("telegram", TelegramAPIView.as_view(), name="telegram_webhook"),
    # path("me<int:tlg_id>")
]