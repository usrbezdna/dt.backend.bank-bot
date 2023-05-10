
import logging
from typing import Optional

from app.internal.api_v1.accounts.db.models import Account
from app.internal.api_v1.cards.db.models import Card
from app.internal.api_v1.users.db.models import User

from app.internal.api_v1.utils.domain.services import verified_phone_required

from app.internal.api_v1.users.domain.services import UserService
from app.internal.api_v1.cards.domain.services import CardService
from app.internal.api_v1.accounts.domain.services import AccountService
from app.internal.api_v1.favourites.domain.services import FavouriteService
from app.internal.api_v1.transactions.domain.services import TransactionService


from app.internal.api_v1.utils.presentation.bot.telegram_messages import (
    ABSENT_ID_NUMBER, BALANCE_NOT_FOUND, CARD_NOT_FOUND, ERROR_DURING_TRANSFER, 
    INCR_TX_VALUE, INSUF_BALANCE, NO_INTERACTED_USERS, NO_TXS_FOR_LAST_MONTH, RSP_NOT_FOUND, 
    RSP_USER_WITH_NO_ACC, RSP_USER_WITH_NO_CARDS, 
    SELF_TRANSFER_ERROR, SENDER_RESTRICTION, STATE_NOT_FOUND, 
    get_message_for_send_command, get_message_with_balance, get_result_message_for_list_interacted, get_result_message_for_transaction_state, get_successful_transfer_message
)


from app.internal.api_v1.favourites.presentation.bot.telegram_messages import NOT_VALID_ID_MSG


from app.internal.api_v1.favourites.db.exceptions import InvalidIDArgumentException
from app.internal.api_v1.users.db.exceptions import UserNotFoundException
from app.internal.api_v1.transactions.db.exceptions import InsufficientBalanceException, TransferException


from telegram import Update
from telegram.ext import ContextTypes


logger = logging.getLogger("django.server")
    

