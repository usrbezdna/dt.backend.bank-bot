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
    
    def __str__(self) -> str:
        """
        Returns a human-readable representation of Telegram User
        """
        user_as_a_str = (
            f"Your Telegram ID: {self.tlg_id}\n"
            f"First name: {self.first_name}\n"
            f"Phone number: {self.phone_number}\n"
        )

        user_as_a_str += f"Last name: {self.last_name}\n" if self.last_name else "You don't have a last name\n"
        user_as_a_str += f"Username: {self.username}\n" if self.username else "Can't find your username\n"
        return user_as_a_str

class UserIn(UserSchema):
    pass
