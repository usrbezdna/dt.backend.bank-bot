### Default bot reply messages 


INVALID_PN_MSG = 'It doesn\'t look like a valid phone number. Try again, please!'
ABSENT_PN_MSG = 'It seems like you forgot to specify the phone number :('

NOT_INT_FORMAT_MSG = 'Don\'t forget to specify ' +\
'phone number with an international country code. Such as: ' +\
'+432111123456 or +7911123456'


def get_unique_start_msg(username : str) -> str:
    """
    Creates unique start message for each user.
    :param username: Telegram User username
    """
    return (f'Hi {username}!\n'
    'Thanks for choosing this Banking Bot. He doesn\'t have ' 
    'much functions just yet, but this will be changed in '
    'future updates')

def get_success_phone_msg(phone_number) -> str:
    """
    Returns message with valid phone number.
    :param phone_number: Telegram User parsed and validated number
    """
    return f'Successfully updated your phone number: {phone_number}'