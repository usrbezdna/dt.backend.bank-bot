from django.apps import AppConfig as Config


class AppConfig(Config):
    name = "app"


default_app_config = "app.AppConfig"
