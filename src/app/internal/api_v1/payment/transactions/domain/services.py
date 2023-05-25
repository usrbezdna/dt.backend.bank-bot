from abc import ABC, abstractmethod
from typing import Any, Dict, List

from asgiref.sync import sync_to_async
from django.core.files.images import ImageFile

from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema


class ITransactionRepository(ABC):
    @abstractmethod
    def try_transfer_to(
        self, sender_acc: AccountSchema, recipient_acc: AccountSchema, transferring_value: float, image_file: ImageFile
    ) -> None:
        pass

    @abstractmethod
    def get_list_of_inter_usernames(self, user_id: int) -> List[str]:
        pass

    @abstractmethod
    def get_list_of_transactions_for_the_last_month(self, user_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_list_of_latest_unseen_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        pass


class TransactionService:
    def __init__(self, tx_repo: ITransactionRepository):
        self._tx_repo = tx_repo

    @sync_to_async
    def atry_transfer_to(
        self, sender_acc: AccountSchema, recipient_acc: AccountSchema, transferring_value: float, image_file: ImageFile
    ) -> None:
        self.try_transfer_to(
            sender_acc=sender_acc,
            recipient_acc=recipient_acc,
            transferring_value=transferring_value,
            image_file=image_file,
        )

    def try_transfer_to(
        self, sender_acc: AccountSchema, recipient_acc: AccountSchema, transferring_value: float, image_file: ImageFile
    ) -> None:
        self._tx_repo.try_transfer_to(
            sender_acc=sender_acc,
            recipient_acc=recipient_acc,
            transferring_value=transferring_value,
            image_file=image_file,
        )

    @sync_to_async
    def aget_list_of_inter_usernames(self, user_id: int) -> List[str]:
        return self.get_list_of_inter_usernames(user_id=user_id)

    def get_list_of_inter_usernames(self, user_id: int) -> List[str]:
        return self._tx_repo.get_list_of_inter_usernames(user_id=user_id)

    @sync_to_async
    def aget_list_of_transactions_for_the_last_month(self, user_id: int) -> List[Dict[str, Any]]:
        return self.get_list_of_transactions_for_the_last_month(user_id=user_id)

    def get_list_of_transactions_for_the_last_month(self, user_id: int) -> List[Dict[str, Any]]:
        return self._tx_repo.get_list_of_transactions_for_the_last_month(user_id=user_id)

    @sync_to_async
    def aget_list_of_latest_unseen_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        return self.get_list_of_latest_unseen_transactions(user_id=user_id)

    def get_list_of_latest_unseen_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        return self._tx_repo.get_list_of_latest_unseen_transactions(user_id=user_id)
