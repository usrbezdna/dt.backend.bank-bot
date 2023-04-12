from concurrent.futures import ThreadPoolExecutor

import pytest
from rest_framework import status

from src.app.internal.services.user_service import update_user_phone_number
from src.app.internal.transport.bot.telegram_messages import get_unique_start_msg
from src.app.internal.transport.rest.serializers import TelegramUserSerializer
from src.app.models import User


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_smoke(
    bot_application, get_update_for_command, telegram_user, telegram_chat, mocked_context, web_api_url, client
):
    """
    This smoke test does the following steps:
    1) Tries to start Bot Application and ensures it is running
    2) Creates a mocked_update for start command and sends it for processing to update queue

    3) Shuts down the application and tries to check that:

        - Test User was successfully saved to DB
        - Telegram User recieved the unique start message

    4) Sets phone number for this User and tries to test WebAPI:

        - Checks that response status code equals 200
        (call to /api/me was successfull for verified user)
        - And compares response body with serialized data of this user

    """

    await bot_application.initialize()
    await bot_application.start()

    assert bot_application.running

    mocked_update = get_update_for_command("/start")
    await bot_application.process_update(mocked_update)
    await bot_application.stop()

    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_unique_start_msg(telegram_user.first_name)
    )

    user_model = await User.objects.filter(tlg_id=telegram_user.id).afirst()
    assert await User.objects.acount() == 1
    assert user_model

    await update_user_phone_number(user_model, "+7654321")
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(lambda url_for_user: client.get(url_for_user), web_api_url(tlg_id=123))
        response = future.result()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == TelegramUserSerializer(user_model).data
