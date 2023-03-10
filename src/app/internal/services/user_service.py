import logging

from asgiref.sync import sync_to_async

from app.models import User

logger = logging.getLogger("django.server")


@sync_to_async
def get_user_from_db(tlg_id):
    """
    Returns Telegram user from Database or None
    (if this user doesn't exist)
    ----------
    :param tlg_id: Telegram user ID
    :return: Telegram User | None
    """
    user_option = User.objects.filter(tlg_id=tlg_id).first()
    if user_option:
        return user_option
    logger.info(f"User with ID {tlg_id} not found in DB")
    return None


@sync_to_async
def save_user_to_db(user):
    """
    Receives Telegram user and saves it in DB.
    (Might be modified in the future to run some
    checks before saving)
    ----------
    :param user: Telegram user object
    """
    user.save()
    logger.info(f"User {user.username} was successfully saved to DB")


@sync_to_async
def update_user_phone_number(user, new_phone_number):
    """
    Updates phone number for a specific User.
    ----------
    :param user: Telegram user object
    :param new_phone_number: already validated phone number as a string
    """

    user.phone_number = new_phone_number
    user.save()
    logger.info(f"Updated phone number for user {user.username}")
