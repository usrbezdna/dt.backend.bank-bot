from unittest.mock import AsyncMock, Mock
import pytest
from src.app.internal.transport.bot.telegram_messages import (
    HELP_MSG, get_unique_start_msg
)

from src.app.models import User
from src.app.internal.transport.bot.handlers import (
    start, me, get_help, set_phone
)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db
async def test_start_handler(mocked_context, telegram_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command('/start')

    await start(mocked_update, mocked_context)

    await User.objects.filter(tlg_id=telegram_user.id).afirst()
    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_unique_start_msg(telegram_user.first_name)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db
async def test_me_handler(saved_user):
    
    await saved_user
    await User.objects.all().acount() == 1


def test_set_phone_handler():
    pass