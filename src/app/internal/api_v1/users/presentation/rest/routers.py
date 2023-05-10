from ninja import Router, Schema
from ninja_jwt.authentication import JWTAuth

from app.internal.api_v1.users.domain.entities import UserSchema, MessageResponseSchema

from app.internal.api_v1.users.presentation.rest.handlers import RestUserHandlers



def get_users_router(rest_user_handlers : RestUserHandlers):
    """
    Creates router for /users/* requests
    """
    router = Router()

    router.add_api_operation(
        path="/me",
        methods=["GET"],
        view_func=rest_user_handlers.get_me,
        response={
            200: UserSchema,
            403: MessageResponseSchema,
            404: MessageResponseSchema,
        },
        auth=JWTAuth(),
        description="Returns full information about Telegram user",
    )

    router.add_api_operation(
        path="/set_phone",
        methods=["PUT"],
        view_func=rest_user_handlers.set_phone,
        response = {
            200 : MessageResponseSchema,
            400 : MessageResponseSchema,
        },
        auth=JWTAuth(),
        description="Returns help message"
    )

    return router