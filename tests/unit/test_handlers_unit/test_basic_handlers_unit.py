import pytest

from src.app.internal.transport.bot.telegram_messages import HELP_MSG
from src.app.internal.transport.bot.handlers import get_help


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_help_handler(mocked_context, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command('/help')

    await get_help(mocked_update, mocked_context)
    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=HELP_MSG
    )