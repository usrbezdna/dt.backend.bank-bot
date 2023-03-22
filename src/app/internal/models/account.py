from django.db import models
from .user import User

class Account(models.Model):
    """
    Account model.
    
    """

    PERSON_CHOICES = [
        ("PER", "Person"),
        ("ENT", "Entity"),
    ]

    CURRENCY_CHOICES = [
        ("USD", "United States dollar"),
        ("EUR", "Euro"),
        ("GBP", "British pound"),
        ("TRY", "Turkish lira"),
        ("RUB", "Russian ruble"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    uniq_id = models.CharField(primary_key=True, max_length=40)
    party = models.CharField(max_length=3, choices=PERSON_CHOICES)

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    value = models.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        """
        Account metadata
        """

        verbose_name = "Account"
        db_table = "payment_accounts"
