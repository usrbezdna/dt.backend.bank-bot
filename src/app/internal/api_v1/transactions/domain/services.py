

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.internal.api_v1.accounts.db.models import Account

from asgiref.sync import sync_to_async


class ITransactionRepository(ABC):

    @abstractmethod
    def try_transfer_to(self, sender_acc : Account, recipient_acc : Account, transferring_value : float) -> None: 
        pass

    @abstractmethod
    def get_list_of_inter_usernames(self, user_id : int) -> List[str]:
        pass

    @abstractmethod
    def get_list_of_transactions_for_the_last_month(self, user_id : int) -> List[Dict[str, Any]]:
        pass


class TransactionService:

    def __init__(self, tx_repo : ITransactionRepository):
        self._tx_repo = tx_repo


    @sync_to_async
    def try_transfer_to(self, sender_acc : Account, recipient_acc : Account, transferring_value : float) -> None:
        self._tx_repo.try_transfer_to(sender_acc=sender_acc, recipient_acc=recipient_acc, transferring_value=transferring_value)

    @sync_to_async
    def get_list_of_inter_usernames(self, user_id : int) -> List[str]:
        return self._tx_repo.get_list_of_inter_usernames(user_id=user_id)
    
    @sync_to_async
    def get_list_of_transactions_for_the_last_month(self, user_id : int) -> List[Dict[str, Any]]:
        return self._tx_repo.get_list_of_transactions_for_the_last_month(user_id=user_id)