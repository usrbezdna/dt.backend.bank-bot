import calendar
import logging
from datetime import timedelta
from typing import Any, Dict, List

from django.db import DatabaseError, transaction
from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat, ExtractDay, ExtractMonth, ExtractYear
from django.utils import timezone

from app.internal.api_v1.payment.accounts.db.models import Account
from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema
from app.internal.api_v1.payment.transactions.db.exceptions import InsufficientBalanceException, TransferException
from app.internal.api_v1.payment.transactions.db.models import Transaction
from app.internal.api_v1.payment.transactions.domain.services import ITransactionRepository
from app.internal.api_v1.users.db.models import User

from app.internal.api_v1.utils.s3.db.models import RemoteImage
from django.core.files.images import ImageFile


logger = logging.getLogger("django.server")


class TransactionRepository(ITransactionRepository):
    def try_transfer_to(
        self, sender_acc: AccountSchema, recipient_acc: AccountSchema, transferring_value: float, image_file : ImageFile
    ) -> None:
        """
        Tries to transfer value from first_payment_account to second_payment_account.
        Saves each Payment Transaction or raises exceptions if something went wrong.
        ----------

        :param first_payment_acc, second_payment_acc: payment Accounts
        :value: transferring value

        :raises InsufficientBalanceException: if sender_acc balance was insufficient
        :raises TransferException: if something went wrong in transaction block
        """
        sender_acc_model = Account.objects.get(pk=sender_acc.uniq_id)
        recipient_acc_model = Account.objects.get(pk=recipient_acc.uniq_id)

        try:
            Account.objects.select_for_update().filter(uniq_id__in=[sender_acc_model.uniq_id, sender_acc_model.uniq_id])

            with transaction.atomic():
                if sender_acc_model.value - transferring_value >= 0:
                    sender_acc_model.value = F("value") - transferring_value
                    recipient_acc_model.value = F("value") + transferring_value

                    sender_acc_model.save()
                    recipient_acc_model.save()

                    tx_image = RemoteImage.objects.filter(content=image_file).first()
                    Transaction.objects.create(
                        tx_sender=sender_acc_model, tx_recip=recipient_acc_model, tx_value=transferring_value, tx_image=tx_image
                    )

                else:
                    logger.info(f"Balance of {sender_acc.uniq_id} was not sufficient for payment transaction")
                    raise InsufficientBalanceException()

        except DatabaseError as err:
            logger.info(f"Error during try_transfer_to call:\n{err}")
            raise TransferException

    def get_list_of_inter_usernames(self, user_id: int) -> List[str]:
        """
        Retuns list of usernames for users who have
        interacted with user_id
        ----------

        :param user_id: Telegram ID of specified user
        """

        tx_list = list(
            Transaction.objects.filter(Q(tx_sender__owner__tlg_id=user_id) | Q(tx_recip__owner__tlg_id=user_id))
            .order_by("tx_sender__owner__tlg_id", "tx_recip__owner__tlg_id")
            .distinct("tx_sender__owner__tlg_id", "tx_recip__owner__tlg_id")
            .values_list("tx_sender__owner", "tx_recip__owner")
        )

        unique_tx_list = [list(i) for i in set(frozenset(tx_tuple) for tx_tuple in tx_list)]
        unique_ids = [tuple[1] if tuple[0] == user_id else tuple[0] for tuple in unique_tx_list]

        return list(User.objects.filter(tlg_id__in=unique_ids).values_list("username", flat=True).all())

    def get_list_of_transactions_for_the_last_month(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Returns list of payment transactions for the last
        month for Telegram user with ID user_id
        ----------
        :param user_id: Telegram ID of specified user
        """

        today = timezone.now().date()

        number_of_days_in_month = calendar.monthrange(today.year, today.month)[1]
        some_day_a_month_ago = today - timedelta(days=number_of_days_in_month)

        tx_list = list(
            Transaction.objects.filter(
                Q(Q(tx_sender__owner__tlg_id=user_id) | Q(tx_recip__owner__tlg_id=user_id))
                & Q(tx_timestamp__gt=some_day_a_month_ago)
                & Q(tx_timestamp__lte=today + timedelta(days=1))
            )
            .annotate(
                date=Concat(
                    ExtractDay("tx_timestamp"),
                    Value("."),
                    ExtractMonth("tx_timestamp"),
                    Value("."),
                    ExtractYear("tx_timestamp"),
                    output_field=CharField(),
                ),
                sender_name=Concat(
                    "tx_sender__owner__first_name", Value(" "), "tx_sender__owner__last_name", output_field=CharField()
                ),
                recip_name=Concat(
                    "tx_recip__owner__first_name", Value(" "), "tx_recip__owner__last_name", output_field=CharField()
                ),
            )
            .values("tx_id", "tx_value", "sender_name", "recip_name", "date")
        )

        return tx_list
