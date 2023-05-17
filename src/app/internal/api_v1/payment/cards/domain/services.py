from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from asgiref.sync import sync_to_async

from app.internal.api_v1.payment.cards.domain.entities import CardSchema


class ICardRepository(ABC):
    @abstractmethod
    def get_card_with_related_account_by_card_id(self, uniq_id: int) -> CardSchema:
        pass

    @abstractmethod
    def get_card_with_related_account_by_account_owner_id(self, tlg_id: int) -> CardSchema:
        pass

    @abstractmethod
    def get_card_with_related_account_by_account_id(self, uniq_id: int) -> CardSchema:
        pass


class CardService:
    def __init__(self, card_repo: ICardRepository):
        self._card_repo = card_repo

    @sync_to_async
    def aget_card_with_related_account_by_card_id(self, uniq_id: int) -> CardSchema:
        return self.get_card_with_related_account_by_card_id(uniq_id=uniq_id)

    def get_card_with_related_account_by_card_id(self, uniq_id: int) -> CardSchema:
        return self._card_repo.get_card_with_related_account_by_card_id(uniq_id=uniq_id)

    @sync_to_async
    def aget_card_with_related_account_by_account_owner_id(self, tlg_id: int) -> CardSchema:
        return self.get_card_with_related_account_by_account_owner_id(tlg_id=tlg_id)

    def get_card_with_related_account_by_account_owner_id(self, tlg_id: int) -> CardSchema:
        return self._card_repo.get_card_with_related_account_by_account_owner_id(tlg_id=tlg_id)

    @sync_to_async
    def aget_card_with_related_account_by_account_id(self, uniq_id: int) -> CardSchema:
        return self.get_card_with_related_account_by_account_id(uniq_id=uniq_id)

    def get_card_with_related_account_by_account_id(self, uniq_id: int) -> CardSchema:
        return self._card_repo.get_card_with_related_account_by_account_id(uniq_id=uniq_id)
