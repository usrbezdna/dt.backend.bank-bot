import logging
from typing import Optional

from app.internal.api_v1.payment.accounts.domain.services import IAccountRepository
from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema

from app.internal.api_v1.payment.accounts.db.models import Account 
from app.internal.api_v1.payment.accounts.db.exceptions import AccountNotFoundException


logger = logging.getLogger("django.server")


class AccountRepository(IAccountRepository):

    def get_account_by_id(self, uniq_id: int) -> AccountSchema:
        """
        Returns Account with provided uniq_id or raises AccountNotFoundException.
        :param uniq_id: uniq_id of this Account
        """ 
        account_option = Account.objects.\
            filter(uniq_id=uniq_id).\
            select_related("owner").\
            first()
        
        if account_option is None:
            raise AccountNotFoundException()

        return AccountSchema.from_orm(account_option)


    def get_full_owner_name_from_account_by_id(self, uniq_id: int) -> str:
        """
        Returns owner of this payment Account or raises AccountNotFoundException.
        :param uniq_id: uniq_id of this Account
        """
        name_as_tuple_option = Account.objects.\
            values_list("owner__first_name", "owner__last_name").\
            filter(uniq_id=uniq_id).\
            first()
        
        if name_as_tuple_option is None:
            raise AccountNotFoundException()

        return " ".join(name_as_tuple_option)
