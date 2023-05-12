import asyncio
import logging

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import is_valid_number
from phonenumbers.phonenumberutil import NumberParseException

from app.internal.api_v1.users.domain.entities import MessageResponseSchema
from app.internal.api_v1.users.domain.services import UserService

from .content_messages import INVALID_PHONE_NUMBER, NOT_VERIFIED, PASSWORD_SUCCESS, PHONE_NUMBER_SUCCESS

logger = logging.getLogger("django.server")


class RestUserHandlers:
    def __init__(self, user_service: UserService):
        self._user_service = user_service

    def get_me(self, request):
        """
        Returns info about Telegram User
        """

        logger.info("Got new GET request on /api/me endpoint!")

        user_from_db = asyncio.run(self._user_service.get_user_by_id(request.user.tlg_id))

        if not user_from_db.hasPhoneNumber():
            return 403, MessageResponseSchema.create(NOT_VERIFIED)

        return 200, user_from_db

    def set_phone(self, request, new_phone: str):
        """
        Sets new phone for this user
        """

        logger.info("Got new GET request on /api/users/phone endpoint!")

        try:
            parsed_number = PhoneNumber.from_string(new_phone)

        except NumberParseException:
            logger.info("User did not provide a valid phone number and it caused ParseError")
            return 400, MessageResponseSchema.create(INVALID_PHONE_NUMBER)

        if not is_valid_number(parsed_number):
            logger.info("Provided number was parsed, but is not valid anyway")
            return 400, MessageResponseSchema.create(INVALID_PHONE_NUMBER)

        asyncio.run(
            self._user_service.update_user_phone_number(tlg_id=request.user.tlg_id, new_phone_number=parsed_number)
        )

        return 200, MessageResponseSchema.create(PHONE_NUMBER_SUCCESS)

    def set_password(self, request, new_password: str):
        """
        Sets new password for this user
        """

        logger.info("Got new POST request on /api/users/password endpoint!")

        asyncio.run(self._user_service.update_user_password(tlg_id=request.user.tlg_id, new_password=new_password))

        return 200, MessageResponseSchema.create(PASSWORD_SUCCESS)
