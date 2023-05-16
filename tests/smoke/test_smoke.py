import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from django.test import AsyncClient, Client

from src.app.internal.api_v1.users.domain.entities import UserSchema
from src.app.internal.api_v1.users.presentation.bot.telegram_messages import get_unique_start_msg
from src.app.models import User


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.django_db
@pytest.mark.valid_case
async def test_smoke(bot_application, get_update_for_command, telegram_user, telegram_chat, mocked_context, client):
    """
    This smoke test does the following steps:
    1) Tries to start Bot Application and ensures it is running
    2) Creates a mocked_update for start command and sends it for processing to update queue

    3) Shuts down the application and tries to check that:

        - Test User was successfully saved to DB
        - Telegram User recieved the unique start message

    4) Sets phone number and password for this User and tries to get access token for auth

    5) Passes authentication and sends request on /api/users/me endpoint

    6) After that it completes last two steps:

        - Checks that response status code equals 200
        (call to /api/users/me was successfull for verified user)
        - And compares the response body with actual data of this UserSchema

    """

    # 1
    await bot_application.initialize()
    await bot_application.start()

    assert bot_application.running

    # 2
    mocked_update = get_update_for_command("/start")
    await bot_application.process_update(mocked_update)
    await bot_application.stop()

    # 3
    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, text=get_unique_start_msg(telegram_user.first_name)
    )

    user_model = await User.objects.filter(tlg_id=telegram_user.id).afirst()

    assert await User.objects.acount() == 1
    assert await User.objects.aget(pk=user_model.tlg_id) == user_model

    # 4
    user_model.set_password("123456789")
    user_model.phone_number = "+4214214"
    await user_model.asave()

    client = AsyncClient()

    req_data = {"password": "123456789", "tlg_id": telegram_user.id}
    token_response = await client.post(
        path="/api/token/pair",
        data=json.dumps(req_data),
        content_type="application/json",
    )

    access_token = token_response.json()["access"]

    # 5
    me_response = await client.get(path="/api/users/me", **{"Authorization": f"Bearer {access_token}"})

    # 6
    assert UserSchema.from_orm(user_model) == me_response.json()
    assert me_response.status_code == 200
