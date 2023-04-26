from django.contrib import admin

from app.internal.admin.account import PaymentAccountAdmin
from app.internal.admin.card import PaymentCardAdmin
from app.internal.admin.favourite import FavouriteAdmin
from app.internal.admin.transaction import Transaction
from app.internal.admin.user import TelegramUserAdmin

admin.site.site_title = "Backend course"
admin.site.site_header = "Backend course"
