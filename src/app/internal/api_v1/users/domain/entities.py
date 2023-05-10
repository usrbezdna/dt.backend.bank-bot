from ninja import Schema

from ninja.orm import create_schema
from app.internal.api_v1.users.db.models import User


class MessageResponseSchema(Schema):
    message: str

    @staticmethod
    def create(msg: str):
        return MessageResponseSchema(message=msg)
    
    
UserSchema = create_schema(
    User,
    fields=[
        'tlg_id', 'username', 
        'first_name', 'last_name',
        'phone_number'
    ]
)