from ninja import Schema


class MessageResponseSchema(Schema):
    message: str

    @staticmethod
    def create(msg: str):
        return MessageResponseSchema(message=msg)


class UserSchema(Schema):
    tlg_id : int
    username : str
    first_name : str
    last_name : str
    phone_number : str

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
