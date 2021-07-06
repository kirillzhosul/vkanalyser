# Importing collections for counter.
from collections import Counter

# Importing time for measure time.
from time import time

# Import get env.
from os import getenv

# Importing VK API.
import vk_api, vk_api.utils, vk_api.longpoll 

# Parsing FOAF.
import urllib.request, re

# Analyse.

def _analyse_user(_user_id: int, _fast: bool) -> dict:
    # Function that analyses page.

    # Getting FOAF results.
    print("[Отладка] Обработка FOAF данных...")
    _foaf_results = api_parse_user_foaf(_user_id)

    # Getting current user.
    print("[Отладка] Получение основных данных...")
    _current_user = api_get_user(_user_id)
    _counters = _current_user["counters"]

    # Getting subscriptions.
    print("[Отладка] Получение подписок...")
    _subscriptions = api_get_subscriptions(_user_id)

    # Getting friends IDs.
    print("[Отладка] Получение друзей...")
    _friends_ids = api_get_friends(_user_id)

    # Analyse results.
    print("[Отладка] Создание данных анализа...")
    _analyse_resulsts = {
        "wip_names": [],
        "wip_likers": [],
        "user_potential_relatives": [],
        "user_friends": _counters["friends"] if "friends" in _counters else 0,
        "user_albums": _counters["albums"] if "albums" in _counters else 0,
        "user_gifts": _counters["gifts"] if "gifts" in _counters else 0,
        "user_followers": _counters["followers"] if "followers" in _counters else 0, 
        "user_audios": _counters["audios"] if "audios" in _counters else 0,
        "user_is_closed": "закрытый" if _current_user["is_closed"] else "окрытый",
        "friends_deactivated": 0,
        "friends_closed": 0, 
        "friends_verified": 0, 
        "friends_of_friends": 0, 
        "friends_albums": 0, 
        "friends_audios": 0, 
        "friends_gifts": 0, 
        "friends_followers": 0,
        "friends_male": 0,
        "friends_female": 0,
        "user_wall_posts": 0,
        "user_wall_likes": 0,
        "user_wall_comments": 0,
        "user_wall_reposts": 0,
        "user_wall_views": 0,
        "friends_most_popular_name": "",
        "friends_most_popular_name_count": 0,
        "top_liker_name": "Нет",
        "top_liker_count": 0,
        "user_admin_groups": [],
        "user_subscriptions_count": len(_subscriptions),
        "user_subscriptions_groups": len([_subscription for _subscription in _subscriptions if _subscription["type"] == "group"]),
        "user_subscriptions_pages":  len([_subscription for _subscription in _subscriptions if _subscription["type"] == "page"]),
        "user_subscriptions_events":  len([_subscription for _subscription in _subscriptions if _subscription["type"] == "event"]),
        "user_subscriptions_private": len([_subscription for _subscription in _subscriptions if ("is_closed" in _subscription and _subscription["is_closed"])]),
        "user_birthdate": _current_user["bdate"] if "bdate" in _current_user else "НЕИЗВЕСТНО",
        "user_name": _current_user["first_name"] + " " + _current_user["last_name"],
        "user_sex": "Мужской" if _current_user["sex"] == 2 else ("Женский" if _current_user["sex"] == 1 else "Не указан"),
        "user_index": _user_id,
        "user_registered_at": _foaf_results[0],
        "user_last_logged_in_at": _foaf_results[1],
        "user_modified_at": _foaf_results[2],
        "user_public_access": "открыт" if _foaf_results[3] == "allowed" else "закрыт",
        "user_is_active": "активный" if _foaf_results[4] == "active" else "деактивирован",
    }

    # Message.
    _, _counter, _counted = print("[Отладка] Обработка друзей..."), 0, len(_friends_ids)
    if not _fast:
        for _friend_id in _friends_ids:
            # For every friend in friends ids.

            # Getting friend data.
            _friend_data = api_get_user(_friend_id)

            # Message.
            _counter += 1
            print(f"[Отладка] Обработка друга {_counter} из {_counted}")

            if _friend_data is None:
                # If invalid user.

                # Pass.
                continue

            if "deactivated" in _friend_data:
                # If deactivated.

                # Adding.
                _analyse_resulsts["friends_deactivated"] += 1

            if "counters" not in _friend_data:
                # If invalid result.

                # Pass.
                continue

            # Getting counters.
            _counters = _friend_data["counters"]

            if _friend_data["last_name"] == _current_user["last_name"] or _friend_data["last_name"] + "а" == _current_user["last_name"] or _friend_data["last_name"] == _current_user["last_name"] + "а":
                # If namesakes.

                # Formatting user.
                _user_formatted = "@id" + str(_friend_data["id"]) + "(" + _friend_data["first_name"] + " " + _friend_data["last_name"] + ")"

                if _user_formatted not in _analyse_resulsts["user_potential_relatives"]:
                    # If not already there.

                    # Adding potential relatives.
                    _analyse_resulsts["user_potential_relatives"].append(_user_formatted)

            # Counters etc.
            _analyse_resulsts["friends_closed"] += _friend_data["is_closed"]
            _analyse_resulsts["friends_verified"] += _friend_data["verified"]
            _analyse_resulsts["friends_of_friends"] += _counters["friends"] if "friends" in _counters else 0
            _analyse_resulsts["friends_albums"] += _counters["albums"] if "albums" in _counters else 0
            _analyse_resulsts["friends_audios"] += _counters["audios"] if "audios" in _counters else 0 
            _analyse_resulsts["friends_gifts"] += _counters["gifts"] if "gifts" in _counters else 0
            _analyse_resulsts["friends_followers"] += _counters["followers"] if "followers" in _counters else 0
            _analyse_resulsts["friends_male"] += (_friend_data["sex"] == 2)
            _analyse_resulsts["friends_female"] += (_friend_data["sex"] == 1)

            # Adding first name.
            _analyse_resulsts["wip_names"].append(_friend_data["first_name"])

    if _current_user["can_access_closed"] and not _fast:
        # If user is not closed.

        # Getting all wall posts.
        _wall_posts = api_get_wall_posts(_user_id)

        # Message.
        _, _counter, _counted = print("[Отладка] Обработка постов на стене..."), 0, len(_wall_posts)

        for _wall_post in _wall_posts:
            # For every post in wall.

            # Message.
            _counter += 1
            print(f"[Отладка] Обработка поста {_counter} из {_counted}")
            
            # Analysing wall.
            _analyse_resulsts["user_wall_posts"] += 1
            _analyse_resulsts["user_wall_likes"] += _wall_post["likes"]["count"] if "likes" in _wall_post else 0
            _analyse_resulsts["user_wall_comments"] += _wall_post["comments"]["count"] if "comments" in _wall_post else 0
            _analyse_resulsts["user_wall_reposts"] += _wall_post["reposts"]["count"] if "reposts" in _wall_post else 0
            _analyse_resulsts["user_wall_views"] += _wall_post["views"]["count"] if "views" in _wall_post else 0

            # Getting likes.
            _wall_likes = api_get_post_likes(_wall_post["owner_id"], _wall_post["id"])

            for _user in _wall_likes:
                # For every user in wall likes.

                # Formatting user.
                _user_formatted = "@id" + str(_user["id"]) + "(" + _user["first_name"] + " " + _user["last_name"] + ")"

                if _user["last_name"] == _current_user["last_name"] or _user["last_name"] + "а" == _current_user["last_name"] or _user["last_name"] == _current_user["last_name"] + "а":
                    # If namesakes.

                    # Passing if id is same.
                    if _user["id"] != _user_id:
                        if _user_formatted not in _analyse_resulsts["user_potential_relatives"]:
                            # If not already there.

                            # Adding potential relatives.
                            _analyse_resulsts["user_potential_relatives"].append(_user_formatted)

                # Adding user as likers.
                _analyse_resulsts["wip_likers"].append(_user_formatted)

    # Most popular name.
    if len(_analyse_resulsts["wip_names"]) != 0:
        print("[Отладка] Обработка самого популярного имени в друзьях...")
        _analyse_resulsts["friends_most_popular_name"] = max(set(_analyse_resulsts["wip_names"]), key = _analyse_resulsts["wip_names"].count)
        _analyse_resulsts["friends_most_popular_name_count"] = _analyse_resulsts["wip_names"].count(_analyse_resulsts["friends_most_popular_name"])

    # Top liker name.
    if len(_analyse_resulsts["wip_likers"]) != 0:
        print("[Отладка] Обработка самого популярного лайкера...")
        _analyse_resulsts["top_liker_name"] = max(set(_analyse_resulsts["wip_likers"]), key = _analyse_resulsts["wip_likers"].count)
        _analyse_resulsts["top_liker_count"] = _analyse_resulsts["wip_likers"].count(_analyse_resulsts["top_liker_name"])
    
    # Deep admin search.
    print("[Отладка] Обработка глубокого поиска администратора...")
    for _group in api_get_groups(_user_id):
        # For every group where current user in contacts.

        # Pass if not in contacts.
        if "contacts" not in _group:
            continue

        for _contact in _group["contacts"]:
            # For every contact.

            if "user_id" in _contact and _user_id == _contact["user_id"]:
                # If contacts.

                # Adding groups.
                _analyse_resulsts["user_admin_groups"].append("@" + _group["screen_name"] + "(" +_group["name"] + ")")

    # Clearing memory.
    del _subscriptions

    # Returning results.
    return _analyse_resulsts

