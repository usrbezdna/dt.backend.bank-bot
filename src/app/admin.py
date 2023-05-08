from django.contrib import admin

from app.internal.api_v1.accounts.presentation.admin import PaymentAccountAdmin
from app.internal.api_v1.cards.presentation.admin import PaymentCardAdmin
from app.internal.api_v1.favourites.presentation.admin import FavouriteAdmin
from app.internal.api_v1.transactions.presentation.admin import Transaction
from app.internal.api_v1.users.presentation.admin import TelegramUserAdmin

admin.site.site_title = "Backend course"
admin.site.site_header = "Backend course"
