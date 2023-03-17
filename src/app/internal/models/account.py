from django.db import models

from .payable import Payable


class Account(Payable):
    """
    Account model, inherits from abstract Payable.
    """

    PERSON_CHOICES = [
        ("PER", "Person"),
        ("ENT", "Entity"),
    ]

    party = models.CharField(max_length=3, choices=PERSON_CHOICES)

    class Meta:
        """
        Account metadata
        """

        verbose_name = "Account"
        db_table = "payment_accounts"