def _analyse_format_results(_results: dict) -> str:
    # Function that formats analyse results.

    # Result lines.
    _results_lines = [_line for _line in [
        "[+][Анализатор]",
        "======= Профиль",
        "[+] {0} (@id{1})".format(_results["user_name"], _results["user_index"]),
        "[+] Пол: {0}".format(_results["user_sex"]),
        "[+] Профиль: {0}".format(_results["user_is_closed"]),
        "[+] Дата рождения: {0} числа".format(_results["user_birthdate"]),
        "[+] В ВКонтакте с: {0}".format(_results["user_registered_at"]),
        "[+] Был(а) в сети: {0}".format(_results["user_last_logged_in_at"]),
        "[+] Были изменения: {0}".format(_results["user_modified_at"]),
        "[+] Доступ: {0}".format(_results["user_public_access"]),
        "[+] Статус: {0}".format(_results["user_is_active"]),
        "[+] {0} друзей".format(_results["user_friends"]),
        "[+] {0} фотоальбомов".format(_results["user_albums"]),
        "[+] {0} аудиозаписей".format(_results["user_audios"]),
        "[+] {0} подарков".format(_results["user_gifts"]),
        "[+] {0} подписчиков".format(_results["user_followers"]),
        "======= Подписки",
        "[+] {0} подписок из которых {1} групп, {2} страниц и {3} событий(приватных - {4})".format(_results["user_subscriptions_count"], _results["user_subscriptions_groups"], _results["user_subscriptions_pages"], _results["user_subscriptions_events"], _results["user_subscriptions_private"]),
        "======= Стена",
        "[+] {0} Постов".format(_results["user_wall_posts"]),
        "[+] {0} Просмотров".format(_results["user_wall_views"]),
        "[+] {0} Репостов".format(_results["user_wall_reposts"]),
        "[+] {0} Лайков".format(_results["user_wall_likes"]),
        "[+] {0} Комментариев".format(_results["user_wall_comments"]),
        "[+] Больше всего лайков от {0} ({1} Лайков)".format(_results["top_liker_name"], _results["top_liker_count"]),
        "======= Друзья",
        "[+] {0} друзей (Не скрытые)".format(_results["user_friends"]),
        "[+] Из них {0} удалены или забанены".format(_results["friends_deactivated"]),
        "[+] Из них {0} закрыли профиль".format(_results["friends_closed"]),
        "[+] Из них {0} это профили с 'галочкой'".format(_results["friends_verified"]),
        "[+] У них в сумме",
        "[+] {0} друзей".format(_results["friends_of_friends"]),
        "[+] {0} фотоальбомов".format(_results["friends_albums"]),
        "[+] {0} аудиозаписей".format(_results["friends_audios"]),
        "[+] {0} подарков".format(_results["friends_gifts"]),
        "[+] {0} подписчиков".format(_results["friends_followers"]),
        "[+] {0} мужчин и {1} женщин в друзьях ({0}М/{1}Ж)".format(_results["friends_male"], _results["friends_female"]),
        "[+] Самое популярное имя среди друзей - {} ({} Друзей)".format(_results["friends_most_popular_name"], _results["friends_most_popular_name_count"]),
        "======= Родственники",
        "[+] Вероятные родственники: {0}".format(", ".join(_results["user_potential_relatives"]) if len(_results["user_potential_relatives"]) > 0 else "Не найдено"),
        "======= Управление",
        "[+] Группы под управлением: {0}".format(", ".join(_results["user_admin_groups"]) if len(_results["user_admin_groups"]) > 0 else "Не найдено"),
    ] if _line != ""]
    
    # Returning.
    return ",\n".join(_results_lines) 

