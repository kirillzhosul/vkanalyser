# Module VK for working with commands (handling it).


# Importing.

# Importing time for measuring execution time.
from time import time

# Typing for types.
import typing

# Date (for command clean_groups).
import datetime

# Local modules.
import accounts
import vk
import utils
import phone
import analyse


# Functions.

def execute(_user_id, _peer_id, _command, _arguments) -> typing.Optional[str]:
    # Execute command and return string result or None if not found.

    for _command_name, _command_function in COMMANDS.items():
        # Iterating over commands.

        if _command.startswith(_command_name):
            # If commands exists.

            # Message.
            print(f"[Debug] Executing command {_command} with arguments {_arguments}.")

            # Execute command and return result.
            return _command_function(_user_id, _peer_id, _arguments)

    # Not found.
    return None


def message_handler(_event) -> typing.NoReturn:
    # Handles vk message event.

    # Getting arguments.
    _arguments = _event.message.lower().split(" ")

    # Getting command.
    _command = _arguments[0]
    _arguments.pop(0)

    if any([_command.startswith(_command_name) for _command_name in COMMANDS.keys()]):
        # If command exists.

        # Getting execution result.
        _execution_result = execute(_event.user_id, _event.peer_id, _command, _arguments)

        if _execution_result is not None:
            # Additional check.

            # Sending message.
            vk.api_messages_send(_event.peer_id, _execution_result)


# Commands itself.

def lookup_phone_number(_user_id: int, _peer_id: int, _arguments: list) -> str:
    # Command that lookup phone number.

    if not phone.is_enabled():
        # If not enabled.

        # Error.
        return f"[Анализатор][Телефон] Работа с номерами отключена, включите работу в модуле phone."

    # Getting phone number.
    _phone_number, *_ = *_arguments, None

    if _phone_number is None:
        # If phone is not given.

        # Error.
        return f"[Анализатор][Телефон] Укажите номер телефона для анализа!"

    try:
        # Converting phone number.
        _phone_number = int(_phone_number)
    except (ValueError, TypeError):
        # If error.

        # Error.
        return f"[Анализатор][Телефон] Не корректный номер телефона!"

    # Getting phone number data.
    _result = phone.lookup(_phone_number)

    # Grabbing values.
    _country, _location, _carrier = _result['country_name'], _result['location'], _result['carrier']

    if _result is not None:
        # If all ok.

        # Success.
        return f"[Анализатор][Телефон]\n" \
               f"Страна: {_country},\n " \
               f"Локация: {_location},\n " \
               f"Оператор: {_carrier},\n"
    else:
        # Error.
        return f"[Анализатор][Телефон] Не удалось найти ничего об этом номере!"


def search_accounts(_user_id: int, _peer_id: int, _arguments: list[int]) -> str:
    # Command that searches for account.

    if len(_arguments) == 0:
        # If arguments is not passed.

        # Returning.
        return "[Анализатор][Аккаунты] Вы не указали ник для поиска! Использование: !аккаунты ник"

    # Getting nickname.
    _nickname, *_ = *_arguments,

    # Getting accounts.
    _accounts = ",\n".join([_account[0] + ": " + _account[1] for _account in accounts.search(_nickname)])

    # Returning.
    return f"[Анализатор][Аккаунты] Результат для ника {_nickname}:\n{_accounts}"


def clean_groups(_user_id: int, _peer_id: int, _arguments: list):
    # Command that shows old groups.

    # Result list.
    _groups_old = []

    # Max date for post.
    _date_max, *_ = *_arguments, 2021
    _date_max = int(_date_max)

    # Start message..
    vk.api_messages_send(_peer_id, f"[Анализатор][Группы] Анализ старых групп начат (Посты до {_date_max})!")

    # Getting groups.
    _groups = vk.api_groups_get(_user_id)

    if _groups is not None:
        # If groups exists.

        # Current and total progress of processing.
        _current_progress = 0
        _total_progress = len(_groups)

        for _group in _groups:
            # For every group.

            # Message.
            _current_progress += 1
            print(f"[Debug][Cleaner] Progress {int(_current_progress / _total_progress * 100)}%")

            # Getting posts.
            _posts = vk.api_wall_get(-_group["id"], 10)

            if _posts is None or len(_posts) == 0:
                # If no posts or error.

                # Passing.
                continue

            # Date max iteration.
            _date_max_ = 1970

            for _post in _posts:
                # For every post.

                # Getting date.
                _date = int(datetime.datetime.fromtimestamp(_post["date"]).strftime('%Y-%m-%d %H:%M:%S')[:4])

                if _date > _date_max_:
                    # If new biggest.

                    # Setting.
                    _date_max_ = _date
            if _date_max_ < _date_max:
                # If old.

                # Old.
                _groups_old.append(utils.get_group_mention(_group["screen_name"], _group["name"]))

        if len(_groups_old) == 0:
            # If empty.

            # Returning.
            return f"[Анализатор][Группы]\nУра! У вас нет старых групп."

        # Formatting.
        _groups_old = ", ".join(_groups_old)

        # Returning.
        return f"[Анализатор][Группы]\nЭти группы не выкладывали постов ничего после {_date_max - 1}:\n{_groups_old}."
    else:
        # If cant get groups.

        # Returning errors.
        return f"[Анализатор][Группы]\nНе удалось получить группы (API)!"


