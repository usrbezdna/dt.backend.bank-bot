from typing import Optional

from app.internal.api_v1.payment.cards.db.exceptions import CardNotFoundException
from app.internal.api_v1.payment.cards.db.models import Card
from app.internal.api_v1.payment.cards.domain.entities import CardSchema
from app.internal.api_v1.payment.cards.domain.services import ICardRepository


class CardRepository(ICardRepository):
    def get_card_with_related_account_by_card_id(self, uniq_id: int) -> CardSchema:
        """
        Returns Card with card_uniq_id or raises CardNotFoundException.
        Also makes a foreign-key selection of corresponding account.
        :param uniq_id: uniq_id of this Card
        """
        card_with_acc_option = (
            Card.objects.filter(uniq_id=uniq_id).select_related("corresponding_account__owner").first()
        )

        if card_with_acc_option is None:
            raise CardNotFoundException()

        return CardSchema.from_orm(card_with_acc_option)

    def get_card_with_related_account_by_account_owner_id(self, tlg_id: int) -> CardSchema:
        """
        Returns Card with corresponding Accound owner with tlg_id or raises CardNotFoundException..
        :param tlg_id: Telegram ID of corresponding Accound owner
        """
        card_with_acc_option = (
            Card.objects.filter(corresponding_account__owner__tlg_id=tlg_id)
            .select_related("corresponding_account")
            .first()
        )

        if card_with_acc_option is None:
            raise CardNotFoundException()

        return CardSchema.from_orm(card_with_acc_option)

    def get_card_with_related_account_by_account_id(self, uniq_id: int) -> CardSchema:
        """
        Checks whether or not Account with uniq_id has any linked cards.
        Returns first Card with linked Account or raises CardNotFoundException.
        ----------
        :param uniq_id: Account uniq_id
        """
        card_with_acc_option = (
            Card.objects.filter(corresponding_account__uniq_id=uniq_id).select_related("corresponding_account").first()
        )

        if card_with_acc_option is None:
            raise CardNotFoundException()

        return CardSchema.from_orm(card_with_acc_option)
