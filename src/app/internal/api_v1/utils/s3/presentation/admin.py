from django.contrib import admin

from app.internal.api_v1.utils.s3.db.models import RemoteImage


@admin.register(RemoteImage)
class RemoteImageAdmin(admin.ModelAdmin):
    pass
