
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.internal.api_v1.favourites.db.repositories import FavouriteRepository
from app.internal.api_v1.favourites.domain.services import FavouriteService

from app.internal.api_v1.payment.accounts.db.repositories import AccountRepository
from app.internal.api_v1.payment.accounts.domain.services import AccountService

from app.internal.api_v1.payment.cards.db.repositories import CardRepository
from app.internal.api_v1.payment.cards.domain.services import CardService

from app.internal.api_v1.payment.presentation.bot.handlers import TelegramPaymentHandlers
from app.internal.api_v1.payment.transactions.db.repositories import TransactionRepository
from app.internal.api_v1.payment.transactions.domain.services import TransactionService

from app.internal.api_v1.users.db.repositories import UserRepository
from app.internal.api_v1.users.domain.services import UserService

from app.internal.api_v1.utils.s3.db.repositories import S3Repository
from app.internal.api_v1.utils.s3.domain.services import S3Service


def register_telegram_payment_handlers(application: Application) -> None:
    """
    Registers handlers for payment part of Telegram bot
    """

    user_repo = UserRepository()
    user_service = UserService(user_repo=user_repo)

    fav_repo = FavouriteRepository(user_repo=user_repo)
    fav_service = FavouriteService(fav_repo=fav_repo)

    account_repo = AccountRepository()
    account_service = AccountService(account_repo=account_repo)

    card_repo = CardRepository()
    card_service = CardService(card_repo=card_repo)

    tx_repo = TransactionRepository()
    tx_service = TransactionService(tx_repo=tx_repo)

    s3_repo = S3Repository()
    s3_service = S3Service(s3_repo=s3_repo)

    payment_handlers = TelegramPaymentHandlers(
        user_service=user_service,
        fav_service=fav_service,
        account_service=account_service,
        card_service=card_service,
        tx_service=tx_service,
        s3_service=s3_service
    )

    application.add_handler(CommandHandler("check_card", payment_handlers.check_payable))
    application.add_handler(CommandHandler("check_account", payment_handlers.check_payable))

    application.add_handler(MessageHandler(
        filters.Regex(r'send_to_user') | filters.CaptionRegex(r"/send_to_user")
        | filters.Regex(r'send_to_account') | filters.CaptionRegex(r"/send_to_account")
        | filters.Regex(r'send_to_card') | filters.CaptionRegex(r"/send_to_card"),
        payment_handlers.send_to))

    application.add_handler(CommandHandler("list_inter", payment_handlers.list_inter))
    application.add_handler(CommandHandler("list_latest", payment_handlers.list_latest))

    application.add_handler(CommandHandler("state_card", payment_handlers.state_payable))
    application.add_handler(CommandHandler("state_account", payment_handlers.state_payable))
