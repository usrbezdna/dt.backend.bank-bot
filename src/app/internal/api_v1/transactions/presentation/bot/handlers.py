from src.app.internal.services.telegram_service import verified_phone_required


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