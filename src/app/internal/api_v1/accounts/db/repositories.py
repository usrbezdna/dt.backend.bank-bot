import logging
from typing import Optional, Tuple

from app.internal.api_v1.accounts.db.models import Account
from app.internal.api_v1.accounts.domain.services import IAccountRepository
from app.internal.api_v1.users.db.models import User

logger = logging.getLogger("django.server")


class AccountRepository(IAccountRepository):
    def get_account_by_id(self, uniq_id: int) -> Optional[Account]:
        """
        Returns Account with provided uniq_id or None.
        :param uniq_id: uniq_id of this Account
        """
        return Account.objects.filter(uniq_id=uniq_id).select_related("owner").first()

    def get_account_by_owner(self, owner: User) -> Optional[Account]:
        """
        Returns Payment Account or None for this Telegram User
        :param user: Telegram User object
        """
        return Account.objects.filter(owner=owner).first()

    def get_owner_name_from_account_by_id(self, uniq_id: int) -> Tuple[str, str]:
        """
        Returns owner of this payment Account.
        :param uniq_id: uniq_id of this Account
        """
        return Account.objects.values_list("owner__first_name", "owner__last_name").get(pk=uniq_id)
