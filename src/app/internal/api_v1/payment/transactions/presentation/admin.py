from django.contrib import admin

from app.internal.api_v1.payment.transactions.db.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
