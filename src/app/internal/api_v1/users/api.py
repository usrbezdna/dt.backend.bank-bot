
from ninja_extra import NinjaExtraAPI

from app.internal.api_v1.users.db.repositories import UserRepository
from app.internal.api_v1.users.domain.services import UserService

from app.internal.api_v1.users.presentation.rest.handlers import RestUserHandlers
from app.internal.api_v1.users.presentation.rest.routers import get_users_router


def register_users_api(global_api: NinjaExtraAPI):
    """
    Builds User part of REST APi and 
    attaches routers to global Ninja API 
    """

    user_repo = UserRepository()
    user_service = UserService(user_repo=user_repo)

    rest_user_handlers = RestUserHandlers(user_service=user_service)
    user_router = get_users_router(rest_user_handlers=rest_user_handlers)

    global_api.add_router("/users", user_router)