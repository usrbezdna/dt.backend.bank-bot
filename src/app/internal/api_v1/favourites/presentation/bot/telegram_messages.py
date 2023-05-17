from typing import List

from app.internal.api_v1.users.domain.entities import UserSchema

ABSENT_FAV_MSG = (
    "Couldn't find any users in your favourites.\n" + "Don't forget to add them at first with /add_fav command"
)

ABSENT_ARG_FAV_MSG = (
    "It's necessary to mention the username or Telegram ID of this favourite user!"
    + ' Here is an example: "/add_fav @someUser" or\n "/del_fav 1077393018"'
)


ABSENT_FAV_USER = "This user can't be found in DB. Can't use it in operations with your favourites!"

NOT_VALID_ID_MSG = "Invalid ID."


RESTRICT_SELF_OPS = "You can't do addition/deletion of themself!"
RESTRICT_SECOND_TIME_ADD = "You have already added this user to your favourites."

USER_NOT_IN_FAV = "Your favourites list doesn't include this user."


def get_result_message_for_user_favourites(favs_list: List[UserSchema]) -> str:
    """
    Creates message with all favourites of a particular user
    ----------
    :param favs_list: list of favourite users
    """
    res_msg = ""
    for fav_user in favs_list:
        res_msg += f"Name: {fav_user.first_name} {fav_user.last_name}," + f" ID: {fav_user.tlg_id}, Phone: "
        res_msg += f"{fav_user.phone_number}\n" if fav_user.phone_number != "" else "None\n"

    return res_msg


def get_success_msg_for_new_fav(fav_user: UserSchema) -> str:
    """
    Returns message with success for favourites addition.
    :param fav_user: Telegram User object that acts as a new favourite.
    """
    return f"User {fav_user.first_name} with ID: {fav_user.tlg_id} added to your favourites!"


def get_success_msg_for_deleted_fav(fav_user: UserSchema) -> str:
    """
    Return message about successful deletion of fav_user from favourites.
    :param fav_user: Telegram User object that was deleted from favourites.
    """
    return f"User {fav_user.first_name} with ID: {fav_user.tlg_id} was deleted from your favourites!"
