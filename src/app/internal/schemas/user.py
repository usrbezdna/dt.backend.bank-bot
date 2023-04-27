from ninja.orm import create_schema

from app.models import User

UserSchema = create_schema(
    User,
    fields=[
        'tlg_id', 'username', 
        'first_name', 'last_name',
        'phone_number'
    ]
)
