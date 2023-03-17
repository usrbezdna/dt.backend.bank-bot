from django.db import models

from app.internal.models.user import User


class Payable(models.Model):
    """
    Abstract Payable Model.
    ----------
    It includes common logic and atributes for
    Card and Account models.
    """

    CURRENCY_CHOICES = [
        ("USD", "United States dollar"),
        ("EUR", "Euro"),
        ("GBP", "British pound"),
        ("TRY", "Turkish lira"),
        ("RUB", "Russian ruble"),
    ]

    uniq_id = models.CharField(primary_key=True, max_length=20)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)

    value = models.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        abstract = True
