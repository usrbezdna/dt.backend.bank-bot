




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