
from asgiref.sync import sync_to_async
import logging

from app.models import Card, Account

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