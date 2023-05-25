import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from app.internal.api_v1.favourites.db.exceptions import InvalidIDArgumentException
from app.internal.api_v1.favourites.domain.services import FavouriteService
from app.internal.api_v1.favourites.presentation.bot.telegram_messages import NOT_VALID_ID_MSG
from app.internal.api_v1.payment.accounts.db.exceptions import AccountNotFoundException
from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema
from app.internal.api_v1.payment.accounts.domain.services import AccountService
from app.internal.api_v1.payment.cards.db.exceptions import CardNotFoundException
from app.internal.api_v1.payment.cards.domain.entities import CardSchema
from app.internal.api_v1.payment.cards.domain.services import CardService
from app.internal.api_v1.payment.presentation.bot.telegram_messages import (
    ABSENT_ID_NUMBER,
    BALANCE_NOT_FOUND,
    CARD_NOT_FOUND,
    ERROR_DURING_TRANSFER,
    INCR_TX_VALUE,
    INSUF_BALANCE,
    NO_INTERACTED_USERS,
    NO_LATEST_TXS,
    NO_TXS_FOR_LAST_MONTH,
    RSP_NOT_FOUND,
    RSP_RESTRICTION,
    SELF_TRANSFER_ERROR,
    SENDER_RESTRICTION,
    STATE_NOT_FOUND,
    get_message_for_send_command,
    get_message_with_balance,
    get_result_message_for_list_interacted,
    get_result_message_for_transaction_state,
    get_successful_transfer_message,
)
from app.internal.api_v1.payment.transactions.db.exceptions import InsufficientBalanceException, TransferException
from app.internal.api_v1.payment.transactions.domain.services import TransactionService
from app.internal.api_v1.users.db.exceptions import UserNotFoundException
from app.internal.api_v1.users.domain.entities import UserSchema
from app.internal.api_v1.users.domain.services import UserService
from app.internal.api_v1.utils.s3.domain.services import S3Service
from app.internal.api_v1.utils.telegram.domain.services import verified_phone_required
from django.core.files.images import ImageFile

logger = logging.getLogger("django_stdout")


