from ninja.orm import create_schema
from app.models import User

UserSchema = create_schema(User, exclude=['phone_number'])