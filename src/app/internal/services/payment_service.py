from datetime import timedelta
from django.utils import timezone

import calendar
import logging

from asgiref.sync import sync_to_async
from django.db import DatabaseError, transaction
from django.db.models.functions import (
    ExtractDay, ExtractMonth, ExtractYear, Concat
)

from asgiref.sync import async_to_sync
from app.models import User

from app.internal.transport.bot.telegram_messages import (
    CARD_NOT_FOUND,
    ERROR_DURING_TRANSFER,
    INSUF_BALANCE,
    NO_TXS_FOR_LAST_MONTH,
    NOT_VALID_ID_MSG,
    RSP_NOT_FOUND,
    RSP_USER_WITH_NO_ACC,
    RSP_USER_WITH_NO_CARDS,
    SENDER_RESTRICTION,
)

from app.models import Account, Card, Transaction
from .favourites_service import try_get_another_user
from django.db.models import F, Q, CharField, Value 


logger = logging.getLogger("django.server")


@sync_to_async
def get_card_with_related(card_uniq_id):
    """
    Returns Card with card_uniq_id or None. 
    Also makes a foreign-key selection of corresponding account.

    :param card_uniq_id: uniq_id of this Card
    """
    return Card.objects.filter(uniq_id=card_uniq_id).\
        select_related('corresponding_account__owner').first()


@sync_to_async
def get_account_from_db(uniq_id):
    """
    Returns Account with provided uniq_id or None.
    :param uniq_id: uniq_id of this Account
    """
    return Account.objects.filter(uniq_id=uniq_id).\
        select_related('owner').first()


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
    return Account.objects.\
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
def transfer_to(sender_acc, recipient_acc, transferring_value, context, chat_id):
    """
    Transfers value from first_payment_account to second_payment_account.
    Saves each Payment Transaction and returns success flag.
    ----------
    :param first_payment_acc, second_payment_acc: payment Accounts
    :value: transferring value
    """
    success_flag = False
    try:

        Account.objects.select_for_update().filter(
            uniq_id__in=[sender_acc.uniq_id, recipient_acc.uniq_id]
        )

        with transaction.atomic():

            if sender_acc.value - transferring_value >= 0:
                
                sender_acc.value = F('value') - transferring_value
                recipient_acc.value = F('value') + transferring_value

                sender_acc.save()
                recipient_acc.save()

                save_payment_transaction(sender_acc, recipient_acc, transferring_value)
                success_flag = True
            
            else:
                async_to_sync(context.bot.send_message)(chat_id=chat_id, text=INSUF_BALANCE)

    except DatabaseError as err:
        async_to_sync(context.bot.send_message)(chat_id=chat_id, text=ERROR_DURING_TRANSFER)

        logger.info(f"Error during transfer_to call:\n{err}")

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

    tx_list = list(Transaction.objects.filter(
        Q(tx_sender__owner__tlg_id = user_id) | 
        Q(tx_recip__owner__tlg_id = user_id)
    ).\
        order_by('tx_sender__owner__tlg_id', 'tx_recip__owner__tlg_id').\
        distinct('tx_sender__owner__tlg_id', 'tx_recip__owner__tlg_id').\
        values_list('tx_sender__owner', 'tx_recip__owner'))
    

    unique_tx_list = [list(i) for i in set(frozenset(tx_tuple) for tx_tuple in tx_list)]
    unique_ids = [tuple[1] if tuple[0] == user_id else tuple[0] for tuple in unique_tx_list]

    return list(User.objects.filter(tlg_id__in=unique_ids).\
           values_list('username', flat=True).all())

