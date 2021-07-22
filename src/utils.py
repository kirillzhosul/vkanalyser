# Utils module for working with utils.


# Functions.


def get_user_mention(_index: int, _first_name: str, _last_name: str) -> str:
    # Function that returns vk mention for user.

    # Returning formatted.
    return f"@id{_index}({_first_name} {_last_name})"


def get_group_mention(_screen_name: str, _group_name: str) -> str:
    # Function that returns vk mention for group.

    # Returning formatted.
    return f"@{_screen_name}({_group_name})"


def chat_to_peer_id(_chat_id: int) -> int:
    # Function that converts chat id to peer id.

    if _chat_id < 0:
        # If negative.

        # Value Error.
        raise ValueError("Not allowed to use negative numbers!")

    # Returning.
    return 2000000000 + _chat_id


def chunks(_list: list, _size: int) -> list:
    # Function that chunks list.

    # Chunking.
    for _index in range(0, len(_list), _size):
        yield _list[_index:_index + _size]
