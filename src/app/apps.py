from typing import Any, Optional
from django.apps import AppConfig as Config


class AppConfig(Config):
    name = "app"

    def __init__(self, app_name: str, app_module: Optional[Any]) -> None:
        """
        Overrides default __init__ method for app configuration and
        creates 2 additional fields for Telegram Bot and Dispatcher instances
        """
        super().__init__(app_name, app_module)
        self.TLG_BOT, self.TLG_DISPATCHER = None, None
        
    def ready(self) -> None:
        #                            NOTE:
        # In the usual initialization process, the ready method is called only once
        # and just after registry configuration. So, I consider it might be a good 
        # approach to start webhook here.

        from app.internal.bot import start_webhook_bot
        # Setting up Webhook Telegram Bot and Dispatcher
        self.TLG_BOT, self.TLG_DISPATCHER = start_webhook_bot()

default_app_config = "app.AppConfig"