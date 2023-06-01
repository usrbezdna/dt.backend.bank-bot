from django.db import models

from app.internal.api_v1.payment.accounts.db.models import Account
from app.internal.api_v1.utils.s3.db.models import RemoteImage


class Transaction(models.Model):
    """
    Model of payment transaction.
    """

    tx_id = models.AutoField(primary_key=True)
    tx_timestamp = models.DateTimeField(auto_now_add=True)

    tx_sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="sender")
    tx_recip = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="recip")
    tx_value = models.DecimalField(max_digits=19, decimal_places=2)

    tx_image = models.OneToOneField(
        RemoteImage, default=None, null=True, on_delete=models.SET_NULL, related_name="transaction"
    )
    already_shown_flag = models.BooleanField(default=False)

    class Meta:
        """
        Transaction metadata
        """

        ordering = ["tx_timestamp"]

        verbose_name = "Transaction"
        db_table = "payment_transactions"
