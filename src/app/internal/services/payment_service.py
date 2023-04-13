import logging

from asgiref.sync import sync_to_async
from django.db import DatabaseError, transaction

from app.models import User

from app.internal.transport.bot.telegram_messages import (
    CARD_NOT_FOUND,
    NOT_VALID_ID_MSG,
    RSP_NOT_FOUND,
    RSP_USER_WITH_NO_ACC,
    RSP_USER_WITH_NO_CARDS,
    SENDER_RESTRICTION,
)
from app.models import Account, Card, Transaction


from .favourites_service import try_get_another_user
from .user_service import get_user_by_id
from django.db.models import F


logger = logging.getLogger("django.server")


@sync_to_async
def get_card_with_account_by_card_id(card_uniq_id):
    """
    Returns Card with uniq_id or None. 
    Also makes a foreign-key selection of corresponding account.

    :param card_uniq_id: uniq_id of this Card
    """
    return Card.objects.filter(uniq_id=card_uniq_id).\
        select_related('corresponding_account').first()


@sync_to_async
def get_account_from_db(uniq_id):
    """
    Returns Account with provided uniq_id or None.
    :param uniq_id: uniq_id of this Account
    """
    return Account.objects.filter(uniq_id=uniq_id).first()


@sync_to_async
def get_account_from_card(uniq_id):
    """
    Returns corresponding Account for specified Card.
    :param uniq_id: uniq_id of this Card
    """
    return Card.objects.get(uniq_id=uniq_id).corresponding_account


@sync_to_async
def get_owner_name_from_account(uniq_id):
    """
    Returns owner of this payment Account.
    :param uniq_id: uniq_id of this Account
    """
    return Account.objects.select_related('owner').\
        values_list('owner__first_name', 'owner__last_name').\
        get(pk=uniq_id)


@sync_to_async
def get_user_payment_account(user):
    """
    Returns Payment Account or None for this Telegram User
    :param user: Telegram User object
    """
    return Account.objects.filter(owner=user).first()


@sync_to_async
def get_first_card_for_account(account):
    """
    This function returns first Card (or None) for Payment Account
    :param account: Payment Account object
    """
    return Card.objects.filter(corresponding_account=account).\
        select_related('corresponding_account').first()



@sync_to_async
def transfer_to(sender_acc, recipient_acc, transferring_value):
    """
    Transfers value from first_payment_account to second_payment_account.
    Saves each Payment Transaction
    Returns success flag
    ----------
    :param first_payment_acc, second_payment_acc: payment Accounts
    :value: transferring value
    """
    success_flag = False
    try:
        with transaction.atomic():

            sender_acc.value = F('value') - transferring_value
            recipient_acc.value = F('value') + transferring_value

            sender_acc.save()
            recipient_acc.save()

            save_payment_transaction(sender_acc, recipient_acc, transferring_value)
            success_flag = True

    except DatabaseError as err:
        logger.error(f"Error during transfer_to call:\n{err}")

    finally:
        return success_flag

@sync_to_async
def get_list_of_inter_usernames(user_id):
    """
    Retuns list of usernames for users who have
    interacted with user_id
    ----------
    :param user_id: Telegram ID of specified user 
    """
    qs_tx_list = Transaction.objects.\
        select_related('tx_sender__owner', 'tx_recip__owner').\
        values_list('tx_sender__owner', 'tx_recip__owner')
    
    list_of_ids = []
    for sender_with_recip_ids in qs_tx_list:
          first_id, second_id = sender_with_recip_ids
          
          id_to_add = first_id if user_id != first_id else second_id
          list_of_ids.append(id_to_add)

    uniq_list_of_ids = list(set(list_of_ids))
    
    return list(User.objects.filter(tlg_id__in=uniq_list_of_ids).\
           values_list('username', flat=True).all())


def get_result_message_for_list_interacted(usernames_list):
    """
    Returns message with usernames of users who
    have interacted with this user.
    ----------
    :param usernames_list: list of usernames
    """
    res_msg = 'Here is the list of interacted users:'
    for username in usernames_list:
        res_msg += f'\n - {username}'

    return res_msg


def save_payment_transaction(sender_acc, recipient_acc, transferring_value):
    """
    Saves payment transaction to DB.
    ----------
    :param sender_acc: Payment Account of sender
    :param recipient_acc: Payment Account of recipient
    :param transferring_value: tx value
    """
    Transaction.objects.create(
        tx_sender = sender_acc,
        tx_recip = recipient_acc,
        tx_value = transferring_value
    )


