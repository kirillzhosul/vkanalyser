# Phone module for working with phones.


# Importing.

# OS For working with env.
import os

# Typing for types.
import typing

# Requests for requests.
import requests

# Importing json for parsing.
import json


# Settings.


# NUMVERIFY API key, if in PATH, otherwise - from code.
# You may get it there https://numverify.com
API_KEY = os.getenv("NUMVERIFY_KEY", None)

# Is phone processing is enabled or not.
ENABLED = True


# Functions.


def is_enabled() -> bool:
    # Function that returns is processing enabled or not.

    # Returning.
    return ENABLED and is_configured()


def is_configured() -> bool:
    # Function that returns is Numverify configured or not.

    # Returning.
    return API_KEY is not None


def lookup(_number: typing.Union[str, int], _country_code: str = "", _format: int = 1) -> typing.Union[dict, None]:
    # Function that lookup for phone number.

    if not is_configured():
        # If not configured.

        # Returning.
        return None

    # Getting request link.
    _api_request_link = "http://apilayer.net/api/validate"
    _api_request_link = f"{_api_request_link}?" \
                        f"access_key={API_KEY}&" \
                        f"number={_number}&" \
                        f"country_code={_country_code}&" \
                        f"format={_format}"

    # Getting response.
    _api_response = requests.get(_api_request_link)
    _api_response = json.loads(_api_response.text)

    if "error" in _api_response:
        # If error in response.

        # Returning.
        return None

    if not _api_response["valid"]:
        # If not valid response.

        # Returning.
        return None

    # Returning.
    return _api_response

# Entry point.


if API_KEY is None:
    # If key is not set.

    # Message.
    print("[Debug][Phone][Numverify] Key is not set! Phone processing is disabled.")

    # Disabling.
    ENABLED = False
