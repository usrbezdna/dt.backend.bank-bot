from ninja_extra import NinjaExtraAPI

from app.internal.api_v1.favourites.db.repositories import FavouriteRepository
from app.internal.api_v1.favourites.domain.services import FavouriteService
from app.internal.api_v1.favourites.presentation.rest.handlers import RestFavouritesHandlers
from app.internal.api_v1.favourites.presentation.rest.routers import get_favourites_router
from app.internal.api_v1.users.db.repositories import UserRepository
from app.internal.api_v1.users.domain.services import UserService


def register_favourites_api(global_api: NinjaExtraAPI):
    """
    Builds Favourites part of REST APi and
    attaches routers to global Ninja API
    """

    user_repo = UserRepository()
    user_service = UserService(user_repo=user_repo)

    fav_repo = FavouriteRepository(user_repo=user_repo)
    fav_service = FavouriteService(fav_repo=fav_repo)

    rest_fav_handlers = RestFavouritesHandlers(fav_service=fav_service, user_service=user_service)

    fav_router = get_favourites_router(rest_fav_handlers=rest_fav_handlers)
    global_api.add_router("/favourites", fav_router)
