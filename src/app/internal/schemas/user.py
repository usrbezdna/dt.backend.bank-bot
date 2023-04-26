from ninja.orm import create_schema
from app.models import User

UserSchema = create_schema(User, exclude=[
    'is_staff', 'is_superuser', 'is_active',
    'password', 'email', 'last_login', 'groups',
    'user_permissions', 'date_joined'
])