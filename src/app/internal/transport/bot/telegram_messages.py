# Default bot reply messages


INVALID_PN_MSG = "It doesn't look like a valid phone number. Try again, please!"
ABSENT_PN_MSG = "It seems like you forgot to specify the phone number :("
ABSENT_ID_NUMBER = "You should specify unique card / account id! "

NOT_INT_FORMAT_MSG = (
    "Don't forget to specify "
    + "phone number with an international country code. Such as: "
    + "+432111123456 or +7911123456"
)

HELP_MSG = (
    "Hi, I am yet another banking bot!\n"
    + "Here is the list of commands I support:\n\n"
    + "/start - prints started message, adds you to DB\n"
    + "/set_phone - sets your phone number in an international format\n"
    + "/me - returns known info about your account (verified phone req.)\n"
    + "/check_card and /check_account - returns balance of specified card or account\n"
)


def get_unique_start_msg(first_name):
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


def get_success_phone_msg(phone_number):
    """
    Returns message with valid phone number.
    :param phone_number: Telegram User parsed and validated number
    """
    return f"Successfully updated your phone number: {phone_number}"
