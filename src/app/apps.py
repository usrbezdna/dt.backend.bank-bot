from django.apps import AppConfig as Config


class AppConfig(Config):
    name = "app"

    TLG_BOT = None
    TLG_DISPATCHER = None

    def ready(self) -> None:
        global TLG_BOT 
        global TLG_DISPATCHER
        #                            NOTE:
        # In the usual initialization process, the ready method is called only once
        # and just after registry configuration. So, I consider it might be a good 
        # approach to start webhook here.
        from app.internal.bot import start_webhook_bot

        # Setting up Webhook Telegram Bot and Dispatcher
        TLG_BOT, TLG_DISPATCHER = start_webhook_bot()


default_app_config = "app.AppConfig"