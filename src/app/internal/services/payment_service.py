import logging

from asgiref.sync import sync_to_async

from app.models import Account, Card
from .favourites_service import try_get_another_user

from app.internal.transport.bot.telegram_messages import (
    RSP_USER_WITH_NO_ACC, RSP_USER_WITH_NO_CARDS
)

logger = logging.getLogger("django.server")

@sync_to_async
def get_card_from_db(uniq_id):
    """
    Returns card value or None
    :param uniq_id: uniq_id of this card
    """
    return Card.objects.filter(uniq_id=uniq_id).first()


@sync_to_async
def get_account_from_db(uniq_id):
    """
    Returns account value or None
    :param uniq_id: uniq_id of this account
    """
    return Account.objects.filter(uniq_id=uniq_id).first()

@sync_to_async
def get_account_from_card(uniq_id):
    """
    Returns corresponding account for specified card.
    :param uniq_id: uniq_id of this card
    """
    return Card.objects.get(uniq_id=uniq_id).corresponding_account


@sync_to_async
def get_owner_from_account(uniq_id):
    """
    Returns owner of this payment Account.
    :param uniq_id: uniq_id of this account
    """
    return Account.objects.get(uniq_id=uniq_id).owner

@sync_to_async
def get_user_payment_account(user):
    """
    Returns Payment Account or None for this Telegram User 
    :param user: Telegram User object
    """
    return Account.objects.filter(owner=user).first()

@sync_to_async
def get_card_for_account(account):
    """
    This function returns first card (or None) for Payment Account
    :param account: Payment Account object
    """
    return Card.objects.filter(corresponding_account=account).first()


async def account_has_any_cards(context, chat_id, account):
    """
    Checks whether or not this account has any linked cards.
    Returns first card or None.
    :param account: Payment Account object
    """
    card = await get_card_for_account(account)
    if card:
        return card
    await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_CARDS)
    return None



async def try_get_recipient_card(context, chat_id, arg_user):
    """
    This function tries to get the recipient card for the transaction.
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID
    :param arg_user: Telegram username (or ID) / Card ID / Account ID

    :return: Tuple with Card object and error flag
    """

    recipient_user_opt, arg_error = await try_get_another_user(context, chat_id, arg_user)
    if arg_error:
        return (None, True)
    
    if recipient_user_opt:
        account = await get_user_payment_account(recipient_user_opt)

        if account:
            card_option = await account_has_any_cards(context, chat_id, account)
            return (card_option, False)

        await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_ACC)
        return (None, False)


    recipient_account_opt = await get_account_from_db(arg_user)

    if recipient_account_opt:
        card_option = await account_has_any_cards(context, chat_id, recipient_account_opt)
        return (card_option, False)
    

    recipient_card_opt = await get_card_from_db(arg_user)

    if recipient_card_opt:
        return (recipient_card_opt, False)
    

    return (None, False)

