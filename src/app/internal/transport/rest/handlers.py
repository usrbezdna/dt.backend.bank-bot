import asyncio
import logging

from ninja import Schema
from ninja.errors import HttpError

from app.internal.api_v1.users.domain.entities import UserSchema
# from app.internal.services.user_service import get_user_by_id

from .content_messages import NO_PHONE_VERIFICATION, USER_NOT_FOUND

logger = logging.getLogger("django.server")


class MessageResponse(Schema):
    message: str

    @staticmethod
    def create(msg: str):
        return MessageResponse(message=msg)


def get_me(request):
    """
    Returns info about specified Telegram User

    """
    logger.info("Got new GET request on /api/me endpoint!")

    # user_from_db = asyncio.run(get_user_by_id(request.user.tlg_id))
    # if user_from_db:
    #     if user_from_db.hasPhoneNumber():
    #         return 200, user_from_db
    #     return 403, MessageResponse.create("No verified phone number")

    return 404, MessageResponse.create("Not Found")
