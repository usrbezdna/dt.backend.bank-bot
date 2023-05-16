from ninja import Schema
from app.internal.api_v1.users.domain.entities import UserSchema


class AccountSchema(Schema):
    uniq_id : int
    value : float
    
    currency : str = None
    party : str = None

    owner : UserSchema
