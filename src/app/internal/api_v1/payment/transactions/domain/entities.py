from datetime import datetime

from ninja import Schema

from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema
from app.internal.api_v1.utils.s3.domain.entities import RemoteImageSchema


class TransactionSchema(Schema):
    tx_id: int
    tx_timestamp: datetime

    tx_sender: AccountSchema
    tx_recip: AccountSchema

    tx_value: float
    tx_image : RemoteImageSchema

