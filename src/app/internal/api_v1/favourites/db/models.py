from django.db import models

from app.internal.api_v1.users.db.models import User


class Favourite(models.Model):
    """
    Model for the list of favourite users.
    """

    tlg_id = models.IntegerField(primary_key=True)
    favourites = models.ManyToManyField(User, related_name="favs")

    class Meta:
        verbose_name = "Favourite"
        db_table = "fav_table"
