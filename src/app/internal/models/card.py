from django.db import models

from .account import Account
from .payable import Payable


class Card(Payable):
    """
    Card model, inherits from abstract Payable.
    """

    corresponding_account = models.ForeignKey(Account, on_delete=models.CASCADE)

    expiration = models.DateField()

    class Meta:
        """
        Card metadata
        """

        verbose_name = "Card"
        db_table = "payment_cards"
