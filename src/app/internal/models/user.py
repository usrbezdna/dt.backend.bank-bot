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
        verbose_name = 'TelegramUser'


    def hasPhoneNumber(self) -> bool:
        """
        Returns True if this user has a phone number
        """
        return len(self.phone_number) > 0