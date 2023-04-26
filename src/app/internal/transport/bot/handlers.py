import logging

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException

from app.internal.services.favourites_service import (
    get_limited_list_of_favourites,
    get_result_message_for_user_favourites,
    prevent_ops_with_themself,
    try_add_fav_to_user,
    try_del_fav_from_user,
    try_get_another_user,
)
from app.internal.services.payment_service import (
    get_account_from_db,
    get_bank_requisites_for_sender,
    get_card_with_related,
    get_list_of_inter_usernames,
    get_list_of_transactions_for_the_last_month,
    get_owner_name_from_account,
    get_result_message_for_list_interacted,
    get_result_message_for_transaction_state,
    send_result_message_for_transaction_state,
    transfer_to,
    try_get_recipient_card,
)
from app.internal.services.telegram_service import verified_phone_required
from app.internal.services.user_service import (
    create_user_model_for_telegram,
    get_user_by_id,
    save_user_to_db,
    update_user_password,
    update_user_phone_number,
)

from .telegram_messages import (
    ABSENT_ARG_FAV_MSG,
    ABSENT_FAV_MSG,
    ABSENT_FAV_USER,
    ABSENT_ID_NUMBER,
    ABSENT_OLD_FAV_USER,
    ABSENT_PASSWORD_MSG,
    ABSENT_PN_MSG,
    BALANCE_NOT_FOUND,
    ERROR_DURING_TRANSFER,
    HELP_MSG,
    INCR_TX_VALUE,
    INSUF_BALANCE,
    INVALID_PN_MSG,
    NO_INTERACTED_USERS,
    NO_TXS_FOR_LAST_MONTH,
    NOT_INT_FORMAT_MSG,
    NOT_VALID_ID_MSG,
    PASSWORD_UPDATED,
    SELF_TRANSFER_ERROR,
    STATE_NOT_FOUND,
    get_info_for_me_handler,
    get_message_for_send_command,
    get_message_with_balance,
    get_success_for_deleted_fav,
    get_success_for_new_fav,
    get_success_phone_msg,
    get_successful_transfer_message,
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
    telegram_user = update.effective_user
    chat_id = update.effective_chat.id

    user_model = create_user_model_for_telegram(telegram_user)

    await save_user_to_db(user_model)
    await context.bot.send_message(chat_id=chat_id, text=get_unique_start_msg(user_model.first_name))


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
    chat_id = update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:
        phone_number = command_data[1]

        if phone_number.startswith("+"):
            try:
                parsed_number = PhoneNumber.from_string(phone_number)

                await update_user_phone_number(update.effective_user.id, parsed_number)
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

    await context.bot.send_message(chat_id=update.effective_chat.id, text=get_info_for_me_handler(user_from_db))


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
        command, uniq_id = command_data[0], command_data[1]
        obj_option = None

        if not uniq_id.isdigit() or int(uniq_id) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return

        if command == "/check_card":
            obj_option = await get_card_with_related(uniq_id)
        else:
            obj_option = await get_account_from_db(uniq_id)

        if obj_option and command == "/check_card":
            await context.bot.send_message(
                chat_id=chat_id, text=get_message_with_balance(obj_option.corresponding_account)
            )

        elif obj_option and command == "/check_account":
            await context.bot.send_message(chat_id=chat_id, text=get_message_with_balance(obj_option))

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=BALANCE_NOT_FOUND)
            logger.info(f"Card / account with ID {uniq_id} not found in DB")

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

    favs_limit = 5

    user_id, chat_id = update.effective_user.id, update.effective_chat.id
    favs_list_option = await get_limited_list_of_favourites(tlg_id=user_id, favs_limit=favs_limit)

    if favs_list_option:
        res_msg = get_result_message_for_user_favourites(favs_list_option)

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
            error_ops = await prevent_ops_with_themself(context, chat_id, user_id, another_user_option.tlg_id)
            if error_ops:
                return

            error_add = await try_add_fav_to_user(context, chat_id, user_id, another_user_option)
            if error_add:
                return

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
            error_ops = await prevent_ops_with_themself(context, chat_id, user_id, another_user_option.tlg_id)
            if error_ops:
                return

            error_not_in_fav = await try_del_fav_from_user(context, chat_id, user_id, another_user_option)
            if error_not_in_fav:
                return

            await context.bot.send_message(chat_id=chat_id, text=get_success_for_deleted_fav(another_user_option))
            return

        await context.bot.send_message(chat_id=chat_id, text=ABSENT_OLD_FAV_USER)
        return

    await context.bot.send_message(chat_id=chat_id, text=ABSENT_ARG_FAV_MSG)


