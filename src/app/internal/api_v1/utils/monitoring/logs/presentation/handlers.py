import asyncio
import logging
from logging import Handler, LogRecord
from queue import Queue
from threading import Thread

import requests
from requests.exceptions import RequestException

logger = logging.getLogger("stdout")


class TelegramLogsHandler(Handler):
    def __init__(self, logs_bot_token: str, logs_chat_id: str):
        super().__init__()

        self._token = logs_bot_token
        self._chat_id = logs_chat_id

        self._updates_queue = Queue()
        self.start_logs_bot()

    def start_logs_bot(self):
        """
        Starts thread with Telegram logs manager function
        """
        th = Thread(daemon=True, target=self.telegram_logs_manager)
        th.start()

    def telegram_logs_manager(self):
        """
        Recieves logs from queue and sends them to Telegram channel
        """
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"

        while True:
            update = self._updates_queue.get()
            if update:
                params = {"chat_id": self._chat_id, "text": self.format(update)}
                try:
                    requests.get(url, params=params)
                except RequestException:
                    logger.info("Some error occured during sending logs to Telegram!")

    def emit(self, record: LogRecord):
        self._updates_queue.put(record)


class RestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Decied not to add Body and Headers in log message due to their length
        logger.info(
            f"Got new request with METHOD: {request.method} "
            + f"on ENDPOINT: {request.path} from USER: {request.user} "
        )

        response = self.get_response(request)
        return response
