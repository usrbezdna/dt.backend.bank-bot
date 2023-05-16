from abc import ABC, abstractmethod
from typing import Any

from asgiref.sync import sync_to_async
from telegram import User as TelegramUser

from app.internal.api_v1.users.domain.entities import UserSchema


class IUserRepository(ABC):
    @abstractmethod
    def get_user_by_id(self, tlg_id: int) -> UserSchema:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> UserSchema:
        pass

    @abstractmethod
    def get_user_field_by_id(self, tlg_id: int, field_name: str) -> Any:
        pass

    @abstractmethod
    def update_user_phone_number(self, tlg_id: int, new_phone_number: str) -> None:
        pass

    @abstractmethod
    def update_user_password(self, tlg_id: int, new_password: str) -> None:
        pass

    @abstractmethod
    def save_telegram_user_to_db(self, tlg_user: TelegramUser) -> None:
        pass


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    @sync_to_async
    def aget_user_by_id(self, tlg_id: int) -> UserSchema:
        return self.get_user_by_id(tlg_id=tlg_id)

    def get_user_by_id(self, tlg_id: int) -> UserSchema:
        return self._user_repo.get_user_by_id(tlg_id=tlg_id)

    @sync_to_async
    def aget_user_by_username(self, username: str) -> UserSchema:
        return self.get_user_by_username(username=username)

    def get_user_by_username(self, username: str) -> UserSchema:
        return self._user_repo.get_user_by_username(username=username)

    @sync_to_async
    def aget_user_field_by_id(self, tlg_id: int, field_name: str) -> Any:
        return self.get_user_field_by_id(tlg_id=tlg_id, field_name=field_name)

    def get_user_field_by_id(self, tlg_id: int, field_name: str) -> Any:
        return self._user_repo.get_user_field_by_id(tlg_id=tlg_id, field_name=field_name)

    @sync_to_async
    def aupdate_user_phone_number(self, tlg_id: int, new_phone_number: str) -> None:
        self.update_user_phone_number(tlg_id=tlg_id, new_phone_number=new_phone_number)

    def update_user_phone_number(self, tlg_id: int, new_phone_number: str) -> None:
        self._user_repo.update_user_phone_number(tlg_id=tlg_id, new_phone_number=new_phone_number)

    @sync_to_async
    def aupdate_user_password(self, tlg_id: int, new_password: str) -> None:
        self.update_user_password(tlg_id=tlg_id, new_password=new_password)

    def update_user_password(self, tlg_id: int, new_password: str) -> None:
        self._user_repo.update_user_password(tlg_id=tlg_id, new_password=new_password)

    @sync_to_async
    def asave_telegram_user_to_db(self, tlg_user: TelegramUser) -> None:
        self.save_telegram_user_to_db(tlg_user=tlg_user)

    def save_telegram_user_to_db(self, tlg_user: TelegramUser) -> None:
        self._user_repo.save_telegram_user_to_db(tlg_user=tlg_user)
