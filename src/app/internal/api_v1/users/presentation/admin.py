from django.contrib import admin

from app.internal.api_v1.users.db.models import User


@admin.register(User)
class TelegramUserAdmin(admin.ModelAdmin):
    pass
