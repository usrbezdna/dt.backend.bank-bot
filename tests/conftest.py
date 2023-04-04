import datetime
import pytest 

from unittest.mock import AsyncMock
from telegram import Chat, Message, Update, User, MessageEntity
from telegram.ext import ApplicationBuilder

from src.app.internal.bot import setup_application_handlers

@pytest.fixture
def bot_application(mocked_context):

    application = ApplicationBuilder().\
        bot(mocked_context.bot).\
        updater(None).\
        build()
    
    setup_application_handlers(application)
    return application


@pytest.fixture
def mocked_context():

    mocked_context = AsyncMock()
    mocked_context.bot.username = 'testbot'

    return mocked_context


@pytest.fixture
def telegram_user():
    return User(
        id=123, 
        is_bot=False,
        first_name='foo', 
        last_name='bar', 
        username='foobar'
    )

@pytest.fixture
def telegram_chat():
    return Chat(
        id=123, 
        type='private'
    )


@pytest.fixture
def get_update_for_command(get_message_with_text, mocked_context):
    def inner(message_text):

        message = get_message_with_text(message_text)
        custom_update = Update(
            update_id=123,
            message=message
        )

        custom_update._bot = mocked_context.bot
        return custom_update
    return inner


@pytest.fixture
def get_message_with_text(telegram_user, telegram_chat, mocked_context):
    def inner(message_text):

        custom_message = Message(
            message_id=123,
            date=datetime.datetime.now(),
            from_user=telegram_user,
            chat=telegram_chat,
            entities=(MessageEntity(length=len(message_text), offset=0, type=MessageEntity.BOT_COMMAND),),
            text=message_text
        )

        custom_message._bot = mocked_context.bot
        return custom_message
    return inner


