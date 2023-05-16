from typing import Any, Dict, List

from app.internal.api_v1.payment.accounts.domain.entities import AccountSchema

NO_VERIFIED_PN = "You don't have a verified phone number!"


ABSENT_ID_NUMBER = "You should specify unique card / account id! "
BALANCE_NOT_FOUND = "Unable to find balance for this card / account"

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


INCR_TX_VALUE = "Transfering value should be a positive number"

SENDER_RESTRICTION = "You should have Payment account and at least one Card for making transactions!"


RSP_NOT_FOUND = "Recipient not found. Make sure you are using correct Telegram ID / username"
RSP_RESTRICTION = "Make sure this recipient has at least one Card and Payment account!"


SELF_TRANSFER_ERROR = "Self-transfer is not supported"
INSUF_BALANCE = "Insufficient balance!"
ERROR_DURING_TRANSFER = "Some error occured during transfer!"

CARD_NOT_FOUND = "There is no card with such ID in DB"


STATE_NOT_FOUND = "Unable to find state for this card / account"
NO_INTERACTED_USERS = "There is no users you have interacted with"
NO_TXS_FOR_LAST_MONTH = "You don't have any payment transactions for the last month"


def get_message_with_balance(account: AccountSchema) -> str:
    """
    Returns message with account value
    :param account: Payment Account object
    """
    return f"This card / account balance is {int(account.value)}"


def get_message_for_send_command(arg_command: str) -> str:
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


def get_successful_transfer_message(recipient_name: str, value: int) -> str:
    """
    Returns message for successful transfer.
    :param recipient: recipient payment Account
    :param value: transferring value
    """
    return f"OK! Transaction is finished. Transferred {value} to user {recipient_name}"


def get_result_message_for_list_interacted(usernames_list: List[str]) -> str:
    """
    Returns message with usernames of users who
    have interacted with this user.
    ----------
    :param usernames_list: list of usernames
    """
    res_msg = "Here is the list of interacted users:"
    for username in usernames_list:
        res_msg += f"\n - {username}"

    return res_msg


def get_result_message_for_transaction_state(transactions_list: List[Dict[str, Any]]) -> str:
    """
    Returns message with transactions for the last month.
    ----------
    :param transactions_list: list of transactions
    """
    res_msg = "List of transactions for the last month: \n\n"
    for tx_data in transactions_list:
        res_msg += (
            f"TX ID: {tx_data['tx_id']}, "
            + f"Date: {tx_data['date']}, "
            + f"Sender: {tx_data['sender_name']}, "
            + f"Recipient: {tx_data['recip_name']}, "
            + f"Value: {tx_data['tx_value']}\n"
        )

    return res_msg
