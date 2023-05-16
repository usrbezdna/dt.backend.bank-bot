from datetime import date
from ninja import Schema

from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema

class CardSchema(Schema):

    uniq_id : int
    corresponding_account : AccountSchema
    expiration : date
