from app.internal.api_v1.users.domain.entities import UserSchema

NO_VERIFIED_PN = "You don't have a verified phone number!"

ABSENT_PN_MSG = "It seems like you forgot to specify the phone number :("
INVALID_PN_MSG = "It doesn't look like a valid phone number. Try again, please!"

USER_NOT_FOUND_MSG = "Can't find any info about you, type /start at first!"


ABSENT_PASSWORD_MSG = "Don't forget to specify a new password!"
PASSWORD_UPDATED = "OK! Your password was updated."

HELP_MSG = (
    "Hi, I am yet another banking bot!\n"
    + "Here is the list of commands I support:\n\n"
    + "/start - prints started message, adds you to DB\n"
    + "/set_phone - sets your phone number in an international format\n"
    + "/me - returns known info about your account (verified phone req.)\n"
    + "/check_card and /check_account - returns balance of specified card or account\n"
    + "/list_fav; /add_fav and /del_fav - commands for management of your favourites\n"
    + "/list_inter - returns list of users you have interacted with\n"
    + "/set_password - updates your password"
)


NOT_INT_FORMAT_MSG = (
    "Don't forget to specify "
    + "phone number with an international country code. Such as: "
    + "+432111123456 or +7911123456"
)


def get_unique_start_msg(first_name: str) -> str:
    """
    Creates unique start message for each user.
    :param first_name: Telegram User first name
    """
    return (
        f"Hi {first_name}!\n"
        "Thanks for choosing this Banking Bot. He doesn't have "
        "much functions just yet, but this will be changed in "
        "future updates"
    )


def get_success_phone_msg(phone_number: str) -> str:
    """
    Returns message with valid phone number.
    :param phone_number: Telegram User parsed and validated number
    """
    return f"Successfully updated your phone number: {phone_number}"


def get_info_for_me_handler(user_from_db: UserSchema) -> str:
    """
    Returns info for /me handler
    :param user_from_db: User object
    """
    return f"Here is some info about you:\n\n{str(user_from_db)}"
