from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    This class represents my custom User manager
    with overrided create_user and create_superuser
    methods.
    """

    def _create_base_user(self, tlg_id, password, **extra_fields):
        """
        Creates user with basic fields set.
        """
        if not tlg_id:
            raise ValueError("Telegram ID acts like PK and must be set")

        user = self.model(tlg_id=tlg_id, **extra_fields)
        user.set_password(password)

        user.save()
        return user

    def create_user(self, tlg_id, password=None, **extra_fields):
        """
        Creates normal user
        """
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)

        return self._create_base_user(tlg_id, password, **extra_fields)

    def create_superuser(self, tlg_id, password, **extra_fields):
        """
        Creates superuser
        """

        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("is_superser must be set to True")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("is_staff must be also set to True")

        return self._create_base_user(tlg_id, password, **extra_fields)


class User(AbstractUser):
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

    phone_number = models.CharField(max_length=32, blank=True)

    USERNAME_FIELD = "tlg_id"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        """
        Model Metadata.
        ----------
        verbose_name will be visible in admin panel;
        """

        verbose_name = "TelegramUser"

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
            f"First name: {self.first_name}\n"
            f"Phone number: {self.phone_number}\n"
        )

        user_as_a_str += f"Last name: {self.last_name}\n" if self.last_name else "You don't have a last name\n"
        user_as_a_str += f"Username: {self.username}\n" if self.username else "Can't find your username\n"
        return user_as_a_str