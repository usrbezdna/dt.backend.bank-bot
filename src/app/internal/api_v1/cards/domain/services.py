

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from app.internal.api_v1.accounts.db.models import Account
from app.internal.api_v1.users.db.models import User
from app.internal.api_v1.cards.db.models import Card


from asgiref.sync import sync_to_async

class ICardRepository(ABC):
    
    @abstractmethod
    def get_card_with_related_account_by_card_id(self, uniq_id : int) -> Optional[Card]:
        pass

    @abstractmethod
    def get_card_with_related_account_by_account_owner_id(self, tlg_id : int) -> Optional[Card]:
        pass

    @abstractmethod
    def get_card_with_related_account_by_account_id(self, uniq_id : int) -> Optional[Card]:
        pass

class CardService:

    def __init__(self, card_repo : ICardRepository):
        self._card_repo = card_repo


    @sync_to_async
    def get_card_with_related_account_by_card_id(self, uniq_id : int) -> Optional[Card]:
        return self._card_repo.get_card_with_related_account_by_card_id(uniq_id=uniq_id)
    

    @sync_to_async
    def get_card_with_related_account_by_account_owner_id(self, tlg_id : int) -> Optional[Card]:
        return self._card_repo.get_card_with_related_account_by_account_owner_id(tlg_id=tlg_id)
    
    @sync_to_async
    def get_card_with_related_account_by_account_id(self, uniq_id : int) -> Optional[Card]:
        return self._card_repo.get_card_with_related_account_by_account_id(uniq_id=uniq_id)