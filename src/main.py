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
    print("[Отладка] Получение и парсинг FOAF данных (foaf.php)...")
    _foaf_results = api_parse_user_foaf(_user_id)

    # Getting current user.
    print("[Отладка] Получение основных данных пользователя (users.get)...")
    _current_user = api_get_user(_user_id)
    _counters = _current_user["counters"]

    # Getting subscriptions.
    print("[Отладка] Получение подписок пользователя (subscriptions.get)...")
    _subscriptions = api_get_subscriptions(_user_id)

    # Getting friends IDs.
    print("[Отладка] Получение списка друзей пользователя (friends.get)...")
    _friends_ids = api_get_friends(_user_id)

    # Analyse results.
    print("[Отладка] Обработка полученных данных, создание словаря данных (dict)...")
    _analyse_resulsts = {
        "wip_names": [],
        "wip_likers": [],
        "wip_commentators": [],
        "wip_most_popular_comment": ("", 0),
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
        "user_wall_comments_likes": 0,
        "comments_most_popular_from": "",
        "comments_most_popular_popularity": 0,
        "comments_most_popular_name": "",
        "comments_most_popular_count": "",
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

    if not _fast and len(_friends_ids) != 0:
        # If not fast mode.

        # Message.
        _, _counter, _counted = print("[Отладка] Обработка каждого из друзей отдельно..."), 0, len(_friends_ids)
        for _friend_id in _friends_ids:
            # For every friend in friends ids.

            # Message.
            _counter += 1

            print(f"[Отладка] Получение друга и обработка... ({_counter} из {_counted})")

            # Getting friend data.
            _friend_data = api_get_user(_friend_id)

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
                _user_formatted = _analyse_format_user(_friend_data["id"], _friend_data["first_name"], _friend_data["last_name"])

                if _user_formatted not in _analyse_resulsts["user_potential_relatives"]:
                    # If not already there.

                    # Adding potential relatives.
                    _analyse_resulsts["user_potential_relatives"].append(_user_formatted)

                    # Message.
                    print(f"[Отладка] Успешно найден новый вероятный родственник {_user_formatted}!")

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
        # If user is not closed and not fast.

        # Getting all wall posts.
        print("[Отладка] Загрузка постов с страницы пользователя...")
        _wall_posts = api_get_wall_posts(_user_id)

        # Message.
        if len(_wall_posts) != 0:
            _, _counter, _counted = print("[Отладка] Обработка постов на стене..."), 0, len(_wall_posts)

        for _wall_post in _wall_posts:
            # For every post in wall.

            # Message.
            _counter += 1
            print(f"[Отладка] Получение поста и его данных (wall.get, wall.getComments, likes.getList)... ({_counter} из {_counted})")
            
            # Analysing wall.
            _analyse_resulsts["user_wall_posts"] += 1
            _analyse_resulsts["user_wall_likes"] += _wall_post["likes"]["count"] if "likes" in _wall_post else 0
            _analyse_resulsts["user_wall_comments"] += _wall_post["comments"]["count"] if "comments" in _wall_post else 0
            _analyse_resulsts["user_wall_reposts"] += _wall_post["reposts"]["count"] if "reposts" in _wall_post else 0
            _analyse_resulsts["user_wall_views"] += _wall_post["views"]["count"] if "views" in _wall_post else 0

            # Getting likes and comments.
            _wall_likes = api_get_post_likes(_wall_post["owner_id"], _wall_post["id"])
            _wall_comments = api_get_post_comments(_wall_post["owner_id"], _wall_post["id"])

            # Message.
            print(f"[Отладка] Обработка комментариев и лайков поста... ({_counter} из {_counted})")

            for _comment in _analyse_parse_comments(_wall_comments):
                # For every comment in parsed.

                # Getting comment.
                _comment_creator = _comment["from"]
                _comment_likers = _comment["likes"]
                _comment_creator_last_name = _comment["from_last_name"]
                _comment_likes = len(_comment_likers)

                if _comment_likes > _analyse_resulsts["wip_most_popular_comment"][1]:
                    # If new top comment.

                    # Adding most popular.
                    _analyse_resulsts["wip_most_popular_comment"] = (_comment_creator, _comment_likes)

                # Adding commentator.
                _analyse_resulsts["wip_commentators"].append(_comment_creator)

                # Adding user as likers.
                for _liker in _comment_likers:
                    # For likers.
                    
                    # Adding liker.
                    _analyse_resulsts["wip_likers"].append(_liker)

                # Adding likes.
                _analyse_resulsts["user_wall_comments_likes"] += _comment_likes

                if _comment_creator_last_name == _current_user["last_name"] or _comment_creator_last_name + "а" == _current_user["last_name"] or _comment_creator_last_name == _current_user["last_name"] + "а":
                    # If namesakes.

                    if _comment_creator_last_name != _user_id and _comment_creator not in _analyse_resulsts["user_potential_relatives"]:
                        # If not already there and not self.

                        # Adding potential relatives.
                        _analyse_resulsts["user_potential_relatives"].append(_comment_creator)

                        # Message.
                        print(f"[Отладка] Успешно найден новый вероятный родственник {_comment_creator}!")
                    
            for _user in _wall_likes:
                # For every user in wall likes.

                # Formatting user.
                _user_formatted = _analyse_format_user(_user["id"], _user["first_name"], _user["last_name"])

                if _user["last_name"] == _current_user["last_name"] or _user["last_name"] + "а" == _current_user["last_name"] or _user["last_name"] == _current_user["last_name"] + "а":
                    # If namesakes.

                    if _user["id"] != _user_id and _user_formatted not in _analyse_resulsts["user_potential_relatives"]:
                        # If not already there and not self.

                        # Adding potential relatives.
                        _analyse_resulsts["user_potential_relatives"].append(_user_formatted)

                        # Message.
                        print(f"[Отладка] Успешно найден новый вероятный родственник {_user_formatted}!")
                    
                # Adding user as likers.
                _analyse_resulsts["wip_likers"].append(_user_formatted)

    # Most popular name.
    if len(_analyse_resulsts["wip_names"]) != 0:
        print("[Отладка] Поиск самого популярного имени в друзьях...")
        _analyse_resulsts["friends_most_popular_name"] = max(set(_analyse_resulsts["wip_names"]), key = _analyse_resulsts["wip_names"].count)
        _analyse_resulsts["friends_most_popular_name_count"] = _analyse_resulsts["wip_names"].count(_analyse_resulsts["friends_most_popular_name"])

    # Top liker name.
    if len(_analyse_resulsts["wip_likers"]) != 0:
        print("[Отладка] Поиск самого популярного лайкера на стене...")
        _analyse_resulsts["top_liker_name"] = max(set(_analyse_resulsts["wip_likers"]), key = _analyse_resulsts["wip_likers"].count)
        _analyse_resulsts["top_liker_count"] = _analyse_resulsts["wip_likers"].count(_analyse_resulsts["top_liker_name"])
    
    # Top commentator name.
    if len(_analyse_resulsts["wip_commentators"]) != 0:
        print("[Отладка] Поиск самого популярного комментатора на стене...")
        _analyse_resulsts["comments_most_popular_name"] = max(set(_analyse_resulsts["wip_commentators"]), key = _analyse_resulsts["wip_commentators"].count)
        _analyse_resulsts["comments_most_popular_count"] = _analyse_resulsts["wip_commentators"].count(_analyse_resulsts["comments_most_popular_name"])

    # Deep admin search.
    print("[Отладка] Поиск факта администрации в группах (groups.get)...")
    _analyse_resulsts["user_admin_groups"] = _analyse_search_admin(_user_id)

    # Getting WIP comments most popular.
    _analyse_resulsts["comments_most_popular_from"], _analyse_resulsts["comments_most_popular_popularity"] = _analyse_resulsts["wip_most_popular_comment"]
        
    # Clearing memory.
    del _subscriptions

    # Returning results.
    return _analyse_resulsts

def _analyse_search_admin(_user_id) -> list:
    # Generator that searchs for admin in contacts.

    # Result
    _result = []

    for _group in [_group for _group in api_get_groups(_user_id) if "contacts" in _group]: 
        # For every group where current user in contacts.

        for _ in [_contact for _contact in _group["contacts"] if "user_id" in _contact and _user_id == _contact["user_id"]]:
            # For every contact.

            # Formatting.
            _group_formatted = _analyse_format_group(_group["screen_name"], _group["name"])

            # Adding groups.
            _result.append(_group_formatted)

            # Message.
            print(f"[Отладка] Успешно найдена новая группа в контактах - {_group_formatted}!")

    # Returning result.        
    return _result
   
def _analyse_parse_comments(_wall_comments: list) -> list:
    # Function that parses wall comments.

    # Authors cache.
    _cached_authors = {}

    def __parse_comment(_comment: dict) -> dict:
        # Sub function that parses comment.

        # There is also this fields (which may be used):
        # id, text, parents_stack

        # Loading user.
        if _comment["from_id"] not in _cached_authors:
            # If not cached.

            # Getting author.
            _author = api_get_user(_comment["from_id"])

            # Adding in cache.
            _cached_authors[_comment["from_id"]] = _author
        else:
            # If cached.

            # Getting cached author.
            _author = _cached_authors[_comment["from_id"]]

        # Getting comment.
        _result = [{
            "from": _analyse_format_user(_comment["from_id"], _author["first_name"], _author["last_name"]),
            "from_last_name": _author["last_name"],
            "likes": []
        }]

        if _comment["likes"]["count"] > 0:
            # If likes not 0.

            # Getting comment id.
            _comment_id = _comment["id"]
            
            # Getting likes
            _likes = api_get_comment_likes(_comment["owner_id"], _comment_id)

            for _liker in _likes:
                # For every user who left like.

                # Adding.
                _result[0]["likes"].append(_analyse_format_user(_liker["id"], _liker["first_name"], _liker["last_name"]))
    
        if "thread" in _comment and _comment["thread"]["count"] > 0:
            # If thread not null-size.

            for _thread_comment in _comment["thread"]["items"]:
                # For every comment.

                # Adding result to new.
                _result += __parse_comment(_thread_comment)

        # Returning.
        return _result

    # Parsed comments.
    _parsed_comments = []

    for _comment in _wall_comments:
        # For every comments.

        # Parsing.
        _parsed_comments += __parse_comment(_comment)

    # Deleting cached.
    del _cached_authors

    # Returning.
    return _parsed_comments

def _analyse_format_results(_results: dict, _fast: bool) -> str:
    # Function that formats analyse results.

    # Result lines.
    _results_lines = [
        "[+][Анализатор]",
    ]

    # Profile.
    _results_lines += [
        "[+] @id{0}({1})".format(_results["user_index"], _results["user_name"]),
        "[+] Пол: {0}".format(_results["user_sex"]),
        "[+] Профиль: {0}".format(_results["user_is_closed"]),
        "[+] Дата рождения: {0}".format(_results["user_birthdate"]),
        "[+] Регистрация: {0}".format(_results["user_registered_at"]),
        "[+] Был(а) в сети: {0}".format(_results["user_last_logged_in_at"]),
        "[+] Были изменения: {0}".format(_results["user_modified_at"]) if _results["user_modified_at"] != "" else "",
        "[+] Внешний доступ: {0}".format(_results["user_public_access"]),
        #"[+] Статус: {0}".format(_results["user_is_active"]),
        "[+] {0} друзей".format(_results["user_friends"]),
        "[+] {0} фотоальбомов".format(_results["user_albums"]) if _results["user_albums"] != 0 else "",
        "[+] {0} аудиозаписей".format(_results["user_audios"]) if _results["user_audios"] != 0 else "",
        "[+] {0} подарков".format(_results["user_gifts"]) if _results["user_gifts"] != 0 else "",
        "[+] {0} подписчиков".format(_results["user_followers"]) if _results["user_followers"] != 0 else "",
        "[+] {0}({4} Приватных, {1} групп, {2} страниц, {3} событий) подписок".format(_results["user_subscriptions_count"], _results["user_subscriptions_groups"], _results["user_subscriptions_pages"], _results["user_subscriptions_events"], _results["user_subscriptions_private"]),
    ]

    # Wall.
    if not _fast:
        _results_lines += [
            "[--------] Стена",
            "[+] {0} Постов".format(_results["user_wall_posts"]),
            "[+] {0} Просмотров".format(_results["user_wall_views"]),
            "[+] {0} Репостов".format(_results["user_wall_reposts"]),
            "[+] {0} Лайков".format(_results["user_wall_likes"]),
            "[+] {0} Комментариев".format(_results["user_wall_comments"]),
            "[+] {0} Лайков на всех комментариях".format(_results["user_wall_comments_likes"]),
            "[+] Самый популярный комментарий от {0} ({1} Лайков)".format(_results["comments_most_popular_from"], _results["comments_most_popular_popularity"]) if _results["comments_most_popular_from"] != "" else "",
            "[+] Больше всего комментариев от {0} (x{1})".format(_results["comments_most_popular_name"], _results["comments_most_popular_count"]) if _results["comments_most_popular_name"] != "" else "",
            "[+] Больше всего лайков от {0} (x{1})".format(_results["top_liker_name"], _results["top_liker_count"]) if _results["top_liker_name"] != "" else "",
        ]

    # Friends.
    if not _fast:
        _results_lines += [
            "[--------] Друзья",
            "[+] {0} видимых друзей".format(_results["user_friends"]),
            "[+] {0} удалены или забанены".format(_results["friends_deactivated"]),
            "[+] {0} закрыли профиль".format(_results["friends_closed"]),
            "[+] {0} верифицированные".format(_results["friends_verified"]),
            "[+] {0} мужчин и {1} женщин ({0}М/{1}Ж)".format(_results["friends_male"], _results["friends_female"]),
            "[+] Самое популярное имя - {} ({} Друзей)".format(_results["friends_most_popular_name"], _results["friends_most_popular_name_count"]) if _results["friends_most_popular_name"] != "" else "",
            "[--------] Подсчёт друзей",
            "[+] У всех друзей, в сумме",
            "[+] {0} друзей".format(_results["friends_of_friends"]),
            "[+] {0} фотоальбомов".format(_results["friends_albums"]),
            "[+] {0} аудиозаписей".format(_results["friends_audios"]),
            "[+] {0} подарков".format(_results["friends_gifts"]),
            "[+] {0} подписчиков".format(_results["friends_followers"]),
        ]

    # Potential relativies.
    _results_lines += [
        "[--------] Родственники, Однофамильцы",
        "[+] Вероятные сходства: {0}".format(", ".join(_results["user_potential_relatives"]) if len(_results["user_potential_relatives"]) > 0 else "Не найдено"),
    ]

    # Admin in groups.
    _results_lines += [
        "[--------] Управление",
        "[+] Группы под управлением: {0}".format(", ".join(_results["user_admin_groups"]) if len(_results["user_admin_groups"]) > 0 else "Не найдено")
    ]

    # Returning.
    return ",\n".join([_line for _line in _results_lines if _line != ""]) 

def _analyse_format_user(_id: int, _first_name: str, _last_name: str) -> str:
    # Function that format user link.

    # Returning formatted.
    return f"@id{_id}({_first_name} {_last_name})"

def _analyse_format_group(_screen_name: int, _group_name: str) -> str:
    # Function that format group link.

    # Returning formatted.
    return f"@{_screen_name}({_group_name})"

# API.

def api_get_user(_user_id: int, _fields: str="counters, sex, verified, bdate") -> dict:
    # Function that returns user data.
    try:
        # Getting user.
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
    try:
        _friends = API.method("friends.get",{
            "random_id": vk_api.utils.get_random_id(), 
            "user_id": _user_id
        })

        # Returning.
        return _friends["items"]
    except Exception:
        return []

def api_send_message(_peer_id: int, _message: str) -> any:
    # Function that sends message.

    # Sending.
    try:
        return API.method("messages.send",{
            "random_id": vk_api.utils.get_random_id(), 
            "peer_id": _peer_id, "message": _message
        })
    except Exception:
        return None

def api_longpoll_listener(_function) -> None:
    # Function that listens for longpool.
    for _event in vk_api.longpoll.VkLongPoll(API).listen():
        # For every event in longpoll.

        if _event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
            # If new message.

            # Calling function.
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
    _loggedin_at = "Скрыто через VK Me" if len(_loggedin_at) == 0 else _loggedin_at[0]
    _modified_at = re.findall(r'ya:modified dc:date="(.*)"', _user_xml)
    _modified_at = "" if len(_modified_at) == 0 else _modified_at[0]
    _public_access = re.findall(r'<ya:publicAccess>(.*)</ya:publicAccess>', _user_xml)[0]
    _profile_state = re.findall(r'<ya:profileState>(.*)</ya:profileState>', _user_xml)[0]

    # Returning.
    return _created_at, _loggedin_at, _modified_at, _public_access, _profile_state

def api_get_subscriptions(_user_id: int, _offset: int=0) -> list:
    # Function that returns list of subscriptions.

    # Max count for request.
    _max_count = 200

    try:
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
    except Exception:
        return []

def api_get_groups(_user_id: int, _offset: int=0) -> list:
    # Function that returns list of subscriptions.

    # Max count for request.
    _max_count = 200

    try:
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
    except Exception:
        return []

def api_get_wall_posts(_user_id: int, _offset: int=0) -> list:
    # Function that returns list of wall posts.

    # Max count for request.
    _max_count = 100

    # Getting subscriptions.
    try:
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
    except Exception:
        return []

def api_get_post_likes(_owner_id: int, _item_id: int, _offset: int=0) -> list:
    # Function that returns post likes list.

    # Max count for request.
    _max_count = 1000

    # Getting likes.
    try:
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
    except Exception:
        return []

def api_get_comment_likes(_owner_id: int, _item_id: int, _offset: int=0) -> list:
    # Function that returns post likes list.

    # Max count for request.
    _max_count = 1000

    # Getting likes.
    try:
        _likes = API.method("likes.getList",{
            "random_id": vk_api.utils.get_random_id(), 
            "type": "comment",
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
            _likes["items"] += api_get_post_likes(_owner_id, _item_id, _offset + _max_count)
        
        # Returning.
        return _likes["items"]
    except Exception:
        return []

def api_get_post_comments(_owner_id: int, _item_id: int, _offset: int=0) -> list:
    # Function that returns post comments list.

    # Max count for request.
    _max_count = 100

    # Getting comments.
    try:
        _comments = API.method("wall.getComments",{
            "random_id": vk_api.utils.get_random_id(), 
            "owner_id": _owner_id,
            "post_id": _item_id,
            "count": _max_count,
            "offset": _offset,
            "thread_items_count": 10,
            # This is dont work, i DONT KNOW why, in developer panel this have to work as i expect!
            #"fields": "first_name, last_name",
            "extended": 1,
            "need_likes": 1
        })

        if _comments["count"] - (_offset + _max_count) > 0:
            # If not all.

            # Adding other.
            _comments["items"] += api_get_post_comments(_owner_id, _item_id, _offset + _max_count)
        
        # Returning.
        return _comments["items"]
    except Exception:
        return []

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
    elif _event.message.lower().startswith("анализ_быстрый_для"):
        # If message starts with.

        # Analyse.
        command_analyse(int(_event.message[len("анализ_быстрый_для"):]), _event.peer_id, True)

def command_analyse(_user_id: int, _peer_id: int, _fast: bool=False) -> None:
    # Function for command analyse.
    
    # Start message.
    api_send_message(_peer_id, f"[Анализатор] Анализ @id{_user_id}(профиля) успешно начат!" + (" (Быстрый режим, анализ друзей, стены отключён)" if _fast else ""))
    print(f"[Отладка] Анализ https://vk.com/id{_user_id}!")

    # Getting start time.
    _start_time = time()

    # Analysing.
    _analyse_results = _analyse_user(_user_id, _fast)

    # Results.
    api_send_message(_peer_id, f"{_analyse_format_results(_analyse_results, _fast)}")

    # End message.
    api_send_message(_peer_id, f"[Анализатор] Анализ @id{_user_id}(профиля) закончен! Потрачено: {int(time() - _start_time)}с!")
    print(f"[Отладка] Анализ https://vk.com/id{_user_id} выполнен! Затрачено {int(time() - _start_time)}с!")

# Connecting to the api.
API = vk_api.VkApi(token=getenv("VK_USER_TOKEN"))

# Message.
print("[Отладка] Скрипт запущен")

# Starting listener.
api_longpoll_listener(message_handler)

# TODO:
# Photos scannning? Videos?
# FAST arguments should make users.get method work as group call, faster, less return values.
# Repair wall.getComments threading (sub comments feature)