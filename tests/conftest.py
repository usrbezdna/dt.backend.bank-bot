import datetime
import json
from unittest.mock import AsyncMock

import pytest
from django.test import AsyncClient, Client
from telegram import Chat, Message, MessageEntity, Update, User
from telegram.ext import ApplicationBuilder

from src.app.internal.api_v1.favourites.db.repositories import FavouriteRepository
from src.app.internal.api_v1.favourites.domain.services import FavouriteService
from src.app.internal.api_v1.favourites.presentation.bot.handlers import TelegramFavouritesHandlers
from src.app.internal.api_v1.payment.accounts.db.repositories import AccountRepository
from src.app.internal.api_v1.payment.accounts.domain.services import AccountService
from src.app.internal.api_v1.payment.cards.db.repositories import CardRepository
from src.app.internal.api_v1.payment.cards.domain.services import CardService
from src.app.internal.api_v1.payment.presentation.bot.handlers import TelegramPaymentHandlers
from src.app.internal.api_v1.payment.transactions.db.repositories import TransactionRepository
from src.app.internal.api_v1.payment.transactions.domain.services import TransactionService
from src.app.internal.api_v1.users.db.repositories import UserRepository
from src.app.internal.api_v1.users.domain.services import UserService
from src.app.internal.api_v1.users.presentation.bot.handlers import TelegramUserHandlers
from src.app.internal.api_v1.utils.s3.db.repositories import S3Repository
from src.app.internal.api_v1.utils.s3.domain.services import S3Service
from src.app.internal.bot import setup_application_handlers
from src.app.models import User as UserModel


@pytest.fixture
def bot_application(mocked_context):
    application = ApplicationBuilder().bot(mocked_context.bot).updater(None).build()

    setup_application_handlers(application)
    return application


@pytest.fixture
def telegram_user_handlers():
    user_repo = UserRepository()

    user_service = UserService(user_repo=user_repo)
    user_handlers = TelegramUserHandlers(user_service=user_service)

    return user_handlers


@pytest.fixture
def telegram_fav_handlers():
    user_repo = UserRepository()
    fav_repo = FavouriteRepository(user_repo=user_repo)

    fav_service = FavouriteService(fav_repo=fav_repo)
    fav_handlers = TelegramFavouritesHandlers(favourite_service=fav_service)

    return fav_handlers


@pytest.fixture
def telegram_payment_handlers():
    user_repo = UserRepository()
    user_service = UserService(user_repo=user_repo)

    fav_repo = FavouriteRepository(user_repo=user_repo)
    fav_service = FavouriteService(fav_repo=fav_repo)

    account_repo = AccountRepository()
    account_service = AccountService(account_repo=account_repo)

    card_repo = CardRepository()
    card_service = CardService(card_repo=card_repo)

    tx_repo = TransactionRepository()
    tx_service = TransactionService(tx_repo=tx_repo)

    s3_repo = S3Repository()
    s3_service = S3Service(s3_repo=s3_repo)

    payment_handlers = TelegramPaymentHandlers(
        user_service=user_service,
        fav_service=fav_service,
        account_service=account_service,
        card_service=card_service,
        tx_service=tx_service,
        s3_service=s3_service,
    )

    return payment_handlers


@pytest.fixture
def already_saved_user(telegram_user):
    user_model = UserModel(
        tlg_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        phone_number="",
    )
    user_model.save()
    return telegram_user


@pytest.fixture
def already_verified_user(already_saved_user):
    user_model = UserModel.objects.get(tlg_id=already_saved_user.id)
    user_model.phone_number = "+12345"
    user_model.save()

    return already_saved_user


@pytest.fixture
def mocked_context():
    mocked_context = AsyncMock()
    mocked_context.bot.username = "testbot"

    return mocked_context


@pytest.fixture
def telegram_user():
    return User(id=123, is_bot=False, first_name="foo", last_name="bar", username="foobar")


@pytest.fixture
def telegram_chat():
    return Chat(id=123, type="private")


@pytest.fixture
def get_update_for_command(get_message_with_text, mocked_context):
    def inner(message_text):
        message = get_message_with_text(message_text)
        custom_update = Update(update_id=123, message=message)

        custom_update._bot = mocked_context.bot
        return custom_update

    return inner


@pytest.fixture
def get_list_with_updates(get_update_for_command):
    def inner(list_with_commands):
        updates_list = []
        for command in list_with_commands:
            updates_list.append(get_update_for_command(command))

        return updates_list

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
            text=message_text,
        )

        custom_message._bot = mocked_context.bot
        return custom_message

    return inner
