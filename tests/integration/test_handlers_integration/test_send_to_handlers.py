from unittest.mock import call

import pytest

from src.app.internal.transport.bot.handlers import send_to
from src.app.internal.transport.bot.telegram_messages import (
    INCR_TX_VALUE,
    RSP_NOT_FOUND,
    RSP_USER_WITH_NO_ACC,
    RSP_USER_WITH_NO_CARDS,
    SENDER_RESTRICTION,
    get_message_for_send_command,
)
from src.app.models import Account, Card, User


async def basic_test_for_send_to_validations(
    get_list_with_updates, mocked_context, telegram_chat, list_of_commands, expected_error_text
):
    updates_list = get_list_with_updates(list_of_commands)
    for update in updates_list:
        await send_to(update, mocked_context)

    mocked_context.bot.send_message.assert_called_with(chat_id=telegram_chat.id, text=expected_error_text)

    assert len(mocked_context.mock_calls) == len(updates_list)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_without_requered_args(
    mocked_context, already_verified_user, telegram_chat, get_update_for_command
):
    commands_list = ["/send_to_user", "/send_to_account", "/send_to_card"]

    for command_name in commands_list:
        mocked_update = get_update_for_command(command_name)
        await send_to(mocked_update, mocked_context)

        mocked_context.bot.send_message.assert_called_with(
            chat_id=telegram_chat.id, text=get_message_for_send_command(command_name)
        )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_with_invalid_value(mocked_context, already_verified_user, telegram_chat, get_list_with_updates):

    commands_list = [
        "/send_to_user @FooUser -521",
        "/send_to_user @Username text",
        "/send_to_account 5125 -7643",
        "/send_to_account 512425 newtext",
        "/send_to_card 946 -125",
        "/send_to_card 4687 moretext",
    ]

    await basic_test_for_send_to_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, INCR_TX_VALUE
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_with_no_sender_bank_requisites(
    mocked_context, already_verified_user, telegram_chat, get_list_with_updates
):

    commands_list = [
        "/send_to_user @BarUser 100",
        "/send_to_user @User 4512",
        "/send_to_account 4125 500",
        "/send_to_account 512425 600",
        "/send_to_card 946 450",
        "/send_to_card 4687 320",
    ]

    await basic_test_for_send_to_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, SENDER_RESTRICTION
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_user_with_db_miss_on_recipient(
    mocked_context,
    sender_with_bank_requisites,
    telegram_chat,
    get_update_for_command,
):

    mocked_update = get_update_for_command("/send_to_user 4215124 300")
    await send_to(mocked_update, mocked_context)

    print(mocked_context.mock_calls)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=RSP_NOT_FOUND)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_user_with_recipient_no_account(
    mocked_context, sender_with_bank_requisites, telegram_chat, get_update_for_command, user_model_without_verified_pn
):
    new_user_model = user_model_without_verified_pn(tlg_id=567)
    await new_user_model.asave()

    mocked_update = get_update_for_command(f"/send_to_user {new_user_model.tlg_id} 300")
    await send_to(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=RSP_USER_WITH_NO_ACC)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_user_with_recipient_no_cards(
    mocked_context, sender_with_bank_requisites, telegram_chat, get_update_for_command, new_user_with_account
):

    new_user_model, new_account_model = await new_user_with_account(
        user_tlg_id=567, account_uniq_id=600, account_value=500
    )

    mocked_update = get_update_for_command(f"/send_to_user {new_user_model.tlg_id} 300")
    await send_to(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=RSP_USER_WITH_NO_CARDS)
