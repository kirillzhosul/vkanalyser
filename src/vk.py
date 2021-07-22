# Module VK for working with VK API.


# Importing.

# OS For working with env.
import os

# VK API for working with vk.
import vk_api
import vk_api.longpoll
import vk_api.utils

# Typing for types.
import typing

# Importing local modules.

# Utils for working with chunks and id converting.
from utils import chunks

# Settings.


# VK API Token.
__TOKEN: typing.Optional[str] = os.getenv("VK_USER_TOKEN", None)

# Variables.


# API Object.
API: vk_api.VkApi = None  # noqa

# Default longpoll events handlers.
HANDLERS: list = []

# Events what we need in longpoll.
EVENTS: list = [
    # Just message for default.
    vk_api.longpoll.VkEventType.MESSAGE_NEW
]

# Current user index.
USER_ID: int = 0


# Main Functions.


def __is_authorized() -> bool:
    # Returning is token exists or not.

    # Returning.
    return __TOKEN is not None


def __is_allowed() -> bool:
    # Returning is allowed to connected or not.

    # Returning if authorized and not connected.
    return __is_authorized() and not is_connected()


def is_connected() -> bool:
    # Returning is API connected or not.

    # Returning.
    return API is not None


def handler_add(_handler: typing.Callable) -> None:
    # Adds handlers.

    # Returning if handler exists.
    if _handler in HANDLERS:
        return

    # Adding handler.
    HANDLERS.append(_handler)


def event_add(_event: vk_api.longpoll.VkEventType) -> None:
    # Adds event.

    # Returning if event exists.
    if _event in EVENTS:
        return

    # Adding event.
    EVENTS.append(_event)


def listen() -> typing.NoReturn:
    # Function that starts listening.

    for _event in vk_api.longpoll.VkLongPoll(API).listen():
        # For every event.

        # Passing if event not supposed to be used.
        if _event.type not in EVENTS:
            continue

        for _handler in HANDLERS:
            # For every handler.

            # Calling handler.
            _handler(_event)


def connect() -> None:
    # Connecting to the VK API.

    if not __is_allowed():
        # If not allowed to connect.

        # Returning.
        return

    # Making API, USER ID variable global.
    global API
    global USER_ID

    if __TOKEN is None:
        return

    # Connecting to the VK API.
    API = vk_api.VkApi(token=__TOKEN)

    # Getting current user index.
    USER_ID = api_users_get(None, "")["id"]


def method(_name: str, _params: dict) -> typing.Any:
    # Calling any API method.

    # Adding random id.
    _params.update({
        "random_id": vk_api.utils.get_random_id()
    })

    # Returning result.
    return API.method(
        _name,
        _params
    )


def method_exceed_limit(_name: str, _size_limit: int, _params: dict, _offset: typing.Optional[int] = None) -> \
        typing.Optional[list[typing.Any]]:
    # Calling any API method exceed its max size limit by checking count result.

    if _offset is None:
        # If offset is not set.

        # Default zero offset.
        _offset = 0

        if "count" in _params or "offset" in _params:
            # If not own call, and there is already COUNT or OFFSET params.

            # Message.
            print("[Debug][Warning] Trying to call method_exceed_limit with already passed count / offset values! "
                  "Please review this warning! Count / offset will be overwritten!")

    # Preparing params.
    _params["count"] = _size_limit
    _params["offset"] = _offset

    # Getting method result.
    _method_result = method_safe(_name, _params)

    if _method_result is None or "items" not in _method_result or "count" not in _method_result:
        # If response is None or no items / count fields.

        # Returning None.
        return None

    # How much items left.
    _items_left = _method_result["count"] - (_offset + _size_limit)

    if _items_left > 0:
        # If any item left.

        # Adding other from new request.
        _method_result["items"] += method_exceed_limit(_name, _size_limit, _params, _offset + _size_limit)

    # Returning result.
    return _method_result["items"]


def method_safe(_name: str, _params: dict) -> typing.Any:
    # Calling any API method.

    try:
        # Returning result.
        return method(
            _name,
            _params
        )
    except Exception:  # noqa
        # If error.

        # Returning none.
        return None


# API Functions.


# utils.resolveScreenName
def api_utils_resolve_screen_name(_screen_name: str) -> typing.Optional[int]:
    # Method utils.resolveScreenName.
    # Returns index (user, group) from its screen name

    # Getting response.
    _api_response = method("utils.resolveScreenName", {
        "screen_name": _screen_name
    })

    if "object_id" in _api_response:
        # If object ID in response.

        # Returning.
        return _api_response["object_id"]

    # Returning none.
    return None