def get_user_indices(_user_id: int, _peer_id: int, _arguments: list) -> str:
    # Function for command get user indices.

    # Returning.
    return f"[Анализатор] Индекс профиля: {_user_id},\nИндекс переписки: {_peer_id}."


def api_method(_user_id: int, _peer_id: int, _arguments: list) -> str:
    # Function for command that executes vk method.

    if len(_arguments) == 0:
        # If empty arguments.

        # Error.
        return "[Анализатор][API] Вы не указали запрос!"

    # Getting source.
    _method = " ".join(_arguments)

    # Result.
    try:
        if _method.startswith("!*"):
            # If unsafe.

            # Result.
            _result = eval(_method[len('!*'):])
        elif _method.startswith("[]"):
            # If exceed limit

            # Result.
            _result = eval(f"vk.method_exceed_limit({_method[len('[]'):]})")
        else:
            # If safe

            # Result.
            _result = eval(f"vk.method_safe({_method[len('[]'):]})")
    except Exception as _exception:
        # If error.

        # Exception.
        _result = f"Исключение - {_exception}"

    # Returning.
    return f"[Анализатор][API] Результат - {_result}!"


def help_commands(_user_id: int, _peer_id: int, _arguments: list) -> str:
    # Command help.

    # Returning.
    return "\n".join([f"{_command[0]}\n" for _command in [
        [
            "[Анализатор] Справка по командам:"
        ],
        [
            "!анализ_профиль [быстрый_режим(y|n)] [индекс], "
            "Анализирует профиль, если индекс не указан, то анализ профиля собеседника переписки. "
            "Быстрый режим ускоряет сканирования, отключая емкие сканы."
        ],
        [
            "!помощь, "
            "Показывает справку,"
        ],
        [
            "!индексы, "
            "Показывает индексы (user, peer) профиля владельца ЛС. "
        ],
        [
            "!анализ_телефон [номер], "
            "Анализирует номер телефона (Оператор, регион и т.д)."
        ],
        [
            "!api [(!*)([]) запрос], "
            "Исполняет метод API, не используйте если не разбираетесь!,"
        ],
        [
            "!анализ_аккаунты [ник], "
            "Делает поиск аккаунтов с заданным никнеймом. "
        ],
        [
            "!чистка_групп [год], "
            "Показывает список групп владельца ЛС, "
            "которые не выкладывали ничего после указанного года (мертвые группы). "
            "Если не указан, будет выбран 2021 год"
        ]
    ]])


def analyse_profile(_user_id: int, _peer_id: int, _arguments: list) -> str:
    # Function for command analyse.

    # Getting arguments.
    _fast_mode, _user_id, *_ = *_arguments, "n", _user_id
    _fast_mode = _fast_mode == "y"
    _user_id = int(_user_id)

    # Getting mention.
    _mention = utils.get_user_mention(_user_id, 'профиля')

    # Fast mode warning.
    _fast_mode_warning = " (Быстрый режим, емкие сканирования отключены)" if _fast_mode else ""

    # Start message.
    vk.api_messages_send(_peer_id, f"[Анализатор][Профиль] Анализ {_mention} начат! {_fast_mode_warning}")
    print(f"[Debug] Analysing https://vk.com/id{_user_id} started!")

    # Getting start time.
    _start_time = time()

    # Analysing.
    _analyse_results = analyse.analyse_user(_user_id, _fast_mode)

    # Getting elapsed time.
    _elapsed_time = int(time() - _start_time)

    # Results message..
    vk.api_messages_send(_peer_id, f"{analyse.analyse_format_results(_analyse_results, _fast_mode)}")
    print(f"[Debug] Analysis https://vk.com/id{_user_id} completed! Passed {_elapsed_time}s!")

    # End message.
    return f"[Анализатор] Анализ {_mention} окончен! Потрачено: {_elapsed_time}с!"


# Settings.

# Commands for executing.
COMMANDS = {
    "!анализ_телефон": lookup_phone_number,
    "!анализ_профиль": analyse_profile,
    "!анализ_аккаунты": search_accounts,

    "!чистка_групп": clean_groups,
    "!индексы": get_user_indices,

    "!api": api_method,
    "!помощь": help_commands
}
