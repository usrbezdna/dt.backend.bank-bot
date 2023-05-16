from django.db import models

from app.internal.api_v1.payment.accounts.db.models import Account


class Card(models.Model):
    """
    Card model.

    """

    uniq_id = models.IntegerField(primary_key=True)
    corresponding_account = models.ForeignKey(Account, on_delete=models.CASCADE)

    expiration = models.DateField()

    class Meta:
        """
        Card metadata
        """

        verbose_name = "Card"
        db_table = "payment_cards"
