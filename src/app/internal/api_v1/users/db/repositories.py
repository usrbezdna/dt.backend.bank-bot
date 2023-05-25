import logging
from typing import Any, Optional

from telegram import User as TelegramUser

from app.internal.api_v1.users.db.exceptions import UserNotFoundException
from app.internal.api_v1.users.db.models import User
from app.internal.api_v1.users.domain.entities import UserSchema
from app.internal.api_v1.users.domain.services import IUserRepository

logger = logging.getLogger("django_stdout")


class UserRepository(IUserRepository):
    def get_user_by_id(self, tlg_id: int) -> UserSchema:
        """
        Returns Telegram user by ID from DB
        or raises UserNotFoundException (if user with such TgID doesn't exist)
        ----------

        :param tlg_id: Telegram user ID
        :return: User object
        :raises UserNotFoundException: if user not found in DB
        """
        user_option: Optional[User] = User.objects.filter(tlg_id=tlg_id).first()

        if user_option is None:
            logger.info(f"User with ID {tlg_id} not found in DB")
            raise UserNotFoundException("Can't find user with such ID")

        return UserSchema.from_orm(user_option)

    def get_user_by_username(self, username: str) -> UserSchema:
        """
        Returns Telegram user by username from DB
        or raises UserNotFoundException (if user with such username doesn't exist)
        ----------

        :param username: Telegram user username
        :return: User object
        :raises UserNotFoundException: if user not found in DB
        """
        user_option: Optional[User] = User.objects.filter(username=username).first()

        if user_option is None:
            logger.info(f"User with username {username} not found in DB")
            raise UserNotFoundException("Can't find user with such username")

        return UserSchema.from_orm(user_option)

    def get_user_field_by_id(self, tlg_id: int, field_name: str) -> Any:
        """
        Returns value of specified field
        for User with Telegram ID tlg_id
        ----------

        :param tlg_id: Telegram User ID
        :params field_name: wished model field
        :return: Value of this field
        """
        if not User.objects.filter(tlg_id=tlg_id).exists():
            raise UserNotFoundException("This user does not exist! Can't address to his fields")

        return User.objects.values_list(field_name, flat=True).get(pk=tlg_id)

    def update_user_phone_number(self, tlg_id: int, new_phone_number: str) -> None:
        """
        Updates phone number for a specific User.
        ----------

        :param tlg_id: Telegram ID of this User
        :param new_phone_number: already validated phone number
        """
        User.objects.filter(tlg_id=tlg_id).update(phone_number=new_phone_number)
        logger.info(f"Updated phone number for user with {tlg_id} ID")

    def update_user_password(self, tlg_id: int, new_password: str) -> None:
        """
        Updates password for a specific User.
        ----------

        :param tlg_id: Telegram ID of this User
        :param new_password: new password
        """
        user: User = User.objects.filter(tlg_id=tlg_id).first()
        user.set_password(new_password)

        user.save()
        logger.info(f"Updated password for user with ID {tlg_id}")

    def save_telegram_user_to_db(self, tlg_user: TelegramUser) -> None:
        """
        Receives Telegram user and saves it in DB.
        ----------

        :param user: TelegramUser object
        """
        user_model: User = User(
            tlg_id=tlg_user.id,
            username=tlg_user.username if tlg_user.username else "",
            first_name=tlg_user.first_name,
            last_name=tlg_user.last_name if tlg_user.last_name else "",
            phone_number="",
        )
        user_model.save()
        logger.info(f"User with {user_model.tlg_id} ID was successfully saved to DB")
