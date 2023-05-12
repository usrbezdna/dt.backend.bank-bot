from django.db import models

from app.internal.api_v1.accounts.db.models import Account


class Card(models.Model):
    """
    Card model.

    """

    uniq_id = models.CharField(primary_key=True, max_length=20)
    corresponding_account = models.ForeignKey(Account, on_delete=models.CASCADE)

    expiration = models.DateField()

    class Meta:
        """
        Card metadata
        """

        verbose_name = "Card"
        db_table = "payment_cards"
