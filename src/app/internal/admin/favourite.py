from django.contrib import admin

from app.internal.models.favourite import Favourite


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    pass