@sync_to_async
def get_list_of_transactions_for_the_last_month(user_id):
    """
    Returns list of payment transactions for the last
    month for Telegram user with ID user_id
    ----------
    :param user_id: Telegram ID of specified user 
    """

    today = timezone.now().date()

    number_of_days_in_month = calendar.monthrange(today.year, today.month)[1]
    some_day_a_month_ago = today - timedelta(days=number_of_days_in_month)

    tx_list = list(Transaction.objects.filter(

        Q ( 
            Q(tx_sender__owner__tlg_id = user_id) | 
            Q(tx_recip__owner__tlg_id = user_id) 
        ) 

        & Q(tx_timestamp__gt=some_day_a_month_ago)
        & Q(tx_timestamp__lte= today + timedelta(days=1))

    ).\

        annotate(
        
            date = Concat(
                ExtractDay('tx_timestamp'), Value('.'),
                ExtractMonth('tx_timestamp'), Value('.'),
                ExtractYear('tx_timestamp'),
                output_field=CharField()
            ),

            sender_name = Concat(
                'tx_sender__owner__first_name', Value(' '), 'tx_sender__owner__last_name',
                output_field=CharField()
            ),

            recip_name = Concat(
                'tx_recip__owner__first_name', Value(' '), 'tx_recip__owner__last_name',
                output_field=CharField()
            ), 

        ).\
        
        values(
            'tx_id', 'tx_value', 'sender_name', 'recip_name', 'date'
        )
    )

    return tx_list


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


def get_result_message_for_transaction_state(transactions_list):
    """
    Returns message with transactions for the last month.
    ----------
    :param transactions_list: list of transactions
    """ 
    res_msg = "List of transactions for the last month: \n\n"
    for tx_data in transactions_list:
        res_msg += (
            f"TX ID: {tx_data['tx_id']}, " + f"Date: {tx_data['date']}, " + f"Sender: {tx_data['sender_name']}, " +
            f"Recipient: {tx_data['recip_name']}, " + f"Value: {tx_data['tx_value']}\n"
        )

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


async def get_card_with_account_by_account_id(context, chat_id, account_id):
    """
    Checks whether or not this account has any linked cards.
    Returns first Card with linked Account | None and error flag.
    ----------
    :param context: context object
    :param chat_id: Telegram User chat_id
    :param account_id: Payment Account uniq_id

    :return: Tuple with Card object and error flag
    """
    error_flag = False
    card_with_acc = await Card.objects.\
        filter(corresponding_account__uniq_id = account_id).\
        select_related('corresponding_account').afirst()
    
    if not card_with_acc:
        await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_CARDS)
        error_flag = True
    
    return (card_with_acc, error_flag)
    

async def get_bank_requisites_for_sender(context, chat_id, user_id):
    """
    Checks whether this sending account has any Cards and Payment account.
    Returns Card with linked Payment Account (or None) and sending_requisites_error flag.
    ----------
    :param context: context object
    :param chat_id: Telegram User chat_id
    :param user_id: Telegram User ID

    :return: Tuple(card_with_acc_option, sending_requisites_error)
    """
    error_flag = False
    card_with_acc_opt = await Card.objects.\
        filter(corresponding_account__owner__tlg_id = user_id).\
        select_related('corresponding_account').afirst()

    if not card_with_acc_opt:
        await context.bot.send_message(chat_id=chat_id, text=SENDER_RESTRICTION)
        error_flag = True
    
    return (card_with_acc_opt, error_flag)


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
            return await get_card_with_account_by_account_id(context, chat_id, account_opt.uniq_id)

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
        return await get_card_with_account_by_account_id(context, chat_id, account_id)
    
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
        card_with_acc = await get_card_with_related(card_id)

        if card_with_acc:
            return (card_with_acc, False)

        await context.bot.send_message(chat_id=chat_id, text=CARD_NOT_FOUND)
        return (None, True)

    return (None, True)


async def send_result_message_for_transaction_state(context, chat_id, user_id):
    """
    Tries to create list of transactions for the last month
    and send it to the user.
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID
    :param card_id: Recipient Card ID

    """
    transactions = await get_list_of_transactions_for_the_last_month(user_id)
    if transactions:
        await context.bot.send_message(
            chat_id=chat_id, text=get_result_message_for_transaction_state(transactions) 
        ) 
        return
    
    await context.bot.send_message(
        chat_id=chat_id, text=NO_TXS_FOR_LAST_MONTH
    )