@verified_phone_required
async def send_to(update, context):
    """
    Universal handler for all /send_to_{recip} commands.
    Allows transactions between Users.
    ----------
    :param update: recieved Update object
    :param context: context object
    """
    user_id, chat_id = update.effective_user.id, update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 3:
        arg_command, arg_user_or_id, arg_value = command_data

        if not arg_value.isdigit() or int(arg_value) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=INCR_TX_VALUE)
            return

        value = int(arg_value)

        sender_card_with_acc, requisites_error = await get_bank_requisites_for_sender(context, chat_id, user_id)
        if requisites_error:
            return

        recip_card_with_acc, error = await try_get_recipient_card(context, chat_id, arg_user_or_id, arg_command)
        if error:
            return

        sending_payment_account = sender_card_with_acc.corresponding_account
        recipient_payment_account = recip_card_with_acc.corresponding_account

        if recipient_payment_account == sending_payment_account:
            await context.bot.send_message(chat_id=chat_id, text=SELF_TRANSFER_ERROR)
            return

        success_flag = await transfer_to(sending_payment_account, recipient_payment_account, value, context, chat_id)

        if success_flag:
            recipient_name_as_tuple = await get_owner_name_from_account(recipient_payment_account.uniq_id)
            recipient_name = " ".join(recipient_name_as_tuple)

            await context.bot.send_message(chat_id=chat_id, text=get_successful_transfer_message(recipient_name, value))

        return

    await context.bot.send_message(chat_id=chat_id, text=get_message_for_send_command(command_data[0]))


@verified_phone_required
async def list_inter(update, context):
    """
    Handler for /list_inter command.
    Returns list of users this user have interacted with.
    Or returns empty list if user have no payment transactions.
    ----------
    :param update: recieved Update object
    :param context: context object
    """

    user_id, chat_id = update.effective_user.id, update.effective_chat.id
    usernames = await get_list_of_inter_usernames(user_id)

    if usernames:
        await context.bot.send_message(chat_id=chat_id, text=get_result_message_for_list_interacted(usernames))
        return
    await context.bot.send_message(chat_id=chat_id, text=NO_INTERACTED_USERS)


@verified_phone_required
async def state_payable(update, context):
    """
    Handler for /state_card and /state_account commands.

    Returns list of payment transaction for specified
    card or account for the last month.
    Or returns empty list if user have no payment transactions.
    ----------
    :param update: recieved Update object
    :param context: context object
    """

    chat_id = update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:
        command, uniq_id = command_data[0], command_data[1]
        obj_option = None

        if not uniq_id.isdigit() or int(uniq_id) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return

        if command == "/state_card":
            obj_option = await get_card_with_related(uniq_id)
        else:
            obj_option = await get_account_from_db(uniq_id)

        if obj_option and command == "/state_card":
            owner_id = obj_option.corresponding_account.owner.tlg_id
            await send_result_message_for_transaction_state(context, chat_id, owner_id)

        elif obj_option and command == "/state_account":
            owner_id = obj_option.owner.tlg_id
            await send_result_message_for_transaction_state(context, chat_id, owner_id)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=STATE_NOT_FOUND)
            logger.info(f"Card / account with ID {uniq_id} not found in DB")

        return

    await context.bot.send_message(chat_id=chat_id, text=ABSENT_ID_NUMBER)


@verified_phone_required
async def set_password(update, context):
    """
    Handler for /set_password
    Allows user to set password. 
    ----------
    :param update: recieved Update object
    :param context: context object
    """

    user_id, chat_id = update.effective_user.id, update.effective_chat.id
    command_data = update.message.text.split(" ")

    if len(command_data) == 2:
        argument = command_data[1]

        await update_user_password(tlg_id=user_id, new_password=argument)
        await context.bot.send_message(chat_id=chat_id, text=PASSWORD_UPDATED)

        return
    await context.bot.send_message(chat_id=chat_id, text=ABSENT_PASSWORD_MSG)