# users.get.
def api_users_get(_user_ids: typing.Union[int, list[int], None], _fields: typing.Optional[str] = None) -> \
        typing.Union[dict, list[dict], None]:
    # Method users.get.
    # Returns information about users (user) from given user id(s)

    if _fields is None:
        # If fields argument is not set.

        # Default fields.
        _fields = "counters, sex, verified, bdate, contacts, screen_name"

    # Getting response.
    _api_response = method("users.get", {
        "user_ids": _user_ids,
        "fields": _fields
    })

    if len(_api_response) != 0:
        # If response is not empty.

        if len(_api_response) == 1:
            # If just one.

            # Returning first.
            return _api_response[0]

        # Returning list.
        return _api_response

    # Returning None if empty response.
    return None


# friends.get
def api_friends_get(_user_id: int) -> typing.Optional[list]:
    # Method friends.get.
    # Returns list with all user friends.

    # Getting response.
    _api_response = method_safe("friends.get", {
        "user_id": _user_id
    })

    if _api_response is not None and "items" in _api_response:
        # If response is not empty.

        # Returning list.
        return _api_response["items"]

    # Returning None if empty response.
    return None


# messages.send
def api_messages_send(_peer_id: int, _message: str) -> typing.Optional[int]:
    # Method messages.send.
    # Sends message.

    # Sending.
    return method_safe("messages.send", {
        "peer_id": _peer_id,
        "message": _message
    })


# groups.getById
def api_groups_get_by_id(_group_ids: list[int], _fields: str = "") -> typing.Optional[list[dict]]:
    # Method groups.getById.
    # Returns group information by its id.

    # Size limit.
    size_limit = 500

    if len(_group_ids) > size_limit:
        # If reached method limit.

        # Groups list.
        _groups = []

        for _group_ids_chunk in list(chunks(_group_ids, size_limit)):
            # For chunk with size_limit size.

            # Adding groups.
            _groups = [*_groups, *api_groups_get_by_id(_group_ids_chunk, _fields)]

        # Returning groups data.
        return _groups

    # Returning.
    return method_safe("groups.getById", {
        "group_id" if len(_group_ids) == 0 else "group_ids": ",".join([str(_group_id) for _group_id in _group_ids]),
        "fields": _fields
    })


# users.getSubscriptions
def api_users_get_subscriptions(_user_id: int, _extended: bool = True) -> typing.Optional[list[dict]]:
    # Method users.getSubscriptions.
    # Returns list of user subscriptions.

    # Returning.
    return method_exceed_limit("users.getSubscriptions", 200, {
        "user_id": _user_id,
        "extended": _extended,
    })


# groups.get
def api_groups_get(_user_id: int, _fields: str = "", _extended: bool = 1) -> typing.Optional[list[dict]]:
    # Method users.getSubscriptions.
    # Returns list of user groups.

    # Returning.
    return method_exceed_limit("groups.get", 200, {
        "user_id": _user_id,
        "extended": _extended,
        "fields": _fields
    })


# likes.getList
def api_likes_get_list(_owner_id: int, _item_id: int, _item_type: str,
                       _extended: bool = 1, _filter: str = "likes") -> list[dict]:
    # Method likes.getList.
    # Returns list of all likes of item.

    # Returning.
    return method_exceed_limit("likes.getList", 1000, {
        "owner_id": _owner_id,
        "item_id": _item_id,
        "type": _item_type,
        "filter": _filter,
        "extended": _extended,
    })


# wall.get
def api_wall_get(_user_id: int, _count: typing.Optional[int] = None) -> typing.Optional[list[dict]]:
    # Method wall.get.
    # Returns wall.

    if _count is None:
        # If get all.

        # Returning.
        return method_exceed_limit("wall.get", 100, {
            "owner_id": _user_id,
        })
    else:
        # If not all.

        # Getting result.
        _result = method_safe("wall.get", {
            "owner_id": _user_id,
            "count": _count
        })

        # Returning.
        return _result["items"] if _result is not None else None


# wall.getComments
def api_wall_get_comments(_owner_id: int, _post_id: int, _need_likes: bool = 1, _extended: bool = 1) -> list[dict]:
    # Method wall.getComments.
    # Returns comments.

    # README:
    # Yep, you may use there fields, but as i tried, this is don't work for me.

    # Returning.
    return method_exceed_limit("wall.getComments", 100, {
        "owner_id": _owner_id,
        "post_id": _post_id,
        "thread_items_count": 10,  # Wont change this as it API only, maximum.
        "extended": _extended,
        "need_likes": _need_likes
    })

# Entry point.


if not __is_authorized():
    # If token is not set.

    # Message.
    print("[Debug][VK] Token is not set! Please set your VK token. Exiting...")

    # Exiting.
    exit()
