import logging

from asgiref.sync import sync_to_async

from app.internal.transport.bot.telegram_messages import (
    NOT_VALID_ID_MSG,
    RESTRICT_SECOND_TIME_ADD,
    RESTRICT_SELF_OPS,
    USER_NOT_IN_FAV,
)
from app.models import Favourite

from .user_service import get_user_by_id, get_user_by_username

logger = logging.getLogger("django.server")


@sync_to_async
def get_limited_list_of_favourites(tlg_id, favs_limit):
    """
    Returns limited list of favourite users for Telegram User
    with ID tlg_id or returns None if fav object doens't exist.
    ----------
    :param tlg_id: Telegram ID of this user.
    """
    fav_opt = Favourite.objects.filter(tlg_id=tlg_id).first()
    if fav_opt:
        return list(fav_opt.favourites.all()[:favs_limit])
    return None


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


async def try_del_fav_from_user(context, chat_id, tlg_id_of_owner, fav_user):
    """
    Deletes fav_user User object from the list of
    favourites for user with ID tlg_id_of_owner

    Returns error flag (if specified fav_user not in favourites)
    ----------
    :param tlg_id_of_owner: Telegram ID of list owner.
    :param fav_user: user that will be deleted from favourites

    """

    error_not_in_fav_flag = False
    favs_manager = (await Favourite.objects.aget(tlg_id=tlg_id_of_owner)).favourites

    if await favs_manager.filter(pk=fav_user.tlg_id).aexists():
        await sync_to_async(favs_manager.remove)(fav_user)
        logger.info(f"User with ID {fav_user.tlg_id} was deleted from favourites of user {tlg_id_of_owner}")

    else:
        await context.bot.send_message(chat_id=chat_id, text=USER_NOT_IN_FAV)
        error_not_in_fav_flag = True

    return error_not_in_fav_flag


async def try_add_fav_to_user(context, chat_id, tlg_id_of_owner, new_fav_user):
    """
    Tries to add new User object to the list of favourites
    for another Telegram User (tlg_id_of_owner).

    Returns error flag (if new_fav_user was in favs).
    ----------
    :param tlg_id_of_owner: Telegram ID of list owner.
    :param new_fav_user: new favourite User obj.

    """
    error_add_flag = False
    favs_manager = (await Favourite.objects.aget_or_create(tlg_id=tlg_id_of_owner))[0].favourites

    if await favs_manager.filter(pk=new_fav_user.tlg_id).aexists():
        await context.bot.send_message(chat_id=chat_id, text=RESTRICT_SECOND_TIME_ADD)
        error_add_flag = True

    else:
        await sync_to_async(favs_manager.add)(new_fav_user)
        logger.info(f"User with ID {new_fav_user.tlg_id} added as favourite for {tlg_id_of_owner}")

    return error_add_flag


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
    error_ops_flag = False

    if another_id == user_id:
        await context.bot.send_message(chat_id=chat_id, text=RESTRICT_SELF_OPS)
        error_ops_flag = True

    return error_ops_flag


def get_result_message_for_user_favourites(favs_list):
    """
    Creates message with all favourites of a particular user
    ----------
    :param favs_list: list of favourite users
    """
    res_msg = ""
    for fav_user in favs_list:
        res_msg += f"Name: {fav_user.first_name} {fav_user.last_name}," + f" ID: {fav_user.tlg_id}, Phone: "
        res_msg += f"{fav_user.phone_number}\n" if fav_user.hasPhoneNumber() else "None\n"

    return res_msg
