from abc import ABC, abstractmethod
from typing import Optional, Tuple

from asgiref.sync import sync_to_async

from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema
from app.internal.api_v1.utils.monitoring.metrics.presentation.handlers import PrometheusMetrics


class IAccountRepository(ABC):
    @abstractmethod
    def get_account_by_id(self, uniq_id: int) -> AccountSchema:
        pass

    @abstractmethod
    def get_full_owner_name_from_account_by_id(self, uniq_id: int) -> str:
        pass

    @abstractmethod
    def get_current_number_of_accounts(self) -> int:
        pass


class AccountService:
    def __init__(self, account_repo: IAccountRepository):
        self._account_repo = account_repo

    @sync_to_async
    def aget_account_by_id(self, uniq_id: int) -> AccountSchema:
        return self.get_account_by_id(uniq_id=uniq_id)

    def get_account_by_id(self, uniq_id: int) -> AccountSchema:
        return self._account_repo.get_account_by_id(uniq_id=uniq_id)

    @sync_to_async
    def aget_full_owner_name_from_account_by_id(self, uniq_id: int) -> str:
        return self.get_full_owner_name_from_account_by_id(uniq_id=uniq_id)

    def get_full_owner_name_from_account_by_id(self, uniq_id: int) -> str:
        return self._account_repo.get_full_owner_name_from_account_by_id(uniq_id=uniq_id)

    @sync_to_async
    def aset_current_number_of_accounts_metric(self) -> int:
        PrometheusMetrics.set_accounts_number_gauge(self._account_repo.get_current_number_of_accounts())
