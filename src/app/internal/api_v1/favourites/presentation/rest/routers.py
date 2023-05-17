from typing import List

from ninja import Router
from ninja_jwt.authentication import JWTAuth

from app.internal.api_v1.favourites.presentation.rest.handlers import RestFavouritesHandlers
from app.internal.api_v1.users.domain.entities import MessageResponseSchema, UserSchema


def get_favourites_router(rest_fav_handlers: RestFavouritesHandlers):
    """
    Creates router for /favourites/* requests
    """

    router = Router(tags=["favourites"])

    router.add_api_operation(
        path="",
        methods=["GET"],
        view_func=rest_fav_handlers.list_fav,
        response={
            200: List[UserSchema],
            404: MessageResponseSchema,
        },
        auth=JWTAuth(),
        description="Returns list of favourite users",
    )

    router.add_api_operation(
        path="",
        methods=["PUT"],
        view_func=rest_fav_handlers.add_fav,
        response={
            200: MessageResponseSchema,
            400: MessageResponseSchema,
            403: MessageResponseSchema,
            404: MessageResponseSchema,
        },
        auth=JWTAuth(),
        description="Addes Telegram user into favourites list",
    )

    router.add_api_operation(
        path="",
        methods=["DELETE"],
        view_func=rest_fav_handlers.del_fav,
        response={
            200: MessageResponseSchema,
            400: MessageResponseSchema,
            403: MessageResponseSchema,
            404: MessageResponseSchema,
        },
        auth=JWTAuth(),
        description="Deletes Telegram user from favourites",
    )

    return router
