import asyncio
import logging
from typing import List

from app.internal.api_v1.favourites.db.exceptions import (
    FavouriteNotFoundException,
    InvalidIDArgumentException,
    SecondTimeAdditionException,
    UserNotInFavouritesException,
)
from app.internal.api_v1.favourites.domain.services import FavouriteService
from app.internal.api_v1.favourites.presentation.rest.content_messages import (
    ADDED_SUCCESS,
    DELETED_SUCCESS,
    FAV_USER_NOT_FOUND,
    FAVS_NOT_FOUND,
    INVALID_ID,
    NO_SECOND_TIME_ADDITION,
    NOT_IN_FAV,
    SELF_OPS_PROHIBITED,
)
from app.internal.api_v1.users.db.exceptions import UserNotFoundException
from app.internal.api_v1.users.domain.entities import MessageResponseSchema, UserSchema
from app.internal.api_v1.users.domain.services import UserService

logger = logging.getLogger("stdout_with_tlg")


class RestFavouritesHandlers:
    def __init__(self, fav_service: FavouriteService, user_service: UserService) -> None:
        self._fav_service = fav_service
        self._user_service = user_service

    def list_fav(self, request):
        """
        Returns list of favourite users
        """
        logger.info("Got new GET request on /api/favourites/list endpoint!")

        favs_limit = 5
        user_id = request.user.tlg_id

        try:
            favs_list: List[UserSchema] = self._fav_service.get_limited_list_of_favourites(
                tlg_id=user_id, favs_limit=favs_limit
            )

        except FavouriteNotFoundException:
            logger.info(f"Unable to find favourites for user with ID: {user_id}")
            return 404, MessageResponseSchema.create(FAVS_NOT_FOUND)

        if len(favs_list) == 0:
            logger.info("User has a favorite object, but don't have any favourites users included")
            return 404, MessageResponseSchema.create(FAVS_NOT_FOUND)

        return 200, favs_list

    def del_fav(self, request, tlg_id: int):
        """
        Deletes Telegram user with ID {tlg_id}
        from the favourites list of authenticated user
        """

        logger.info("Got new DELETE request on /api/favourites/list endpoint!")
        user_id = request.user.tlg_id

        try:
            another_user: UserSchema = self._user_service.get_user_by_id(tlg_id=tlg_id)

        except UserNotFoundException:
            return 404, MessageResponseSchema.create(FAV_USER_NOT_FOUND)

        if another_user.tlg_id == user_id:
            return 403, MessageResponseSchema.create(SELF_OPS_PROHIBITED)

        try:
            self._fav_service.try_del_fav_from_user(user_id, another_user)

        except UserNotInFavouritesException:
            return 403, MessageResponseSchema.create(NOT_IN_FAV)

        return 200, MessageResponseSchema.create(DELETED_SUCCESS)

    def add_fav(self, request, tlg_id: int):
        """
        Addes Telegram user with ID {tlg_id}
        to the favourites list of authenticated user
        """

        logger.info("Got new PUT request on /api/favourites/list endpoint!")
        user_id = request.user.tlg_id

        try:
            another_user: UserSchema = self._user_service.get_user_by_id(tlg_id=tlg_id)

        except UserNotFoundException:
            return 404, MessageResponseSchema.create(FAV_USER_NOT_FOUND)

        if another_user.tlg_id == user_id:
            return 403, MessageResponseSchema.create(SELF_OPS_PROHIBITED)

        try:
            self._fav_service.try_add_fav_to_user(user_id, another_user)

        except SecondTimeAdditionException:
            return 403, MessageResponseSchema.create(NO_SECOND_TIME_ADDITION)

        return 200, MessageResponseSchema.create(ADDED_SUCCESS)
