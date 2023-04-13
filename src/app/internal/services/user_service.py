import logging

from asgiref.sync import sync_to_async

from app.models import User

logger = logging.getLogger("django.server")


@sync_to_async
def get_user_by_id(tlg_id):
    """
    Returns Telegram user by ID from Database or None
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
def get_user_by_username(username):
    """
    Returns Tg user by username from DB or None.
    ----------
    :param username: Telegram user username
    :return: Telegram User | None
    """
    user_option = User.objects.filter(username=username).first()
    if user_option:
        return user_option
    logger.info(f"User with username {username} not found in DB")
    return None


@sync_to_async
def get_user_field_by_id(tlg_id, field_name):
    """
    Returns Query Set with specified field for User with Telegram ID tlg_id  
    ----------
    :param tlg_id: Telegram User ID
    :params fields: Wished list of model fields 
    :return: Value of this field
    """
    return User.objects.values_list(field_name, flat=True).get(pk=tlg_id)




@sync_to_async
def update_user_phone_number(tlg_id, new_phone_number):
    """
    Updates phone number for a specific User.
    ----------
    :param tlg_id: Telegram ID of this User
    :param new_phone_number: already validated phone number as a string
    """

    User.objects.filter(tlg_id=tlg_id).update(phone_number=new_phone_number)
    logger.info(f"Updated phone number for user with {tlg_id} ID")


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
    logger.info(f"User with {user.tlg_id} ID was successfully saved to DB")



def create_user_model_for_telegram(user):
    """
    This function recieves user in a form of Effective Telegram User
    and creates a new model based on provided info.
    ----------
    :param user: Telegram user object
    """
    return User(
        tlg_id=user.id,
        username=user.username if user.username else "",
        first_name=user.first_name,
        last_name=user.last_name if user.last_name else "",
        phone_number="",
    )
