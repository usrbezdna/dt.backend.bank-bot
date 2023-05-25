
import asyncio
from logging import Handler, LogRecord
from queue import Queue
from threading import Thread

from telegram import Bot


class TelegramLogsHandler(Handler):

    def __init__(self, logs_bot_token: str, logs_chat_id: str):
        super().__init__()
        self._token = logs_bot_token
        self._chat_id = logs_chat_id

        self._logs_bot = None
        self._updates_queue = Queue()
        self._event_loop = asyncio.get_event_loop()

        self.create_bot()

    def create_bot(self):
        th = Thread(daemon=True, target=self.telegram_logs_manager)
        th.start()

    def telegram_logs_manager(self):
        self._logs_bot = Bot(token=self._token)

        while True:
            update = self._updates_queue.get()
            if update:
                asyncio.run_coroutine_threadsafe(
                    coro=self._logs_bot.send_message(
                        chat_id=self._chat_id,
                        text=self.format(update)
                    ),
                    loop=self._event_loop
                )

    def emit(self, record: LogRecord):
        self._updates_queue.put(record)