class TelegramPaymentHandlers:
    def __init__(
        self,
        user_service: UserService,
        fav_service: FavouriteService,
        account_service: AccountService,
        card_service: CardService,
        tx_service: TransactionService,
        s3_service : S3Service
    ):
        self._user_service = user_service
        self._fav_service = fav_service

        self._account_service = account_service
        self._card_service = card_service

        self._tx_service = tx_service
        self._s3_service = s3_service

    @verified_phone_required
    async def check_payable(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /check_card and /check_account command
        Returns remaining value of specified Card or Account
        (error message is returned in case of card / account absence)
        ----------

        :param update: recieved Update object
        :param context: context object passed to the callback
        """
        chat_id = update.effective_chat.id
        command_data = update.message.text.split(" ")

        if len(command_data) != 2:
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_ID_NUMBER)
            return

        command, uniq_id = command_data[0], command_data[1]
        obj_option = None

        if not uniq_id.isdigit() or int(uniq_id) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return

        if command == "/check_card":
            try:
                obj_option: CardSchema = await self._card_service.aget_card_with_related_account_by_card_id(
                    uniq_id=uniq_id
                )

            except CardNotFoundException:
                logger.info(f"Card with ID {uniq_id} not found in DB")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=BALANCE_NOT_FOUND)
                return

        else:
            try:
                obj_option: AccountSchema = await self._account_service.aget_account_by_id(uniq_id=uniq_id)

            except AccountNotFoundException:
                logger.info(f"Account with ID {uniq_id} not found in DB")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=BALANCE_NOT_FOUND)
                return

        if command == "/check_card":
            await context.bot.send_message(
                chat_id=chat_id, text=get_message_with_balance(obj_option.corresponding_account)
            )

        elif command == "/check_account":
            await context.bot.send_message(chat_id=chat_id, text=get_message_with_balance(obj_option))

    @verified_phone_required
    async def state_payable(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /state_card and /state_account commands.

        Returns list of payment transaction for specified card or account for the last month.
        Or returns empty list if user have no payment transactions.
        ----------
        :param update: recieved Update object
        :param context: context object
        """

        chat_id = update.effective_chat.id
        command_data = update.message.text.split(" ")

        if len(command_data) != 2:
            await context.bot.send_message(chat_id=chat_id, text=ABSENT_ID_NUMBER)
            return

        command, uniq_id = command_data[0], command_data[1]
        obj_option = None

        if not uniq_id.isdigit() or int(uniq_id) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return

        if command == "/state_card":
            try:
                obj_option: CardSchema = await self._card_service.aget_card_with_related_account_by_card_id(uniq_id)

            except CardNotFoundException:
                logger.info(f"Card with ID {uniq_id} not found in DB")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=STATE_NOT_FOUND)
                return
        else:
            try:
                obj_option: AccountSchema = await self._account_service.aget_account_by_id(uniq_id)

            except AccountNotFoundException:
                logger.info(f"Account with ID {uniq_id} not found in DB")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=STATE_NOT_FOUND)
                return

        if command == "/state_card":
            owner_id = obj_option.corresponding_account.owner.tlg_id
            await self.send_result_message_for_transaction_state(context, chat_id, owner_id)

        elif command == "/state_account":
            owner_id = obj_option.owner.tlg_id
            await self.send_result_message_for_transaction_state(context, chat_id, owner_id)


    @verified_phone_required
    async def list_latest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /list_latest command.
        Returns latest unseen transactions with attached images.
        ----------

        :param update: recieved Update object
        :param context: context object  
        """
        user_id, chat_id = update.effective_user.id, update.effective_chat.id

        tx_list = await self._tx_service.aget_list_of_latest_unseen_transactions(user_id=user_id)
        if tx_list:
            for tx_data in tx_list:
                res_msg = ''
                res_msg += (
                    f"TX ID: {tx_data['tx_id']}, "
                + f"Sender: {tx_data['sender_name']}, "
                + f"Recipient: {tx_data['recip_name']}, "
                + f"Value: {tx_data['tx_value']}\n"
                )

                if tx_data['tx_image'] is not None:
                    image = await self._s3_service.aget_image_from_s3_bucket(image_id=tx_data['tx_image'])
                    await context.bot.send_photo(chat_id=chat_id, photo=image.content.read())

                await context.bot.send_message(chat_id=chat_id, text=res_msg)
            return
        await context.bot.send_message(chat_id=chat_id, text=NO_LATEST_TXS)
        


    @verified_phone_required
    async def list_inter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler for /list_inter command.
        Returns list of users this user have interacted with.
        Or returns empty list if user have no payment transactions.
        ----------

        :param update: recieved Update object
        :param context: context object
        """

        user_id, chat_id = update.effective_user.id, update.effective_chat.id
        usernames = await self._tx_service.aget_list_of_inter_usernames(user_id)

        if usernames:
            await context.bot.send_message(chat_id=chat_id, text=get_result_message_for_list_interacted(usernames))
            return

        await context.bot.send_message(chat_id=chat_id, text=NO_INTERACTED_USERS)

    @verified_phone_required
    async def send_to(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Universal handler for all /send_to_{recip} commands.
        Allows transactions between Users.
        ----------

        :param update: recieved Update object
        :param context: context object
        """
        user_id, chat_id = update.effective_user.id, update.effective_chat.id
        photo = update.message.photo
        if photo:
            command_data = update.message.caption.split(" ")
        else:
            command_data = update.message.text.split(" ")

        if len(command_data) != 3:
            await context.bot.send_message(chat_id=chat_id, text=get_message_for_send_command(command_data[0]))
            return

        arg_command, arg_user_or_id, arg_value = command_data

        if not arg_value.isdigit() or int(arg_value) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=INCR_TX_VALUE)
            return

        value = int(arg_value)

        try:
            sender_card_with_acc_opt: CardSchema = (
                await self._card_service.aget_card_with_related_account_by_account_owner_id(tlg_id=user_id)
            )

        except CardNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=SENDER_RESTRICTION)
            return

        match arg_command:
            case "/send_to_user":
                recip_card_with_acc_opt = await self.handle_case_with_send_to_user(context, chat_id, arg_user_or_id)

            case "/send_to_account":
                recip_card_with_acc_opt = await self.handle_case_with_send_to_account(context, chat_id, arg_user_or_id)

            case "/send_to_card":
                recip_card_with_acc_opt = await self.handle_case_with_send_to_card(context, chat_id, arg_user_or_id)

        if recip_card_with_acc_opt is None:
            return

        sending_payment_account: AccountSchema = sender_card_with_acc_opt.corresponding_account
        recipient_payment_account: AccountSchema = recip_card_with_acc_opt.corresponding_account

        if recipient_payment_account == sending_payment_account:
            await context.bot.send_message(chat_id=chat_id, text=SELF_TRANSFER_ERROR)
            return

        try:
            image_file = None
            if photo:
                image_file : ImageFile = await self._s3_service.aconvert_telegram_photo_to_image(update, context)

            await self._tx_service.\
                atry_transfer_to(sending_payment_account, recipient_payment_account, value, image_file)

        except InsufficientBalanceException:
            await context.bot.send_message(chat_id=chat_id, text=INSUF_BALANCE)
            return

        except TransferException:
            await context.bot.send_message(chat_id=chat_id, text=ERROR_DURING_TRANSFER)
            return

        recipient_name = await self._account_service.aget_full_owner_name_from_account_by_id(
            uniq_id=recipient_payment_account.uniq_id
        )

        await context.bot.send_message(chat_id=chat_id, text=get_successful_transfer_message(recipient_name, value))

    async def send_result_message_for_transaction_state(
        self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int
    ):
        """
        Sublogic handler for /state_payable. Tries to create list of transactions
        for the last month and send it to the user.
        ----------

        :param context: context object
        :param chat_id: Telegram Chat ID
        :param card_id: Recipient Card ID
        """
        transactions = await self._tx_service.aget_list_of_transactions_for_the_last_month(user_id)

        if transactions:
            for tx_data in transactions:
                res_msg = ""
                res_msg += (f"TX ID: {tx_data['tx_id']}, "
                    + f"Date: {tx_data['date']}, "
                    + f"Sender: {tx_data['sender_name']}, "
                    + f"Recipient: {tx_data['recip_name']}, "
                    + f"Value: {tx_data['tx_value']}\n"
                )
         
                if tx_data['tx_image'] is not None:
                    presigned_url = await self._s3_service.aget_presigned_url_for_image(tx_data['tx_image'])
                    res_msg += f'Url : {presigned_url}'

                await context.bot.send_message(chat_id=chat_id, text=res_msg)
            return
        await context.bot.send_message(chat_id=chat_id, text=NO_TXS_FOR_LAST_MONTH)

    async def handle_case_with_send_to_user(
        self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, arg_user_or_id: int
    ) -> Optional[CardSchema]:
        """
        Acts like sublogic handler. Tries to get recipient card for send_to_user case
        (Sender have specified another Telegram User as a recipient)
        ----------

        :param context: context object
        :param chat_id: Telegram Chat ID
        :param arg_user_or_id: Recipient Telegram username (or ID)

        :return: recipient Card or None
        """

        try:
            another_user: UserSchema = await self._fav_service.aget_another_user_by_arg(arg_user_or_id)

        except InvalidIDArgumentException:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return None

        except UserNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=RSP_NOT_FOUND)
            return None

        try:
            card_with_acc = await self._card_service.aget_card_with_related_account_by_account_owner_id(
                another_user.tlg_id
            )

            return card_with_acc

        except CardNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=RSP_RESTRICTION)
            return None

    async def handle_case_with_send_to_account(
        self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, account_id: int
    ) -> Optional[CardSchema]:
        """
        Sublogic handler. Tries to get recipient card for send_to_account case
        (Sender have specified recipient Account ID)
        ----------

        :param context: context object
        :param chat_id: Telegram Chat ID
        :param account_id: Recipient Payment Account ID

        :return: Card or None
        """
        if not account_id.isdigit() or int(account_id) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return None

        try:
            card_with_acc = await self._card_service.aget_card_with_related_account_by_account_id(account_id)
            return card_with_acc

        except CardNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=RSP_RESTRICTION)
            return None

    async def handle_case_with_send_to_card(
        self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, card_id: int
    ) -> Optional[CardSchema]:
        """
        Tries to get recipient card for send_to_card case
        (Sender have specified recipient Card ID)
        ----------

        :param context: context object
        :param chat_id: Telegram Chat ID
        :param card_id: Recipient Card ID

        :return: Tuple with Card object and error flag
        """
        if not card_id.isdigit() or int(card_id) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return None

        try:
            card_with_acc = await self._card_service.aget_card_with_related_account_by_card_id(card_id)
            return card_with_acc

        except CardNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=CARD_NOT_FOUND)
            return None
