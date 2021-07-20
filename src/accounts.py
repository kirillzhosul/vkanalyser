# Accounts module for working with accounts.


# Importing.

# Typing for types.
import typing

# Requests for requests.
import requests


# Classes.


class Service:
    # Class service that presents service.

    def __init__(self, _title: str, _link: str, _timeout: int = 3):
        # Values.

        # Title returned in search() list.
        self.title = _title

        # Link for check (SHOULD HAVE {} WHERE NICKNAME WILL BE INSERTED)
        self.link = _link

        # Timeout for request (left default if don`t get meaning).
        self.timeout = _timeout

# Settings.


# Services data.
SERVICES = {
    Service("Instagram", "https://www.instagram.com/{}", 5),
    Service("Facebook", "https://www.facebook.com/{}/", 3),
    Service("OK", "https://ok.ru/{}", 2),
    Service("TikTok", "https://www.tiktok.com/@{}", 5),
    Service("Github", "https://github.com/{}", 4),
    Service("Steam", "https://steamcommunity.com/id/{}", 5),
    Service("YouTube", "https://www.youtube.com/user/{}", 2),
    Service("Twitch", "https://www.twitch.tv/{}", 2),
    Service("Twitter", "https://twitter.com/{}", 3)
}

# Headers for requests.
HEADERS = {
    "User-Agent": "VK Analyser"
}


# Functions.

def search(_nickname: str) -> list:
    # Function that searches for services.

    # Returning (__check() for all services in SERVICES and adding in list if not None).
    return [_service for _service in [__check(_service, _nickname) for _service in SERVICES] if _service is not None]


def __check(_service: Service, _nickname: str) -> typing.Optional[tuple]:
    # Function that checks service nickname existence

    # Function that check is 404 or not.

    # Getting link.
    _service_link = _service.link.format(_nickname)

    # Returning.
    try:
        # Getting response.
        _response = requests.get(_service_link, headers=HEADERS)
    except (requests.RequestException, requests.Timeout):
        # If error.

        # Returning None.
        return None

    if _response.status_code == 404:
        # If 404 NOT FOUND.

        # Returning None.
        return None

    # Returning title.
    return _service.title, _service_link