async def id_is_valid(context, chat_id, identifier):
    """
    Ensures that provided identifier is a positive number.
    Returns success flag.
    ----------
    :param context: context object
    :param chat_id: Telegram User chat_id
    :param identifier: ID to check

    :return: success flag (if ID is valid)
    """
    if identifier.isdigit() and int(identifier) > 0:
        return True
    await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
    return False


async def account_has_any_cards(context, chat_id, account):
    """
    Checks whether or not this account has any linked cards.
    Returns first Card or None and error flag.
    ----------
    :param context: context object
    :param chat_id: Telegram User chat_id
    :param account: Payment Account object

    :return: Tuple with Card object and error flag
    """
    card_with_acc = await get_first_card_for_account(account)
    if card_with_acc:
        return (card_with_acc, False)
    
    await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_CARDS)
    return (None, True)


async def check_bank_requisites_for_sender(context, chat_id, user_id):
    """
    Checks whether this sending account has any Cards and Payment account.
    Returns Payment Account (or None) and sending_requisites_error flag
    ----------
    :param context: context object
    :param chat_id: Telegram User chat_id
    :param user_id: Telegram User ID
    """
    sending_user = await get_user_by_id(user_id)
    sending_payment_account = await get_user_payment_account(sending_user)
    sending_card = await get_first_card_for_account(sending_payment_account)

    if not sending_payment_account or not sending_card:
        await context.bot.send_message(chat_id=chat_id, text=SENDER_RESTRICTION)
        return (None, True)
    return (sending_payment_account, False)


async def try_get_recipient_card(context, chat_id, arg_user_or_id, arg_command):
    """
    This function tries to get the recipient card for the transaction.
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID
    :param arg_user: Telegram username (or ID) / Card ID / Account ID

    :return: Tuple with Card object and error flag
    """

    match arg_command:

        case "/send_to_user":
            return await handle_case_with_send_to_user(context, chat_id, arg_user_or_id)

        case "/send_to_account":
            return await handle_case_with_send_to_account(context, chat_id, arg_user_or_id)

        case "/send_to_card":
            return await handle_case_with_send_to_card(context, chat_id, arg_user_or_id)


async def handle_case_with_send_to_user(context, chat_id, arg_user_or_id):
    """
    Tries to get recipient card for send_to_user case
    (Sender have specified another Telegram User as a recipient)
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID
    :param arg_user_or_id: Recipient Telegram username (or ID)

    :return: Tuple with Card object and error flag
    """

    recipient_user_opt, arg_error = await try_get_another_user(context, chat_id, arg_user_or_id)
    if arg_error:
        return (None, True)

    if recipient_user_opt:
        account_opt = await get_user_payment_account(recipient_user_opt)

        if account_opt:
            card_with_acc, cards_error = await account_has_any_cards(context, chat_id, account_opt)
            return (card_with_acc, cards_error)

        await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_ACC)
        return (None, True)

    await context.bot.send_message(chat_id=chat_id, text=RSP_NOT_FOUND)
    return (None, True)


async def handle_case_with_send_to_account(context, chat_id, account_id):
    """
    Tries to get recipient card for send_to_account case
    (Sender have specified recipient Account ID)
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID
    :param account_id: Recipient Payment Account uniq ID

    :return: Tuple with Card object and error flag
    """
    if await id_is_valid(context, chat_id, account_id):
        account_opt = await get_account_from_db(account_id)

        if account_opt:
            card_with_acc, no_cards_error = await account_has_any_cards(context, chat_id, account_opt)
            return (card_with_acc, no_cards_error)
        
    return (None, True)


async def handle_case_with_send_to_card(context, chat_id, card_id):
    """
    Tries to get recipient card for send_to_card case
    (Sender have specified recipient Card ID)
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID
    :param card_id: Recipient Card ID

    :return: Tuple with Card object and error flag
    """
    if await id_is_valid(context, chat_id, card_id):
        card_with_acc = await get_card_with_account_by_card_id(card_id)

        if card_with_acc:
            return (card_with_acc, False)

        await context.bot.send_message(chat_id=chat_id, text=CARD_NOT_FOUND)
        return (None, True)

    return (None, True)
