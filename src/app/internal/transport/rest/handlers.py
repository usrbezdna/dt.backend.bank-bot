import asyncio
import logging


from app.internal.services.user_service import get_user_by_id
from app.internal.schemas.user import UserSchema

from ninja import Schema
from .content_messages import NO_PHONE_VERIFICATION, USER_NOT_FOUND
from ninja.errors import HttpError

logger = logging.getLogger("django.server")

class MessageResponse(Schema):
    message: str

    @staticmethod
    def create(msg: str):
        return MessageResponse(message=msg)



def get_me(request, tlg_id : int):
    """
    Returns info about specified Telegram User
    
    """
    logger.info("Got new GET request on /api/me endpoint!")

    user_from_db = asyncio.run(get_user_by_id(tlg_id))
    if user_from_db:
        return 200, user_from_db
    
    return 404, MessageResponse.create('Not Found')