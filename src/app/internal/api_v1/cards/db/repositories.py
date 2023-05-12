from typing import Optional

from app.internal.api_v1.cards.db.models import Card
from app.internal.api_v1.cards.domain.services import ICardRepository


class CardRepository(ICardRepository):
    def get_card_with_related_account_by_card_id(self, uniq_id: int) -> Optional[Card]:
        """
        Returns Card with card_uniq_id or None.
        Also makes a foreign-key selection of corresponding account.
        :param uniq_id: uniq_id of this Card
        """
        return Card.objects.filter(uniq_id=uniq_id).select_related("corresponding_account__owner").first()

    def get_card_with_related_account_by_account_owner_id(self, tlg_id: int) -> Optional[Card]:
        """
        Returns Card with corresponding Accound owner with tlg_id or None.
        :param tlg_id: Telegram ID of corresponding Accound owner
        """
        return (
            Card.objects.filter(corresponding_account__owner__tlg_id=tlg_id)
            .select_related("corresponding_account")
            .first()
        )

    def get_card_with_related_account_by_account_id(self, uniq_id: int) -> Optional[Card]:
        """
        Checks whether or not Account with uniq_id has any linked cards.
        Returns first Card with linked Account or None.
        ----------
        :param uniq_id: Account uniq_id
        """
        return (
            Card.objects.filter(corresponding_account__uniq_id=uniq_id).select_related("corresponding_account").first()
        )
