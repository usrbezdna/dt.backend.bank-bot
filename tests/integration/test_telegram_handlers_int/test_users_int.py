
import pytest

from src.app.internal.api_v1.users.presentation.bot.telegram_messages import (
    ABSENT_PASSWORD_MSG,
    NO_VERIFIED_PN,
    PASSWORD_UPDATED,
    get_info_for_me_handler,
    get_success_phone_msg,
    get_unique_start_msg,
)
from src.app.models import User


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db
@pytest.mark.valid_case
async def test_start(telegram_user_handlers, mocked_context, telegram_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/start")
    await telegram_user_handlers.start(mocked_update, mocked_context)

    await User.objects.filter(tlg_id=telegram_user.id).afirst()
    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_unique_start_msg(telegram_user.first_name)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_set_phone_with_valid_pn(telegram_user_handlers, mocked_context, already_saved_user, telegram_chat, get_update_for_command):

    new_valid_phone_number = "+79267378397"
    initial_phone_number = await User.objects.values_list('phone_number', flat=True).aget(pk=already_saved_user.id)

    assert initial_phone_number != new_valid_phone_number

    mocked_update = get_update_for_command(f"/set_phone {new_valid_phone_number}")
    await telegram_user_handlers.set_phone(mocked_update, mocked_context)

    updated_phone_number = await User.objects.values_list('phone_number', flat=True).aget(pk=already_saved_user.id)
    assert updated_phone_number == new_valid_phone_number

    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_success_phone_msg(new_valid_phone_number)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_me_without_verified_phone(telegram_user_handlers, mocked_context, already_saved_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/me")
    await telegram_user_handlers.me(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=NO_VERIFIED_PN)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_me_with_verified_phone(telegram_user_handlers, mocked_context, already_verified_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/me")
    await telegram_user_handlers.me(mocked_update, mocked_context)

    user_model = await User.objects.aget(pk=already_verified_user.id)

    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_info_for_me_handler(user_model)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_set_password_without_arg(telegram_user_handlers, mocked_context, already_verified_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/set_password")
    await telegram_user_handlers.set_password(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=ABSENT_PASSWORD_MSG)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_set_password_valid(telegram_user_handlers, mocked_context, already_verified_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/set_password 6543582413412")

    initial_password = await User.objects.values_list('password', flat=True).aget(pk=already_verified_user.id)
    assert initial_password == ''

    await telegram_user_handlers.set_password(mocked_update, mocked_context)

    updated_password = await User.objects.values_list('password', flat=True).aget(pk=already_verified_user.id)
    assert updated_password != ''

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=PASSWORD_UPDATED)