# API.

def api_get_user(_user_id: int, _fields: str="counters, sex, verified, bdate") -> dict:
    # Function that returns user data.
    try:
        # Gettin user.
        return API.method("users.get",{
            "random_id": vk_api.utils.get_random_id(), 
            "user_ids": _user_id, 
            "fields": _fields
        })[0]
    except Exception:
        return None

def api_get_friends(_user_id: int) -> list:
    # Function that returns friends list and count,
    
    # Getting friends.
    _friends = API.method("friends.get",{
        "random_id": vk_api.utils.get_random_id(), 
        "user_id": _user_id
    })

    # Returning.
    return _friends["items"]

def api_send_message(_peer_id: int, _message: str) -> any:
    # Function that sends message.

    # Sending.
    return API.method("messages.send",{
        "random_id": vk_api.utils.get_random_id(), 
        "peer_id": _peer_id, "message": _message
    })

def api_longpoll_listener(_function) -> None:
    # Function that listens for longpool.
    for _event in vk_api.longpoll.VkLongPoll(API).listen():
        if _event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
            _function(_event)

def api_parse_user_foaf(_user_id: int): 
    # Function that parses FOAF.

    # Getting user FOAF link.
    _user_foaf_link = f"https://vk.com/foaf.php?id={_user_id}"
    _user_foaf_code = "windows-1251"

    with urllib.request.urlopen(_user_foaf_link) as _response:
        # Opening.

        # Getting XML, decoding.
        _user_xml = _response.read().decode(_user_foaf_code)

    # Parsing xml.
    _created_at = re.findall(r'ya:created dc:date="(.*)"', _user_xml)[0]
    _loggedin_at = re.findall(r'ya:lastLoggedIn dc:date="(.*)"', _user_xml)
    _loggedin_at = "СКРЫТО" if len(_loggedin_at) == 0 else _loggedin_at[0]
    _modified_at = re.findall(r'ya:modified dc:date="(.*)"', _user_xml)
    _modified_at = "НЕ УКАЗАНО" if len(_modified_at) == 0 else _modified_at[0]
    _public_access = re.findall(r'<ya:publicAccess>(.*)</ya:publicAccess>', _user_xml)[0]
    _profile_state = re.findall(r'<ya:profileState>(.*)</ya:profileState>', _user_xml)[0]

    # Returning.
    return _created_at, _loggedin_at, _modified_at, _public_access, _profile_state

