import logging
import sys

import requests

logger = logging.getLogger("django.server")


def parse_ngrok_url():
    """
    This function parses default Ngrok API Page and returns public_url.
    ----------
    :return: public_url is available all over the net
    :raises NewConnectionError: if Ngrok instance is not up and running
    """
    try:
        response = requests.get("http://localhost:4040/api/tunnels/")
        return response.json().get("tunnels")[0].get("public_url")
    except Exception as e:
        logger.error(f"It looks like you haven't started ngrok instance and it caused a Connection Error:\n\n{e}")
        sys.exit(1)
