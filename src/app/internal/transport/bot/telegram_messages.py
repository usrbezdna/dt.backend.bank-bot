# Default bot reply messages

NO_VERIFIED_PN = "You don't have a verified phone number!"
RESTRICT_SELF_OPS = "You can't do addition/deletion of themself!"
RESTRICT_SECOND_TIME_ADD = "You have already added this user to your favourites."
USER_NOT_IN_FAV = "Your favourites list doesn't include this user."

INVALID_PN_MSG = "It doesn't look like a valid phone number. Try again, please!"
ABSENT_PN_MSG = "It seems like you forgot to specify the phone number :("
ABSENT_ID_NUMBER = "You should specify unique card / account id! "

ME_WITH_NO_USER = "Type /start at first and verify you phone number"


ABSENT_FAV_MSG = (
    "Couldn't find any users in your favourites.\n" + "Don't forget to add them at first with /add_fav command"
)

ABSENT_ARG_FAV_MSG = (
    "It's necessary to mention the username or Telegram ID of this favourite user!"
    + ' Here is an example: "/add_fav @someUser" or\n "/del_fav 1077393018"'
)

ABSENT_FAV_USER = "There is no user in DB with such username / Telegram ID.\nCan't add it as your favourite."

ABSENT_OLD_FAV_USER = (
    "This user can't be found in DB (user with provided username / "
    + "Telegram ID doesn't exist). Can't delete it from your favourites!"
)

ABSENT_PASSWORD_MSG = "Don't forget to specify a new password!"
PASSWORD_UPDATED = "OK! Your password was updated."

INCR_TX_VALUE = "Transfering value should be a positive number"

NOT_VALID_ID_MSG = "Invalid ID."


BALANCE_NOT_FOUND = "Unable to find balance for this card / account"
STATE_NOT_FOUND = "Unable to find state for this card / account"

RSP_NOT_FOUND = "Recipient not found. Make sure you are using correct Telegram ID / username"
RSP_USER_WITH_NO_ACC = "This recipient user doesn't have a payment account."
RSP_USER_WITH_NO_CARDS = "Recipient user doesn't have any linked cards for his payment account"


SENDER_RESTRICTION = "You should have Payment account and at least one Card for making transactions!"
SELF_TRANSFER_ERROR = "Self-transfer is not supported"
INSUF_BALANCE = "Insufficient balance!"
ERROR_DURING_TRANSFER = "Some error occured during transfer!"

CARD_NOT_FOUND = "There is no card with such ID in DB"

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
    + "/list_fav; /add_fav and /del_fav - commands for management of your favourites\n"
    + "/list_inter - returns list of users you have interacted with\n"
    + "/set_password - updates your password"
)

NO_INTERACTED_USERS = "There is no users you have interacted with"
NO_TXS_FOR_LAST_MONTH = "You don't have any payment transactions for the last month"


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


def get_success_for_new_fav(fav_user):
    """
    Returns message with success for favourites addition.
    :param fav_user: Telegram User object that acts as a new favourite.
    """
    return f"User {fav_user.first_name} with ID: {fav_user.tlg_id} added to your favourites!"


def get_success_for_deleted_fav(fav_user):
    """
    Return message about successful deletion of fav_user from favourites.
    :param fav_user: Telegram User object that was deleted from favourites.
    """
    return f"User {fav_user.first_name} with ID: {fav_user.tlg_id} was deleted from your favourites!"


SEND_TO_ACC_ARGS = (
    "Use this command with 2 following arguments: <Payment Account ID> and <Value>.\n\n"
    + "Don't forget to add recipient Telegram User to favourites at first!"
    + "Usage example: /send_to_account 51241421 450"
)

SEND_TO_CARD_ARGS = (
    "Use this command with 2 following arguments: <Card ID> and <Value>.\n\n"
    + "Don't forget to add recipient Telegram User to favourites at first!"
    + "Usage example: /send_to_card 3214122 150"
)

SEND_TO_USER_ARGS = (
    "Use this command with 2 following arguments: <Recipient Telegram ID / username> and <Value>.\n\n"
    + "Don't forget to add recipient Telegram User to favourites at first!"
    + "Usage example: /send_to_user @usrBezdna 100"
)


def get_info_for_me_handler(user_from_db):
    """
    Returns info for /me handler
    :param user_from_db: User object
    """
    return f"Here is some info about you:\n\n {str(user_from_db)}"


def get_message_for_send_command(arg_command):
    """
    Returns uniq message for each type of send_to command.
    :param arg_command: first command argument with command name.
    """
    match arg_command:
        case "/send_to_user":
            return SEND_TO_USER_ARGS
        case "/send_to_account":
            return SEND_TO_ACC_ARGS
        case "/send_to_card":
            return SEND_TO_CARD_ARGS


def get_successful_transfer_message(recipient_name, value):
    """
    Returns message for successful transfer.
    :param recipient: recipient payment Account
    :value: transferring value
    """
    return f"OK! Transaction is finished. Transferred {value} to user {recipient_name}"


def get_message_with_balance(account):
    """
    Returns message with account value
    :param account: Payment Account object
    """
    return f"This card / account balance is {int(account.value)}"