class TelegramPaymentHandlers:

    def __init__(
            self, 
            user_service : UserService,
            fav_service : FavouriteService,

            account_service : AccountService, 
            card_service : CardService, 

            tx_service : TransactionService
        ):

        self._user_service = user_service
        self._fav_service = fav_service

        self._account_service = account_service
        self._card_service = card_service

        self._tx_service = tx_service


    @verified_phone_required
    async def check_payable(self, update : Update, context : ContextTypes.DEFAULT_TYPE):
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
            obj_option : Optional[Card] = await self._card_service.\
                  get_card_with_related_account_by_card_id(uniq_id=uniq_id)
            
        else:
            obj_option : Optional[Account] = await self._account_service.\
                get_account_by_id(uniq_id=uniq_id)


        if obj_option and command == "/check_card":
            await context.bot.send_message(
                chat_id=chat_id, text=get_message_with_balance(obj_option.corresponding_account)
            )

        elif obj_option and command == "/check_account":
            await context.bot.send_message(chat_id=chat_id, text=get_message_with_balance(obj_option))

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=BALANCE_NOT_FOUND)
            logger.info(f"Card / account with ID {uniq_id} not found in DB")




    @verified_phone_required
    async def send_to(self, update : Update, context : ContextTypes.DEFAULT_TYPE):
        """
        Universal handler for all /send_to_{recip} commands.
        Allows transactions between Users.
        ----------

        :param update: recieved Update object
        :param context: context object
        """
        user_id, chat_id = update.effective_user.id, update.effective_chat.id
        command_data = update.message.text.split(" ")

        if len(command_data) != 3:
            await context.bot.send_message(chat_id=chat_id, text=get_message_for_send_command(command_data[0]))
            return

        arg_command, arg_user_or_id, arg_value = command_data

        if not arg_value.isdigit() or int(arg_value) <= 0:
            await context.bot.send_message(chat_id=chat_id, text=INCR_TX_VALUE)
            return

        value = int(arg_value)

        sender_card_with_acc_opt : Optional[Card] = await self._card_service.\
            get_card_with_related_account_by_account_owner_id(tlg_id=user_id)
        
        if sender_card_with_acc_opt is None:
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

        sending_payment_account : Account = sender_card_with_acc_opt.corresponding_account
        recipient_payment_account : Account = recip_card_with_acc_opt.corresponding_account

        if recipient_payment_account == sending_payment_account:
            await context.bot.send_message(chat_id=chat_id, text=SELF_TRANSFER_ERROR)
            return

        try: 
            await self._tx_service.\
                try_transfer_to(sending_payment_account, recipient_payment_account, value)
            
        except InsufficientBalanceException:   
            await context.bot.send_message(chat_id=chat_id, text=INSUF_BALANCE) 
            return
        
        except TransferException:
            await context.bot.send_message(chat_id=chat_id, text=ERROR_DURING_TRANSFER)
            return


        recipient_name_as_tuple = await self._account_service.\
            get_owner_name_from_account_by_id(recipient_payment_account.uniq_id)
        
        recipient_name = " ".join(recipient_name_as_tuple)

        await context.bot.send_message(
            chat_id=chat_id, text=get_successful_transfer_message(recipient_name, value)
        )



    @verified_phone_required
    async def list_inter(self, update : Update, context : ContextTypes.DEFAULT_TYPE):
        """
        Handler for /list_inter command.
        Returns list of users this user have interacted with.
        Or returns empty list if user have no payment transactions.
        ----------

        :param update: recieved Update object
        :param context: context object
        """

        user_id, chat_id = update.effective_user.id, update.effective_chat.id
        usernames = await self._tx_service.\
            get_list_of_inter_usernames(user_id)

        if usernames:
            await context.bot.send_message(chat_id=chat_id, text=get_result_message_for_list_interacted(usernames))
            return
        
        await context.bot.send_message(chat_id=chat_id, text=NO_INTERACTED_USERS)



    @verified_phone_required
    async def state_payable(self, update : Update, context : ContextTypes.DEFAULT_TYPE):
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
            obj_option : Optional[Card] = await self._card_service.\
                get_card_with_related_account_by_card_id(uniq_id)
        else:
            obj_option : Optional[Account] = await self._account_service.\
                get_account_by_id(uniq_id)


        if obj_option and command == "/state_card":
            owner_id = obj_option.corresponding_account.owner.tlg_id
            await self.send_result_message_for_transaction_state(context, chat_id, owner_id)

        elif obj_option and command == "/state_account":
            owner_id = obj_option.owner.tlg_id
            await self.send_result_message_for_transaction_state(context, chat_id, owner_id)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=STATE_NOT_FOUND)
            logger.info(f"Card / account with ID {uniq_id} not found in DB")



    
    async def send_result_message_for_transaction_state(
            self, 
            context : ContextTypes.DEFAULT_TYPE,

            chat_id : int, 
            user_id : int
        ):

        """
        Sublogic handler for /state_payable. Tries to create list of transactions 
        for the last month and send it to the user.
        ----------

        :param context: context object
        :param chat_id: Telegram Chat ID
        :param card_id: Recipient Card ID
        """
        transactions = await self._tx_service.\
            get_list_of_transactions_for_the_last_month(user_id)
        
        if transactions:
            await context.bot.send_message(
                chat_id=chat_id, text=get_result_message_for_transaction_state(transactions)
            )
            return
        
        await context.bot.send_message(chat_id=chat_id, text=NO_TXS_FOR_LAST_MONTH) 


    async def handle_case_with_send_to_user(
            self, 
            context : ContextTypes.DEFAULT_TYPE, 

            chat_id : int, 
            arg_user_or_id: int

        ) -> Optional[Card]:

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
            another_user : User = await self._fav_service.\
                get_another_user(arg_user_or_id)
            
        except InvalidIDArgumentException:
            await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
            return None
        
        except UserNotFoundException:
            await context.bot.send_message(chat_id=chat_id, text=RSP_NOT_FOUND)
            return None


        account_opt = await self._account_service.\
            get_account_by_owner(another_user)
        
        if account_opt is None:
            await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_ACC)
            return None

        card_opt = await self._card_service.\
            get_card_with_related_account_by_account_id(account_opt.uniq_id)

        
        if card_opt is None:
            await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_CARDS)
            return None

        return card_opt
    

    async def handle_case_with_send_to_account(
            self, 
            context : ContextTypes.DEFAULT_TYPE, 

            chat_id : int, 
            account_id : int

        ) -> Optional[Card]:
        
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
        
        card_opt = await self._card_service.\
            get_card_with_related_account_by_account_id(account_id)

        if card_opt is None:
            await context.bot.send_message(chat_id=chat_id, text=RSP_USER_WITH_NO_CARDS)
            return None
        
        return card_opt
    

    async def handle_case_with_send_to_card(
            self, 
            context : ContextTypes.DEFAULT_TYPE, 

            chat_id : int, 
            card_id : int

        ) -> Optional[Card]:

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

        card_with_acc = await self._card_service.\
            get_card_with_related_account_by_card_id(card_id)

        if card_with_acc is None:
            await context.bot.send_message(chat_id=chat_id, text=CARD_NOT_FOUND)
            return None

        return card_with_acc