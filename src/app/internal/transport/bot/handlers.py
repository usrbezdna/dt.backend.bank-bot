import logging

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException

from app.internal.models.user import User
from app.internal.services.favourites_service import (
    add_fav_to_user,
    del_fav_from_user,
    ensure_user_in_fav,
    get_fav_obj,
    get_list_of_favourites,
    prevent_ops_with_themself,
    prevent_second_time_add,
    try_get_another_user,
)
from app.internal.services.payment_service import (
    get_account_from_card,
    get_account_from_db,
    get_card_for_account,
    get_card_from_db,
    get_user_payment_account,
    try_get_recipient_card,
)
from app.internal.services.telegram_service import verified_phone_required
from app.internal.services.user_service import (
    get_user_by_id,
    get_user_by_username,
    save_user_to_db,
    update_user_phone_number,
)

from .telegram_messages import (
    ABSENT_ARG_FAV_MSG,
    ABSENT_FAV_MSG,
    ABSENT_FAV_USER,
    ABSENT_ID_NUMBER,
    ABSENT_OLD_FAV_USER,
    ABSENT_PN_MSG,
    HELP_MSG,
    INVALID_PN_MSG,
    NOT_INT_FORMAT_MSG,
    RSP_NOT_FOUND,
    SEND_TO_ARGS,
    get_success_for_deleted_fav,
    get_success_for_new_fav,
    get_success_phone_msg,
    get_unique_start_msg,
)

logger = logging.getLogger("django.server")


async def start(update, context):
    """
    Handler for /start command.
    (Handlers usually take 2 arguments: update and context).
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback

    """
    user_data = update.effective_user
    chat_id = update.effective_chat.id

    tlg_user = User(
        tlg_id=user_data.id,
        username=user_data.username if user_data.username else "",
        first_name=user_data.first_name,
        last_name=user_data.last_name if user_data.last_name else "",
        phone_number="",
    )

    await save_user_to_db(tlg_user)
    await context.bot.send_message(chat_id=chat_id, text=get_unique_start_msg(user_data.first_name))


async def get_help(update, context):
    """
    Handler for /help command.
    Returns some info about currently supported commands.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_MSG)


async def set_phone(update, context):
    """
    Handler for /set_phone command.
    Supports phone validation and user existence checking.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    user_data = update.effective_user
    chat_id = update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:
        user_from_db = await get_user_by_id(user_data.id)
        phone_number = command_data[1]

        if phone_number.startswith("+"):
            try:
                parsed_number = PhoneNumber.from_string(phone_number)

                await update_user_phone_number(user_from_db, parsed_number)
                await context.bot.send_message(chat_id=chat_id, text=get_success_phone_msg(parsed_number))

            except NumberParseException:
                logger.info("User did not provide a valid phone number")
                await context.bot.send_message(chat_id=chat_id, text=INVALID_PN_MSG)
            finally:
                return

        await context.bot.send_message(chat_id=chat_id, text=NOT_INT_FORMAT_MSG)
        return
    await context.bot.send_message(chat_id=chat_id, text=ABSENT_PN_MSG)


@verified_phone_required
async def me(update, context):
    """
    Hander for /me command.
    Returns full information about Telegram user.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    user_id = update.effective_user.id
    user_from_db = await get_user_by_id(user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Here is some info about you:\n\n" f"{str(user_from_db)}"
    )


@verified_phone_required
async def check_payable(update, context):
    """
    Handler for /check_card command
    Returns remaining value on specified card or
    error message if card is absent.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    chat_id = update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:

        argument, uniq_id = command_data[0], command_data[1]
        obj_option = None

        if argument == "/check_card":
            obj_option = await get_card_from_db(uniq_id)
        else:
            obj_option = await get_account_from_db(uniq_id)

        if obj_option and argument == "/check_card":
            account = await get_account_from_card(uniq_id)

            await context.bot.send_message(chat_id=chat_id, text=f"This card balance is {account.value}")

        elif obj_option:
            await context.bot.send_message(chat_id=chat_id, text=f"This account balance is {obj_option.value}")

        else:
            logger.info(f"Card / account with ID {uniq_id} not found in DB")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="Unable to find balance for this card / account"
            )

        return

    await context.bot.send_message(chat_id=chat_id, text=ABSENT_ID_NUMBER)


