from unittest.mock import call

import pytest

from src.app.internal.transport.bot.handlers import check_payable
from src.app.internal.transport.bot.telegram_messages import (
    ABSENT_ID_NUMBER,
    BALANCE_NOT_FOUND,
    NOT_VALID_ID_MSG,
    get_message_with_balance,
)
from src.app.models import Account, Card


async def basic_test_for_payable_validations(
    get_list_with_updates, mocked_context, telegram_chat, list_of_commands, expected_error_text
):
    updates_list = get_list_with_updates(list_of_commands)
    for update in updates_list:
        await check_payable(update, mocked_context)

    mock_error_call = call(chat_id=telegram_chat.id, text=expected_error_text)

    assert len(mocked_context.mock_calls) == len(updates_list)
    mocked_context.bot.send_message.assert_has_calls([mock_error_call] * len(updates_list), any_order=True)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_check_payable_with_absent_id(
    mocked_context, already_verified_user, telegram_chat, get_list_with_updates
):
    commands_list = ["/check_card", "/check_account"]

    await basic_test_for_payable_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, ABSENT_ID_NUMBER
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_check_payable_with_invalid_id(
    mocked_context, already_verified_user, telegram_chat, get_list_with_updates
):

    commands_list = [
        "/check_card -5215125",
        "/check_card text",
        "/check_account -45125",
        "/check_account definitely_not_an_id",
    ]

    await basic_test_for_payable_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, NOT_VALID_ID_MSG
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_check_payable_not_found_in_db(
    mocked_context, already_verified_user, telegram_chat, get_list_with_updates
):
    commands_list = ["/check_card 7634344", "/check_account 9783451"]

    await basic_test_for_payable_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, BALANCE_NOT_FOUND
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_check_payable_with_valid_args(
    mocked_context,
    already_verified_user,
    telegram_chat,
    get_update_for_command,
    new_user_with_account_and_card,
):

    _, account_model, card_model = await new_user_with_account_and_card(
        user_tlg_id=101, account_uniq_id=102, card_uniq_id=103, account_value=100
    )

    acc_mocked_update = get_update_for_command(f"/check_account {account_model.uniq_id}")
    await check_payable(acc_mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_with(
        chat_id=telegram_chat.id, text=get_message_with_balance(account_model)
    )

    card_mocked_update = get_update_for_command(f"/check_card {card_model.uniq_id}")
    await check_payable(card_mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_with(
        chat_id=telegram_chat.id, text=get_message_with_balance(account_model)
    )

    assert len(mocked_context.mock_calls) == 2
