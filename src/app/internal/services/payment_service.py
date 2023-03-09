
from asgiref.sync import sync_to_async
import logging

from app.models import Card, Account

logger = logging.getLogger("django.server")

@sync_to_async
def get_card_value(uniq_id):
    """
    Returns card value or None
    :param uniq_id: uniq_id of this card
    """

    card_option = Card.objects.filter(uniq_id=uniq_id)
    if card_option.exists():
        return card_option[0].value
    return None


@sync_to_async
def get_account_value(uniq_id):
    """
    Returns account value or None
    :param uniq_id: uniq_id of this account
    """
    
    acc_option = Account.objects.filter(uniq_id=uniq_id)
    if acc_option.exists():
        return acc_option[0].value
    return None