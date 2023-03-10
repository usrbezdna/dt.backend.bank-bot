import logging

from django.core.management.base import BaseCommand

from app.internal.bot import start_webhook_bot

logger = logging.getLogger("django.server")


class Command(BaseCommand):
    help = "Starts Telegram Bot Application with webhook"

    def handle(self, *args, **options):
        logger.info("Starting...")
        start_webhook_bot()