def api_get_subscriptions(_user_id: int, _offset: int=0) -> list:
    # Function that returns list of subscriptions.

    # Max count for request.
    _max_count = 200

    # Getting subscriptions.
    _subscriptions = API.method("users.getSubscriptions",{
        "random_id": vk_api.utils.get_random_id(), 
        "user_id": _user_id,
        "extended": 1,
        "count": _max_count,
        "offset": _offset,
    })

    if _subscriptions["count"] - (_offset + _max_count) > 0:
        # If not all.

        # Adding other.
        _subscriptions["items"] = _subscriptions["items"] + api_get_subscriptions(_user_id, _offset + _max_count)
    
    # Returning.
    return _subscriptions["items"]

def api_get_groups(_user_id: int, _offset: int=0) -> list:
    # Function that returns list of subscriptions.

    # Max count for request.
    _max_count = 200

    # Getting subscriptions.
    _groups = API.method("groups.get",{
        "random_id": vk_api.utils.get_random_id(), 
        "user_id": _user_id,
        "extended": 1,
        "count": _max_count,
        "offset": _offset,
        "fields": "contacts"
    })

    if _groups["count"] - (_offset + _max_count) > 0:
        # If not all.

        # Adding other.
        _groups["items"] = _groups["items"] + api_get_subscriptions(_user_id, _offset + _max_count)
    
    # Returning.
    return _groups["items"]