@verified_phone_required
async def list_fav(update, context):
    """
    Handler for /list_fav command.
    Returns list of favourites users with max length 5
    or error message if user don't have any favs.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """

    users_limit = 5
    res_msg = ""

    user_id, chat_id = update.effective_user.id, update.effective_chat.id

    if await get_fav_obj(user_id) and await (await get_list_of_favourites(tlg_id=user_id)).acount() > 0:
        favs = await get_list_of_favourites(tlg_id=user_id)

        async for fav_user in favs[:users_limit]:

            res_msg += f"Name: {fav_user.first_name} {fav_user.last_name}," + f" ID: {fav_user.tlg_id}, Phone: "
            res_msg += f"{fav_user.phone_number}\n" if fav_user.hasPhoneNumber() else "None\n"

        await context.bot.send_message(chat_id=chat_id, text=res_msg)
        return

    logger.info(f"Unable to find favourites for user with ID: {user_id}")
    await context.bot.send_message(chat_id=chat_id, text=ABSENT_FAV_MSG)


@verified_phone_required
async def add_fav(update, context):
    """
    Handler for /add_fav command.
    Adds another Telegram user to the list of favourites.
    Accepts Telegram ID or username.
    ----------
    :param update: recieved Update object
    :param context: context object passed to the callback
    """
    user_id, chat_id = update.effective_user.id, update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:
        argument = command_data[1]

        another_user_option, arg_error = await try_get_another_user(context, chat_id, argument)
        if arg_error:
            return

        if another_user_option:

            error_op = await prevent_ops_with_themself(context, chat_id, user_id, another_user_option)
            error_sec = await prevent_second_time_add(context, chat_id, user_id, another_user_option)

            if error_op or error_sec:
                return

            await add_fav_to_user(user_id, another_user_option)
            await context.bot.send_message(chat_id=chat_id, text=get_success_for_new_fav(another_user_option))

            return
        await context.bot.send_message(chat_id=chat_id, text=ABSENT_FAV_USER)
        return
    await context.bot.send_message(chat_id=chat_id, text=ABSENT_ARG_FAV_MSG)


@verified_phone_required
async def del_fav(update, context):
    """
    Handler for /del_fav command.
    Deletes Telegram user from specified favourites.
    ----------
    :param update: recieved Update object
    :param context: context object
    """
    user_id, chat_id = update.effective_user.id, update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:
        argument = command_data[1]

        another_user_option, arg_error = await try_get_another_user(context, chat_id, argument)
        if arg_error:
            return

        if another_user_option:

            error_op = await prevent_ops_with_themself(context, chat_id, user_id, another_user_option)
            if error_op:
                return

            error_not_in_fav = await ensure_user_in_fav(context, chat_id, user_id, another_user_option)
            if error_not_in_fav:
                return

            await del_fav_from_user(user_id, another_user_option)
            await context.bot.send_message(chat_id=chat_id, text=get_success_for_deleted_fav(another_user_option))

            return

        await context.bot.send_message(chat_id=chat_id, text=ABSENT_OLD_FAV_USER)
        return
    await context.bot.send_message(chat_id=chat_id, text=ABSENT_ARG_FAV_MSG)


@verified_phone_required
async def send_to(update, context):
    """
    Handler for /send_to command.
    Allows transactions between Users.
    ----------
    :param update: recieved Update object
    :param context: context object
    """
    user_id, chat_id = update.effective_user.id, update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 3:

        arg_user, arg_value = command_data[1], command_data[2]

        sending_user = await get_user_by_id(user_id)
        sending_payment_account = await get_user_payment_account(sending_user)
        sending_card = await get_card_for_account(sending_payment_account)

        if not sending_payment_account or not sending_card:
            await context.bot.send_message(
                chat_id=chat_id, text="You should have payment account and at least one card for making transactions!"
            )
            return

        card_opt, arg_error = await try_get_recipient_card(context, chat_id, arg_user)
        if arg_error:
            return

        if card_opt:
            print("OK", arg_value)

            return

        return
    await context.bot.send_message(chat_id=chat_id, text=SEND_TO_ARGS)
