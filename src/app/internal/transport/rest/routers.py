from ninja import Router, Schema
from ninja_jwt.authentication import JWTAuth

from app.internal.schemas.user import UserSchema

from .handlers import MessageResponse, get_me


def create_me_router():
    """
    Creates router for /api/me enpoint
    and attaches corresponding handler

    :return: Router object
    """
    router = Router()

    router.add_api_operation(
        path="/",
        methods=["GET"],
        view_func=get_me,
        response={
            200: UserSchema,
            403: MessageResponse,
            404: MessageResponse,
        },
        auth=JWTAuth(),
        description="Returns full information about Telegram user",
    )

    return router


me_router = create_me_router()
