from django.contrib import admin
from app.internal.api_v1.cards.db.models import Card


@admin.register(Card)
class PaymentCardAdmin(admin.ModelAdmin):
    pass
