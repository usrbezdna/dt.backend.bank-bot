from unittest.mock import call

import pytest

from src.app.internal.services.user_service import get_user_by_id
from src.app.internal.transport.bot.handlers import me, set_phone, start
from src.app.internal.transport.bot.telegram_messages import (
    INVALID_PN_MSG,
    ME_WITH_NO_USER,
    NO_VERIFIED_PN,
    NOT_INT_FORMAT_MSG,
    get_info_for_me_handler,
    get_success_phone_msg,
    get_unique_start_msg,
)
from src.app.models import User


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db
async def test_start(mocked_context, telegram_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/start")
    await start(mocked_update, mocked_context)

    await User.objects.filter(tlg_id=telegram_user.id).afirst()
    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_unique_start_msg(telegram_user.first_name)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_set_phone_with_valid_pn(mocked_context, already_saved_user, telegram_chat, get_update_for_command):
    new_valid_phone_number = "+13371707"

    assert (await get_user_by_id(already_saved_user.id)).phone_number != new_valid_phone_number

    mocked_update = get_update_for_command(f"/set_phone {new_valid_phone_number}")
    await set_phone(mocked_update, mocked_context)

    assert (await get_user_by_id(already_saved_user.id)).phone_number == new_valid_phone_number
    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_success_phone_msg(new_valid_phone_number)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_me_without_verified_phone(mocked_context, already_saved_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/me")
    await me(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=NO_VERIFIED_PN)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_me_without_user(mocked_context, telegram_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/me")

    await me(mocked_update, mocked_context)
    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=ME_WITH_NO_USER)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_me_with_verified_phone(mocked_context, already_verified_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/me")
    await me(mocked_update, mocked_context)

    user_model = await get_user_by_id(tlg_id=already_verified_user.id)

    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_info_for_me_handler(user_model)
    )
