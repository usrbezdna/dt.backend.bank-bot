from django.contrib import admin

from app.internal.models.user import User


@admin.register(User)
class TelegramUserAdmin(admin.ModelAdmin):
    pass