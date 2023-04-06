import logging

from asgiref.sync import sync_to_async

from app.internal.transport.bot.telegram_messages import (
    NOT_VALID_ID_MSG, RESTRICT_SECOND_TIME_ADD, 
    RESTRICT_SELF_OPS, USER_NOT_IN_FAV
)

from app.models import Favourite

from .user_service import get_user_by_id, get_user_by_username

logger = logging.getLogger("django.server")


@sync_to_async
def get_list_of_favourites(tlg_id):
    """
    Returns list of favourite users or None
    for Telegram User with ID tlg_id.
    ----------
    :param tlg_id: Telegram ID of this user.
    """
    fav_opt = Favourite.objects.filter(tlg_id=tlg_id).first()
    if fav_opt:
        return list(fav_opt.favourites.all())
    return None


@sync_to_async
def add_fav_to_user(tlg_id_of_owner, new_fav_user):
    """
    Adds new User object to the list of favourites
    for another Telegram User (tlg_id_of_owner).
    ----------
    :param tlg_id_of_owner: Telegram ID of list owner.
    :param new_fav_user: new favourite User obj.

    """
    Favourite.objects.get_or_create(tlg_id=tlg_id_of_owner)[0].favourites.add(new_fav_user)
    logger.info(f"User with ID {new_fav_user.tlg_id} added as favourite for {tlg_id_of_owner}")


@sync_to_async
def del_fav_from_user(tlg_id_of_owner, fav_user):
    """
    Deletes fav_user User object from the list of
    favourites for user with ID tlg_id_of_owner
    ----------
    :param tlg_id_of_owner: Telegram ID of list owner.
    :param fav_user: user that will be deleted from favourites
    """
    Favourite.objects.get(tlg_id=tlg_id_of_owner).favourites.remove(fav_user)
    logger.info(f"User with ID {fav_user.tlg_id} was deleted from favourites of user {tlg_id_of_owner}")


async def try_get_another_user(context, chat_id, argument):
    """
    This function tries to get user by username or Telegram ID.
    Returns Tuple with (another_user_option, arg_error_flag)
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID

    :param argument: argument of /add_fav command
    :return: Tuple with another User obj and error argument flag

    """
    if argument.startswith("@"):
        another_user_option = await get_user_by_username(argument[1:])

    elif not argument.isdigit() or int(argument) <= 0:
        await context.bot.send_message(chat_id=chat_id, text=NOT_VALID_ID_MSG)
        return (None, True)

    else:
        another_user_option = await get_user_by_id(argument)

    return (another_user_option, False)


async def prevent_ops_with_themself(context, chat_id, user_id, another_id):
    """
    Prevents operations (deletion, addition) with themself.
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID

    :param user_id: Telegram User ID
    :param: another_id: Telegram ID of another User

    :return: error flag

    """
    if another_id == user_id:
        await context.bot.send_message(chat_id=chat_id, text=RESTRICT_SELF_OPS)
        return True
    return False


async def prevent_second_time_add(context, chat_id, user_id, another_user):
    """
    Prevents addition of Telegram User that's already in list.
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID

    :param user_id: Telegram User ID
    :param: another_user: new favourite user

    :return: error flag
    """
    list_fav = await get_list_of_favourites(user_id)

    if list_fav and another_user in list_fav:
        await context.bot.send_message(chat_id=chat_id, text=RESTRICT_SECOND_TIME_ADD)
        return True
    return False


async def ensure_user_in_fav(context, chat_id, user_id, another_user):
    """
    Ensures that favourites for user with ID <user_id>
    actually includes another_user.
    ----------
    :param context: context object
    :param chat_id: Telegram Chat ID

    :param user_id: Telegram User ID
    :param: another_user: user that should be in favourites

    :return: error flag
    """

    list_fav = await get_list_of_favourites(user_id)

    if not list_fav or another_user not in list_fav:
        await context.bot.send_message(chat_id=chat_id, text=USER_NOT_IN_FAV)
        return True
    return False


def get_result_message_for_user_favourites(favs_list, users_limit):
    """
    Creates message with all favourites of a particular user  
    ----------
    :param favs_list: list of favourite users
    :param users_limit: allows us to limit number of users in result message 
    """
    res_msg = ""
    for fav_user in favs_list[:users_limit]:

        res_msg += f"Name: {fav_user.first_name} {fav_user.last_name}," + f" ID: {fav_user.tlg_id}, Phone: "
        res_msg += f"{fav_user.phone_number}\n" if fav_user.hasPhoneNumber() else "None\n"

    return res_msg
