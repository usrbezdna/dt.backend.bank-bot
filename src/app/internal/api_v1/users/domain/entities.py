from ninja.orm import create_schema
from app.internal.api_v1.users.db.models import User


UserSchema = create_schema(
    User,
    fields=[
        'tlg_id', 'username', 
        'first_name', 'last_name',
        'phone_number'
    ]
)

class UserOut(UserSchema):
    pass

class UserIn(UserSchema):
    pass
