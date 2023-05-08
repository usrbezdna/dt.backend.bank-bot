



from src.app.internal.services.telegram_service import verified_phone_required


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