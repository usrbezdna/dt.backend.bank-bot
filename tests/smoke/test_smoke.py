import pytest

from src.app.models import User
from src.app.internal.transport.bot.handlers import start
from src.app.internal.transport.bot.telegram_messages import get_unique_start_msg

@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_smoke(bot_application, get_update_for_command, telegram_user, telegram_chat, mocked_context):
    """
    This smoke test does the following steps:
    1) Tries to start Bot Application and ensures it is running
    2) Creates a mocked_update for start command and sends it for processing to update queue

    3) Shuts down the application and tries to check that:
        - Test User was successfully saved to DB
        - Telegram User recieved the unique start message
    """
   

    await bot_application.initialize()
    await bot_application.start()

    assert bot_application.running

    mocked_update = get_update_for_command('/start')
    await bot_application.process_update(mocked_update) 
    await bot_application.stop()


    mocked_context.bot.send_message.assert_called_once_with(
        chat_id=telegram_chat.id, 
        text=get_unique_start_msg(telegram_user.first_name)
    )


    assert await User.objects.acount() == 1
    assert await User.objects.filter(tlg_id=telegram_user.id).afirst()