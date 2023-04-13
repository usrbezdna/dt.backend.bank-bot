import pytest
from django.db import DatabaseError

from src.app.internal.transport.bot.handlers import send_to
from src.app.internal.transport.bot.telegram_messages import (
    CARD_NOT_FOUND,
    ERROR_DURING_TRANSFER,
    INCR_TX_VALUE,
    INSUF_BALANCE,
    NOT_VALID_ID_MSG,
    RSP_NOT_FOUND,
    RSP_USER_WITH_NO_ACC,
    RSP_USER_WITH_NO_CARDS,
    SELF_TRANSFER_ERROR,
    SENDER_RESTRICTION,
    get_message_for_send_command,
    get_successful_transfer_message,
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
async def test_send_to_with_recipient_no_cards(
    mocked_context, sender_with_bank_requisites, new_user_with_account, get_list_with_updates, telegram_chat
):
    new_user_model, new_account_model = await new_user_with_account(
        user_tlg_id=567, account_uniq_id=600, account_value=500
    )

    commands_list = [f"/send_to_user {new_user_model.tlg_id} 300", f"/send_to_account {new_account_model.uniq_id} 300"]

    await basic_test_for_send_to_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, RSP_USER_WITH_NO_CARDS
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_with_invalid_id(mocked_context, sender_with_bank_requisites, telegram_chat, get_list_with_updates):
    commands_list = [
        "/send_to_user -51251 300",
        "/send_to_user textinseadofid 500",
        "/send_to_account -5432 200",
        "/send_to_account 5safasf 340",
        "/send_to_card -7473 400",
        "/send_to_card t36gab 800",
    ]

    await basic_test_for_send_to_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, NOT_VALID_ID_MSG
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
async def test_send_to_card_with_db_miss_on_card(
    mocked_context,
    sender_with_bank_requisites,
    telegram_chat,
    get_update_for_command,
):
    mocked_update = get_update_for_command("/send_to_card 123456789 300")
    await send_to(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=CARD_NOT_FOUND)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_with_self_transfer_restriction(
    mocked_context,
    sender_with_bank_requisites,
    telegram_chat,
    get_list_with_updates,
):
    sender_account_model = await Account.objects.filter(uniq_id=123).afirst()
    sender_card_model = await Card.objects.filter(uniq_id=1234).afirst()

    sender_account_model.value += 1000
    await sender_account_model.asave()

    commands_list = [
        f"/send_to_user {sender_with_bank_requisites.id} 200",
        f"/send_to_account {sender_account_model.uniq_id} 300",
        f"/send_to_card {sender_card_model.uniq_id} 400",
    ]

    await basic_test_for_send_to_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, SELF_TRANSFER_ERROR
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_with_insufficient_balance(
    mocked_context, sender_with_bank_requisites, telegram_chat, get_list_with_updates, new_user_with_account_and_card
):
    rcp_user_model, rcp_account_model, rcp_card_model = await new_user_with_account_and_card(
        user_tlg_id=987, account_uniq_id=567, card_uniq_id=5678, account_value=1000
    )

    send_account_model = await Account.objects.filter(uniq_id=123).afirst()
    assert send_account_model.value == 0

    commands_list = [
        f"/send_to_user {rcp_user_model.tlg_id} 800",
        f"/send_to_account {rcp_account_model.uniq_id} 860",
        f"/send_to_card {rcp_card_model.uniq_id} 420",
    ]

    await basic_test_for_send_to_validations(
        get_list_with_updates, mocked_context, telegram_chat, commands_list, INSUF_BALANCE
    )


@pytest.mark.asyncio
@pytest.mark.current
@pytest.mark.django_db(transaction=True)
async def test_send_to_with_error_during_transfer(
    mocked_context,
    sender_with_bank_requisites,
    telegram_chat,
    mocker,
    get_update_for_command,
    new_user_with_account_and_card,
):
    sender_account_model = await Account.objects.filter(uniq_id=123).afirst()
    sender_account_model.value += 1000
    await sender_account_model.asave()

    rcp_user_model, rcp_account_model, rcp_card_model = await new_user_with_account_and_card(
        user_tlg_id=987, account_uniq_id=567, card_uniq_id=5678, account_value=1000
    )

    mocked_update = get_update_for_command(f"/send_to_user {rcp_user_model.tlg_id} 300")

    mocker.patch("src.app.internal.transport.bot.handlers.transfer_to", return_value=False)
    await send_to(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=ERROR_DURING_TRANSFER)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_send_to_with_valid_transfer(
    mocked_context, sender_with_bank_requisites, telegram_chat, get_list_with_updates, new_user_with_account_and_card
):
    sender_account_model = await Account.objects.filter(uniq_id=123).afirst()
    sender_account_model.value += 1000
    await sender_account_model.asave()

    rcp_user_model, rcp_account_model, rcp_card_model = await new_user_with_account_and_card(
        user_tlg_id=987, account_uniq_id=567, card_uniq_id=5678, account_value=1000
    )

    transfer_on_each_step = 100

    commands_list = [
        f"/send_to_account {rcp_account_model.uniq_id} {transfer_on_each_step}",
        f"/send_to_card {rcp_card_model.uniq_id} {transfer_on_each_step}",
        f"/send_to_user {rcp_user_model.tlg_id} {transfer_on_each_step}",
    ]

    updates_list = get_list_with_updates(commands_list)
    for mocked_update in updates_list:
        await send_to(mocked_update, mocked_context)

        rcp_name =  " ".join([rcp_user_model.first_name, rcp_user_model.last_name]) 
        mocked_context.bot.send_message.assert_called_with(
            chat_id=telegram_chat.id, text=get_successful_transfer_message(rcp_name, transfer_on_each_step)
        )

    assert (await Account.objects.filter(uniq_id=123).afirst()).value == 700
    assert (await Account.objects.filter(uniq_id=567).afirst()).value == 1300
