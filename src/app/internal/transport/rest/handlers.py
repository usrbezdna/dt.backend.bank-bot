import asyncio
import logging

from asgiref.sync import sync_to_async
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.internal.services.user_service import get_user_by_id

from .content_messages import NO_PHONE_VERIFICATION, USER_NOT_FOUND
from .serializers import TelegramUserSerializer

logger = logging.getLogger("django.server")


class WebAPIView(APIView):
    """
    View, serving API endpoint /api/me/{some_tlg_id}/.
    Allows user to get info about himself.
    """

    def get(self, request, tlg_id):
        logger.info("Got new GET request on /api/me endpoint!")

        user_from_db = asyncio.run(get_user_by_id(tlg_id))
        if user_from_db:
            if user_from_db.hasPhoneNumber():
                serialized = TelegramUserSerializer(user_from_db)
                return Response(serialized.data, status.HTTP_200_OK)

            return Response(NO_PHONE_VERIFICATION, status=status.HTTP_403_FORBIDDEN)
        return Response(USER_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
