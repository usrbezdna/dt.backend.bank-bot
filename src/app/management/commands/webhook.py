from django.core.management.base import BaseCommand

from app.internal.bot import start_webhook_bot


class Command(BaseCommand):
    help = "Starts Telegram Bot Application with webhook"

    def handle(self, *args, **options):
        self.stdout.write("Starting...")
        start_webhook_bot()
