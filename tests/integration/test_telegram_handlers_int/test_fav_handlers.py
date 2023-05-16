from unittest.mock import call

import pytest

from src.app.internal.api_v1.favourites.presentation.bot.telegram_messages import (
    ABSENT_ARG_FAV_MSG, ABSENT_FAV_MSG, ABSENT_FAV_USER, 
    NOT_VALID_ID_MSG, RESTRICT_SECOND_TIME_ADD, RESTRICT_SELF_OPS, USER_NOT_IN_FAV,
    get_result_message_for_user_favourites, get_success_msg_for_deleted_fav, 
    get_success_msg_for_new_fav,
)

from src.app.models import Favourite


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_list_fav_with_absent_fav_obj(telegram_fav_handlers, mocked_context, already_verified_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/list_fav")
    await telegram_fav_handlers.list_fav(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=ABSENT_FAV_MSG)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_list_fav_with_empty_list(telegram_fav_handlers, mocked_context, already_verified_user, telegram_chat, get_update_for_command):
    mocked_update = get_update_for_command("/list_fav")

    await Favourite.objects.acreate(tlg_id=already_verified_user.id)
    await telegram_fav_handlers.list_fav(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=ABSENT_FAV_MSG)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_list_fav_with_added_user(
    telegram_fav_handlers, mocked_context, already_verified_user, 
    user_model_without_verified_pn, telegram_chat, get_update_for_command
):
    new_fav_user_model = user_model_without_verified_pn(tlg_id=100)
    await new_fav_user_model.asave()

    await Favourite.objects.acreate(tlg_id=already_verified_user.id)
    fav_object = (await Favourite.objects.aget(pk=already_verified_user.id)).favourites

    await fav_object.aadd(new_fav_user_model)

    mocked_update = get_update_for_command("/list_fav")
    await telegram_fav_handlers.list_fav(mocked_update, mocked_context)


    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_result_message_for_user_favourites(favs_list=[new_fav_user_model])
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_ops_with_no_argument(
    telegram_fav_handlers, mocked_context, 
    already_verified_user, telegram_chat, get_update_for_command
):
    mocked_add_update = get_update_for_command("/add_fav")
    mocked_del_update = get_update_for_command("/del_fav")

    await telegram_fav_handlers.add_fav(mocked_add_update, mocked_context)
    await telegram_fav_handlers.del_fav(mocked_del_update, mocked_context)

    mock_error_call = call(chat_id=telegram_chat.id, text=ABSENT_ARG_FAV_MSG)

    assert len(mocked_context.mock_calls) == 2
    mocked_context.bot.send_message.assert_has_calls([mock_error_call] * 2, any_order=True)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_ops_with_invalid_telegram_id(
    telegram_fav_handlers, mocked_context, 
    already_verified_user, telegram_chat, get_list_with_updates
):
    add_commands_list = ["/add_fav sometrashinput", "/add_fav -9999999", "/add_fav -4214", "/add_fav 0"]

    del_command_list = ["/del_fav yt3qwtfa", "/del_fav -6363214", "/del_fav -900", "/del_fav 0"]

    add_updates_list = get_list_with_updates(add_commands_list)
    for add_update in add_updates_list:
        await telegram_fav_handlers.add_fav(add_update, mocked_context)

    del_updates_list = get_list_with_updates(del_command_list)
    for del_update in del_updates_list:
        await telegram_fav_handlers.del_fav(del_update, mocked_context)

    mock_error_call = call(chat_id=telegram_chat.id, text=NOT_VALID_ID_MSG)
    updates_total_len = len(add_updates_list) + len(del_updates_list)

    assert len(mocked_context.mock_calls) == updates_total_len
    mocked_context.bot.send_message.assert_has_calls([mock_error_call] * updates_total_len, any_order=True)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_ops_with_db_miss(
    telegram_fav_handlers, mocked_context, 
    already_verified_user, telegram_chat, get_list_with_updates
):
    add_commands_list = ["/add_fav @AbsentUser", "/add_fav 59014"]
    del_commands_list = ["/del_fav @SomeAbsentUser", "/del_fav 98765"]

    add_updates_list = get_list_with_updates(add_commands_list)
    for add_update in add_updates_list:
        await telegram_fav_handlers.add_fav(add_update, mocked_context)

    del_updates_list = get_list_with_updates(del_commands_list)
    for del_update in del_updates_list:
        await telegram_fav_handlers.del_fav(del_update, mocked_context)

    mock_add_error_call = call(chat_id=telegram_chat.id, text=ABSENT_FAV_USER)

    add_len = len(add_updates_list)
    del_len = len(del_updates_list)

    assert len(mocked_context.mock_calls) == add_len + del_len

    mocked_context.bot.send_message.assert_has_calls(
        [mock_add_error_call] * (add_len + del_len), any_order=True
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_ops_with_self_addition_prevention(
    telegram_fav_handlers, mocked_context, 
    already_verified_user, telegram_chat, get_update_for_command
):
    add_mocked_update = get_update_for_command(f"/add_fav {already_verified_user.id}")
    del_mocked_update = get_update_for_command(f"/del_fav {already_verified_user.id}")

    await telegram_fav_handlers.add_fav(add_mocked_update, mocked_context)
    await telegram_fav_handlers.del_fav(del_mocked_update, mocked_context)

    mock_error_call = call(chat_id=telegram_chat.id, text=RESTRICT_SELF_OPS)

    assert await Favourite.objects.filter(tlg_id=already_verified_user.id).afirst() is None

    assert len(mocked_context.mock_calls) == 2
    mocked_context.bot.send_message.assert_has_calls([mock_error_call] * 2, any_order=True)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_add_fav_with_second_time_add_prevention(
    telegram_fav_handlers,
    mocked_context,
    already_verified_user,
    user_model_without_verified_pn,
    telegram_chat,
    get_update_for_command,
):
    new_fav_user_model = user_model_without_verified_pn(tlg_id=100)
    await new_fav_user_model.asave()

    mocked_update = get_update_for_command(f"/add_fav {new_fav_user_model.tlg_id}")
    await telegram_fav_handlers.add_fav(mocked_update, mocked_context)

    fav_object = (await Favourite.objects.aget(pk=already_verified_user.id)).favourites

    assert await fav_object.acount() == 1
    assert await fav_object.acontains(new_fav_user_model)

    await telegram_fav_handlers.add_fav(mocked_update, mocked_context)

    new_fav_object = (await Favourite.objects.aget(pk=already_verified_user.id)).favourites
    assert await new_fav_object.acount() == 1

    mocked_context.bot.send_message.assert_called_with(
        chat_id=telegram_chat.id, text=RESTRICT_SECOND_TIME_ADD
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_add_fav_with_valid_args(
    telegram_fav_handlers,
    mocked_context,
    already_verified_user,
    user_model_without_verified_pn,
    telegram_chat,
    get_update_for_command,
):
    new_fav_user_model = user_model_without_verified_pn(tlg_id=100)
    await new_fav_user_model.asave()

    mocked_update = get_update_for_command("/add_fav @Testuser")
    await telegram_fav_handlers.add_fav(mocked_update, mocked_context)

    fav_object = (await Favourite.objects.aget(pk=already_verified_user.id)).favourites

    assert await fav_object.acount() == 1
    assert await fav_object.acontains(new_fav_user_model)

    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_success_msg_for_new_fav(new_fav_user_model)
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_del_fav_with_user_not_in_favs(
    telegram_fav_handlers,
    mocked_context,
    already_verified_user,
    user_model_without_verified_pn,
    telegram_chat,
    get_update_for_command,
):
    new_fav_user_model = user_model_without_verified_pn(tlg_id=100)
    await new_fav_user_model.asave()

    mocked_update = get_update_for_command(f"/del_fav {new_fav_user_model.tlg_id}")

    await Favourite.objects.acreate(tlg_id=already_verified_user.id)
    await telegram_fav_handlers.del_fav(mocked_update, mocked_context)

    mocked_context.bot.send_message.assert_called_once_with(chat_id=telegram_chat.id, text=USER_NOT_IN_FAV)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
async def test_del_fav_with_valid_args(
    telegram_fav_handlers,
    mocked_context,
    already_verified_user,
    user_model_without_verified_pn,
    telegram_chat,
    get_update_for_command,
):
    new_fav_user_model = user_model_without_verified_pn(tlg_id=100)
    await new_fav_user_model.asave()


    await Favourite.objects.acreate(tlg_id=already_verified_user.id)
    fav_object = (await Favourite.objects.aget(pk=already_verified_user.id)).favourites
    await fav_object.aadd(new_fav_user_model)


    initial_fav_object = (await Favourite.objects.aget(pk=already_verified_user.id)).favourites
    assert await initial_fav_object.acount() == 1

    del_mocked_update = get_update_for_command(f"/del_fav {new_fav_user_model.tlg_id}")
    await telegram_fav_handlers.del_fav(del_mocked_update, mocked_context)


    updated_fav_object = (await Favourite.objects.aget(pk=already_verified_user.id)).favourites
    assert await updated_fav_object.acount() == 0

    mocked_context.bot.send_message.assert_called_with(
        chat_id=telegram_chat.id, text=get_success_msg_for_deleted_fav(new_fav_user_model)
    )