
from ninja_extra import NinjaExtraAPI
from .db.repositories import UserRepository

def create_users_api(main_api : NinjaExtraAPI) -> None:

    user_repo = UserRepository()