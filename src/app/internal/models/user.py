from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    """
    This class defines a model of Telegram User.
    ----------
    Based on original Telegram representation:
    https://core.telegram.org/bots/api#user
    """

    tlg_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=32)

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, blank=True)

    phone_number = PhoneNumberField(blank=True)

    class Meta:
        """
        Model Metadata.
        ----------
        verbose_name will be visible in admin panel;
        """

        verbose_name = "TelegramUser"
        # db_table = 'telegram_users'

    def hasPhoneNumber(self) -> bool:
        """
        Returns True if this user has a phone number
        """
        return len(self.phone_number) > 0

    def __str__(self) -> str:
        """
        Returns a human-readable representation of Telegram User
        """
        user_as_a_str = (
            f"Your Telegram ID: {self.tlg_id}\n"
            f"Username: {self.username}\n"
            f"Phone number: {self.phone_number}\n"
            f"First name: {self.first_name}\n"
        )
        user_as_a_str += f"Last name: {self.last_name}\n" if self.last_name else "\nYou don't have a last name"
        return user_as_a_str
