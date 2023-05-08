


from src.app.internal.services.telegram_service import verified_phone_required
from src.app.internal.transport.bot.telegram_messages import ABSENT_ARG_FAV_MSG, ABSENT_FAV_MSG, ABSENT_FAV_USER, get_success_for_new_fav


logger = logging.getLogger("django.server")

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