def api_get_wall_posts(_user_id: int, _offset: int=0) -> list:
    # Function that returns list of wall posts.

    # Max count for request.
    _max_count = 100

    # Getting subscriptions.
    _posts = API.method("wall.get",{
        "random_id": vk_api.utils.get_random_id(), 
        "owner_id": _user_id,
        "count": _max_count,
        "offset": _offset,
    })

    if _posts["count"] - (_offset + _max_count) > 0:
        # If not all.

        # Adding other.
        _posts["items"] = _posts["items"] + api_get_wall_posts(_user_id, _offset + _max_count)
    
    # Returning.
    return  _posts["items"]

def api_get_post_likes(_owner_id: int, _item_id: int, _offset: int=0) -> list:
    # Function that returns post likes list.

    # Max count for request.
    _max_count = 1000

    # Getting subscriptions.
    _likes = API.method("likes.getList",{
        "random_id": vk_api.utils.get_random_id(), 
        "type": "post",
        "owner_id": _owner_id,
        "item_id": _item_id,
        "filter": "likes",
        "count": _max_count,
        "offset": _offset,
        "extended": 1,
    })

    if _likes["count"] - (_offset + _max_count) > 0:
        # If not all.

        # Adding other.
        _likes["items"] = _likes["items"] + api_get_post_likes(_owner_id, _item_id, _offset + _max_count)
    
    # Returning.
    return _likes["items"]

# Messages.

def message_handler(_event) -> None:
    # Function that handles message.

    if _event.message.lower() == "анализ":
        # If message starts with.

        # Analyse.
        command_analyse(_event.user_id, _event.peer_id)
    elif _event.message.lower() == "анализ_быстрый":
        # If message starts with.

        # Analyse.
        command_analyse(_event.user_id, _event.peer_id, True)
    elif _event.message.lower().startswith("анализ_для"):
        # If message starts with.

        # Analyse.
        command_analyse(int(_event.message[len("анализ_для"):]), _event.peer_id)

def command_analyse(_user_id: int, _peer_id: int, _fast: bool=False) -> None:
    # Function for command analyse.
    
    #_user_id = 599326371

    # Start message.
    api_send_message(_peer_id, f"[Анализатор] Анализ успешно начат! Время ожидания должно быть не более часа! Индекс пользователя запустившего анализ: @id{_user_id}")
    if _fast:
        api_send_message(_peer_id, f"[Анализатор] Выбран быстрый режим, в этом режиме друзья и посты не включены в анализ!")
    print(f"[Отладка] Запрос на анализ от @id{_user_id} принят!")

    # Getting start time.
    _start_time = time()

    # Analysing.
    _analyse_results = _analyse_user(_user_id, _fast)

    # Results.
    api_send_message(_peer_id, f"{_analyse_format_results(_analyse_results)}")

    # End message.
    api_send_message(_peer_id, f"[Анализатор] Анализ успешно закончен! Время ожидания составило: {int(time() - _start_time)}с!")
    print(f"[Отладка] Запрос на анализ от @id{_user_id} выполнен! Затрачено: {int(time() - _start_time)}с!")

# Connecting to the api.
API = vk_api.VkApi(token=getenv("VK_USER_TOKEN"))

# Starting listener.
api_longpoll_listener(message_handler)

# TODO:
# Поиск родственников в комментариях.