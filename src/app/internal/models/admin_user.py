from django.contrib.auth.models import AbstractUser


class AdminUser(AbstractUser):
    pass

    class Meta:
        """
        DB User Metadata
        """

        verbose_name = "DB User"
