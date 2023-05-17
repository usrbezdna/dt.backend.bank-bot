from django.contrib import admin

from app.internal.api_v1.favourites.db.models import Favourite


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    pass
