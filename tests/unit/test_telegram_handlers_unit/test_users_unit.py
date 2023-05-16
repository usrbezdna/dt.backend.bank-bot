from unittest.mock import call

import pytest

from src.app.internal.api_v1.users.presentation.bot.telegram_messages import (
    ABSENT_PN_MSG,
    HELP_MSG,
    INVALID_PN_MSG,
    NOT_INT_FORMAT_MSG,
)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.valid_case
async def test_get_help_handler(telegram_user_handlers, mocked_context, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/help")

    await telegram_user_handlers.get_help(mocked_update, mocked_context)
    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=HELP_MSG)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.error_case
async def test_set_phone_with_no_phone_number(
    telegram_user_handlers, mocked_context, telegram_chat, get_update_for_command
):
    mocked_update = get_update_for_command("/set_phone")
    await telegram_user_handlers.set_phone(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=ABSENT_PN_MSG)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.error_case
async def test_set_phone_with_incorrect_format(
    telegram_user_handlers, mocked_context, telegram_chat, get_update_for_command
):
    mocked_update = get_update_for_command("/set_phone 51526361")

    await telegram_user_handlers.set_phone(mocked_update, mocked_context)
    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=NOT_INT_FORMAT_MSG)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.error_case
async def test_set_phone_with_invalid_pn(telegram_user_handlers, mocked_context, telegram_chat, get_list_with_updates):
    commands_list = [
        "/set_phone +1234567891011121314",
        "/set_phone +1",
        "/set_phone +somerandomtext",
        "/set_phone ++asdfd",
        "/set_phone +7963671674785142",
    ]

    updates_list = get_list_with_updates(commands_list)
    for update in updates_list:
        await telegram_user_handlers.set_phone(update, mocked_context)

    mock_error_call = call(chat_id=telegram_chat.id, text=INVALID_PN_MSG)

    assert len(mocked_context.mock_calls) == len(updates_list)
    mocked_context.bot.send_message.assert_has_calls([mock_error_call] * len(updates_list), any_order=True)
