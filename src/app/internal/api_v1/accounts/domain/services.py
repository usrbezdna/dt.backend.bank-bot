from abc import ABC, abstractmethod
from typing import Optional, Tuple

from asgiref.sync import sync_to_async

from app.internal.api_v1.accounts.db.models import Account
from app.internal.api_v1.users.db.models import User


class IAccountRepository(ABC):
    @abstractmethod
    def get_account_by_id(self, uniq_id: int) -> Optional[Account]:
        pass

    @abstractmethod
    def get_account_by_owner(self, owner: User) -> Optional[Account]:
        pass

    @abstractmethod
    def get_owner_name_from_account_by_id(self, uniq_id: int) -> Tuple[str, str]:
        pass


class AccountService:
    def __init__(self, account_repo: IAccountRepository):
        self._account_repo = account_repo

    @sync_to_async
    def get_account_by_id(self, uniq_id: int) -> Optional[Account]:
        return self._account_repo.get_account_by_id(uniq_id=uniq_id)

    @sync_to_async
    def get_account_by_owner(self, owner: User) -> Optional[Account]:
        return self._account_repo.get_account_by_owner(owner=owner)

    @sync_to_async
    def get_owner_name_from_account_by_id(self, uniq_id: int) -> Tuple[str, str]:
        return self._account_repo.get_owner_name_from_account_by_id(uniq_id=uniq_id)
