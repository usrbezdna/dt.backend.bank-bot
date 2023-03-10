from django.contrib import admin

from app.internal.models.card import Card


@admin.register(Card)
class PaymentCardAdmin(admin.ModelAdmin):
    pass
