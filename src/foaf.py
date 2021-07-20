# FOAF module for working with VK FOAF data.


# Importing.


# Requests for requests.
import requests

# Parsing FOAF.
import re

# Typing for types.
import typing

# Enum for enumerators.
import enum


# Classes.


class ProfileState(enum.Enum):
    # Profile state types.

    # Active profile.
    active = "active",

    # Banned profile.
    banned = "banned",

    # Deactivated profile.
    deactivated = "deactivated",


class ProfileAccess(enum.Enum):
    # Profile access types.

    # Allowed access.
    allowed = "allowed",

    # Disallowed access.
    disallowed = "disallowed",


# Functions.

def get(_profile_index: int) -> dict:
    # Function that gets vk profile data.

    # Returning parsed.
    return parse(load(int(_profile_index)))


def parse(_foaf: str) -> typing.Optional[dict]:
    # Function that parses FOAF.

    def __parse_field(_pattern: str, _default: str = "") -> str:
        # Sub function for parsing field.

        # Searching for field.
        _field = re.findall(_pattern, _foaf)

        # Returning default or field.
        return _default if len(_field) == 0 else _field[0]

    # Fields dict.
    _fields = {
        "flag_state": __parse_field(r'<ya:profileState>(.*)</ya:profileState>'),
        "flag_access": __parse_field(r'<ya:publicAccess>(.*)</ya:publicAccess>'),
        "date_logged": __parse_field(r'ya:lastLoggedIn dc:date="(.*)"'),
        "date_created": __parse_field(r'ya:created dc:date="(.*)"'),
        "date_modified": __parse_field(r'ya:modified dc:date="(.*)"'),
        "person_name": __parse_field(r'<foaf:name>(.*)</foaf:name>'),
    }

    # Objects.

    # State.
    if _fields["flag_state"] != "":
        _fields["flag_state"] = ProfileState[_fields["flag_state"]]

    # Access.
    if _fields["flag_access"] != "":
        _fields["flag_access"] = ProfileAccess[_fields["flag_access"]]

    # Returning fields.
    return _fields


def load(_profile_index: int) -> str:
    # Function that loads FOAF XML data from VK.

    if int(_profile_index) <= 0:
        # If profile invalid.

        # Returning blank.
        return ""

    # Getting request link.
    _api_request_link = "https://vk.com/foaf.php"
    _api_request_link = f"{_api_request_link}?" \
                        f"id={_profile_index}"

    # Getting response.
    _api_response = requests.get(_api_request_link)
    _api_response = _api_response.text

    # Returning response.
    return _api_response
