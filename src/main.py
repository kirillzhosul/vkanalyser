# Importing collections for counter.
from collections import Counter

# Importing time for measure time.
from time import time, sleep

# Import get env.
from os import getenv

# Importing random
from random import randint

# Importing VK API.
import vk_api, vk_api.utils, vk_api.longpoll
from vk_api.exceptions import AuthError 

# Parsing FOAF, Number validation.
import urllib.request, re, json

# Date.
import datetime

# Analyse.

def _analyse_user(_user_id: int, _fast: bool) -> dict:
    # Function that analyses page.

    # Getting FOAF results.
    print("[Debug][0] Loading user FOAF (foaf.php)...")
    _foaf_results = api_parse_user_foaf(_user_id)

    # Getting current user.
    print("[Debug][1] Loading user data...")
    _current_user = api_get_user(_user_id)
    _counters = _current_user["counters"]

    # Getting subscriptions.
    print("[Debug][2] Loading user subscriptions...")
    _subscriptions = api_get_subscriptions(_user_id)

    # Getting friends IDs.
    print("[Debug][3] Loading friends list...")
    _friends_ids = api_get_friends(_user_id)

    # Analyse results.
    print("[Debug][5] Making default analyse result...")
    _analyse_resulsts = {
        "potential_links": [],
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
        "user_phone_number_validation": None,
        "user_phone_number": None,
        "user_subscriptions_count": len(_subscriptions),
        "user_subscriptions_groups": len(api_get_groups(_user_id)),
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
        _, _counter, _counted = print("[Debug][6][0] Processing friends..."), 0, len(_friends_ids)
        for _friend_id in _friends_ids:
            # For every friend in friends ids.

            # Message.
            _counter += 1
            print(f"[Debug][6][1] Processing friend... ({_counter} / {_counted})")

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
                    print(f"[Debug][6][2] Found new potential relative {_user_formatted}!")

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
        _wall_posts = api_get_wall_posts(_user_id)

        # Message.
        _, _counter, _counted = print("[Debug][7][0] Processing wall posts..."), 0, len(_wall_posts)
        for _wall_post in _wall_posts:
            # For every post in wall.

            # Message.
            _counter += 1
            print(f"[Debug][7][1] Processing wall post... ({_counter} / {_counted})")
            
            # Analysing wall.
            _analyse_resulsts["user_wall_posts"] += 1
            _analyse_resulsts["user_wall_likes"] += _wall_post["likes"]["count"] if "likes" in _wall_post else 0
            _analyse_resulsts["user_wall_comments"] += _wall_post["comments"]["count"] if "comments" in _wall_post else 0
            _analyse_resulsts["user_wall_reposts"] += _wall_post["reposts"]["count"] if "reposts" in _wall_post else 0
            _analyse_resulsts["user_wall_views"] += _wall_post["views"]["count"] if "views" in _wall_post else 0

            # Getting likes and comments.
            _wall_likes = api_get_post_likes(_wall_post["owner_id"], _wall_post["id"])
            _wall_comments = api_get_post_comments(_wall_post["owner_id"], _wall_post["id"])

            for _comment in _analyse_parse_comments(_wall_comments):
                # For every comment in parsed.

                # Getting comment.
                _comment_creator = _comment["from"]
                _comment_likers = _comment["likes"]
                _comment_creator_last_name = _comment["from_last_name"]
                _comment_creator_id = _comment["from_id"]
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

                    if _comment_creator_id != _user_id and _comment_creator not in _analyse_resulsts["user_potential_relatives"]:
                        # If not already there and not self.

                        # Adding potential relatives.
                        _analyse_resulsts["user_potential_relatives"].append(_comment_creator)

                        # Message.
                        print(f"[Debug][7][2][0] Found new potential relative {_comment_creator}!")
                    
            for _user in _wall_likes:
                # For every user in wall likes.

                # Formatting user.
                _user_formatted = _analyse_format_user(_user["id"], _user["first_name"], _user["last_name"])

                if _user["last_name"] == _current_user["last_name"] or _user["last_name"] + "а" == _current_user["last_name"] or _user["last_name"] == _current_user["last_name"] + "а":
                    # If namesakes.

                    if str(_user["id"]) != str(_user_id) and _user_formatted not in _analyse_resulsts["user_potential_relatives"]:
                        # If not already there and not self.

                        # Adding potential relatives.
                        _analyse_resulsts["user_potential_relatives"].append(_user_formatted)

                        # Message.
                        print(f"[Debug][7][2][1] Found new potential relative {_user_formatted}!")
                    
                # Adding user as likers.
                _analyse_resulsts["wip_likers"].append(_user_formatted)

    # Most popular name.
    if len(_analyse_resulsts["wip_names"]) != 0:
        print("[Debug][8][0] Searching most popular name in friends...")
        _analyse_resulsts["friends_most_popular_name"] = max(set(_analyse_resulsts["wip_names"]), key = _analyse_resulsts["wip_names"].count)
        _analyse_resulsts["friends_most_popular_name_count"] = _analyse_resulsts["wip_names"].count(_analyse_resulsts["friends_most_popular_name"])

    # Top liker name.
    if len(_analyse_resulsts["wip_likers"]) != 0:
        print("[Debug][8][1] Searching most popular liker on wall...")
        _analyse_resulsts["top_liker_name"] = max(set(_analyse_resulsts["wip_likers"]), key = _analyse_resulsts["wip_likers"].count)
        _analyse_resulsts["top_liker_count"] = _analyse_resulsts["wip_likers"].count(_analyse_resulsts["top_liker_name"])
    
    # Top commentator name.
    if len(_analyse_resulsts["wip_commentators"]) != 0:
        print("[Debug][8][2] Searching most popular commentator on wall...")
        _analyse_resulsts["comments_most_popular_name"] = max(set(_analyse_resulsts["wip_commentators"]), key = _analyse_resulsts["wip_commentators"].count)
        _analyse_resulsts["comments_most_popular_count"] = _analyse_resulsts["wip_commentators"].count(_analyse_resulsts["comments_most_popular_name"])

    # Deep admin search.
    print("[Debug][9] Searching for administrated group...")
    _analyse_resulsts["user_admin_groups"] = _analyse_search_admin(_user_id)

    # Getting WIP comments most popular.
    _analyse_resulsts["comments_most_popular_from"], _analyse_resulsts["comments_most_popular_popularity"] = _analyse_resulsts["wip_most_popular_comment"]
        
    # Getting phone number.
    _phone_number = _current_user["mobile_phone"] if "mobile_phone" in _current_user else (_current_user["home_phone"] if "home_phone" in _current_user else None)

    # Converting phone number.
    try:
        _phone_number = int(_phone_number)
    except (ValueError, TypeError):
        _phone_number = None

    if _phone_number is not None:
        # If phone number is public.

        # Message.
        print("[Debug][10][0] Searching for phone number data (Numverify)...")

        # Adding phone number.
        _analyse_resulsts["user_phone_number"] = _phone_number

        # Getting phone nubmer data.
        _result = api_validate_phone_number(_phone_number)

        if _result is not None and _result != AuthError:
            # If all ok.

            # Message.
            print("[Debug][10][1] Founded phone number (Numverify)...")

            # Adding results.
            _analyse_resulsts["user_phone_number_validation"] = (_result['country_name'], _result['location'], _result['carrier'])
        else:
            if _result == AuthError:
                # If auth error.
                _analyse_resulsts["user_phone_number_validation"] = AuthError
            else:
                # Message.
                print("[Debug][10][2] Not founded any data about this phone number (Numverify)...")

    # Message.
    print("[Debug][11] Searching accounts links...")

    # Accounts search.
    _analyse_resulsts["potential_links"] = api_search_accounts(_current_user["screen_name"])

    for _group in _analyse_resulsts["user_admin_groups"]:
        # For every group.

        if str(_group[0]) in _group[1]:
            # If default name.
            continue

        # Accounts search.
        _analyse_resulsts["potential_links"] += api_search_accounts(_group[1])

    # Getting only formatted.
    _analyse_resulsts["user_admin_groups"] = [_group[2] for _group in _analyse_resulsts["user_admin_groups"]]

    # Clearing memory.
    del _subscriptions

    # Returning results.
    return _analyse_resulsts

def _analyse_search_admin(_user_id) -> list:
    # Generator that searchs for admin in contacts.

    def __process_group(_group: dict) -> None:
        # Function that process group.

        # Return if invalid
        if "contacts" not in _group:
            return

        for _ in [_contact for _contact in _group["contacts"] if "user_id" in _contact and _user_id == _contact["user_id"]]:
            # For every contact.

            # Formatting.
            _group_formatted = _analyse_format_group(_group["screen_name"], _group["name"])

            # Adding groups.
            _result.append((_group["id"], _group["screen_name"], _group_formatted))

            # Message.
            print(f"[Debug][Admin search] Found new group - {_group_formatted}!")

    # Result
    _result = []

    # Groups.
    _groups = []

    #for _subscription in api_get_subscriptions(_user_id): 
    #    # For every subscriptio
    #
    #    # Getting type.
    #    _type = _subscription["type"]
    #
    #    if _type == "page" or _type == "group":
    #        # If page or group.
    #
    #        # Adding group.
    #        _groups.append(_subscription["id"])
    #
    #_groups = [_group for _group in api_get_groups_contacts(_groups) if "contacts" in _group]
    #for _group in _groups: 
    #    # For every group.
    #
    #    # Process.
    #    __process_group(_group)

    # TODO: Should remove one of this loops?

    _groups = [_group for _group in api_get_groups(_user_id) if "contacts" in _group]
    for _group in _groups: 
        # For every group.

        # Process.
        __process_group(_group)

    # Deleting repeating.
    _result = list(set(_result))

    for _group in _result:
        # For every group.

        for _link in [_link for _link in api_get_group_links(_group[0]) if "vk.com/" in _link["url"]]:
            # For every link on vk.

            # Getting screen name.
            _screen_name = _link["url"].split("/")[-1]

            # Checking admin there.
            __process_group(api_get_groups_contacts([api_get_id_from_screen_name(_screen_name)])[0])

    # Deleting repeating.
    _result = list(set(_result))

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

        if _author is None:
            # If some error.

            # TODO: Fix communities.
            return [{
                "from": _comment["from_id"],
                "from_last_name": "UNDEFINED",
                "likes": [],
                "from_id": _comment["from_id"]
            }]

        # Getting comment.
        _result = [{
            "from": _analyse_format_user(_comment["from_id"], _author["first_name"], _author["last_name"]),
            "from_last_name": _author["last_name"],
            "likes": [],
            "from_id": _comment["from_id"]
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
        "[+][Анализатор][Профиль пользователя]"
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
        "[+] {0} ({4} Приватных, {1} групп, {2} страниц, {3} событий) подписок".format(_results["user_subscriptions_count"], _results["user_subscriptions_groups"], _results["user_subscriptions_pages"], _results["user_subscriptions_events"], _results["user_subscriptions_private"]),
    ]

    # Phone (Profile).
    if _results["user_phone_number"] is not None:
        # If phone exists.

        if _results["user_phone_number_validation"] == AuthError:
            # If auth error.
            
            # Lines.
            _results_lines += [
                "[+] Телефон: {0} (Авторизуйтесь для анализа)".format(_results["user_phone_number"])
            ]
        else:
            # If not auth error.

            if _results["user_phone_number_validation"] is None:
                # If phone validation error.

                # Adding.
                _results_lines += [
                    "[+] Телефон: {0}".format(_results["user_phone_number"])
                ]
            else:
                # If phone validated.

                # Adding.
                _results_lines += [
                    "[+] Телефон: {0} ({1} {2} {3})".format(_results["user_phone_number"], _results["user_phone_number_validation"][0], _results["user_phone_number_validation"][1], _results["user_phone_number_validation"][2]),
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
    if len(_results["user_potential_relatives"]) > 0:
        _results_lines += [
            "[--------] Родственники, Однофамильцы",
            "[+] Вероятные сходства: {0}".format(", ".join(_results["user_potential_relatives"]) if len(_results["user_potential_relatives"]) > 0 else "Не найдено"),
        ]

    # Admin in groups.
    if len(_results["user_admin_groups"]) > 0:
        _results_lines += [
            "[--------] Управление",
            "[+] Группы под управлением: {0}".format(", ".join(_results["user_admin_groups"]) if len(_results["user_admin_groups"]) > 0 else "Не найдено")
        ]

    # Potential links
    if len(_results["potential_links"]):
        _results_lines += [
            "[--------] Ссылки",
            "" if len(_results["potential_links"]) > 0 else "Не найдено"
        ]
        for _link in _results["potential_links"]:
            # For link.

            # Adding.
            _results_lines.append("[+] {1}".format(_link[0], _link[1]))
        
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

def api_get_id_from_screen_name(_screen_name: str) -> int:
    # Function that returns id from screen name.

    try:
        # Getting id.
        return API.method("utils.resolveScreenName",{
            "random_id": vk_api.utils.get_random_id(), 
            "screen_name": _screen_name, 
        })["object_id"] 
    except Exception:
        return None

def api_search_accounts(_nickname: str) -> list:
    # Function that search for account in other social networks.

    def __exists(_link: str, _timeout: int=2) -> bool:
        # Function that check is 404 or not.

        # Returning.
        try:
            return urllib.request.urlopen(urllib.request.Request(_link, headers = {'User-Agent': 'VK Analyser'}), timeout=_timeout).status != 404
        except:
            return False

    def __instagram() -> str:
        # Instagram account.
        
        # Getting url.
        _url = f"https://www.instagram.com/{_nickname}/"

        # Returning.
        return ("Instagram", _url) if __exists(_url, 5) else None

    def __facebook() -> str:
        # Facebook account.
        
        # Getting url.
        _url = f"https://www.facebook.com/{_nickname}/"

        # Returning.
        return ("Facebook", _url) if __exists(_url, 3) else None

    def __tiktok() -> str:
        # Tiktok account.

        # Getting url.
        _url = f"https://www.tiktok.com/@{_nickname}?"

        # Returning.
        return ("TikTok", _url) if __exists(_url, 5) else None

    def __odnoklassniki() -> str:
        # Odnoklassniki account.

        # Getting url.
        _url = f"https://ok.ru/{_nickname}"

        # Returning.
        return ("OK", _url) if __exists(_url, 2) else None

    def __github() -> str:
        # Github account.

        # Getting url.
        _url = f"https://github.com/{_nickname}"

        # Returning.
        return ("Github", _url) if __exists(_url, 4) else None
    
    def __steam() -> str:
        # Steam account.

        # Getting url.
        _url = f"https://steamcommunity.com/id/{_nickname}"

        # Returning.
        return ("Steam", _url) if __exists(_url, 5) else None

    def __twitter() -> str:
        # Twitter account.

        # Getting url.
        _url = f"https://twitter.com/{_nickname}"

        # Returning.
        return ("Twitter", _url) if __exists(_url, 3) else None

    def __twitch() -> str:
        # Twitch account.

        # Getting url.
        _url = f"https://www.twitch.tv/{_nickname}"

        # Returning.
        return ("Twitch", _url) if __exists(_url, 2) else None

    def __youtube() -> str:
        # YouTube account.

        # Getting url.
        _url = f"https://www.youtube.com/user/{_nickname}"

        # Returning.
        return ("OK", _url) if __exists(_url, 2) else None

    def __search() -> list:
        # Function that searchs for accounts.

        # Dont returns 404:
        # __twitch(), __steam(), __twitter()

        # Returning.
        return [__tiktok(), __instagram(), __facebook(), __odnoklassniki(), __youtube(), __github()]

    # Getting accounts.
    _accounts = [_account for _account in __search() if _account is not None]

    # Returning.
    return _accounts

def api_validate_phone_number(_number: int) -> dict:
    # Function that validates phone number and returns it to you.

    if NUMVERIFY_KEY is None:
        # If not set numverify key.

        # Returning.
        return AuthError

    with urllib.request.urlopen(f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={_number}&country_code=&format=1") as _response:
        # Opening.

        # Getting response.
        _result = _response.read()
        _result = json.loads(_result)

        if "error" in _result or not _result["valid"]:
            # If invalid 

            # Returning invalid.
            return None

        # Returning result.
        return _result

def api_get_user(_user_id: int, _fields: str="counters, sex, verified, bdate, contacts, screen_name") -> dict:
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

def api_get_groups_contacts(_group_ids: list) -> list:
    # Function that returns groups contacts
    
    # Getting contacts.
    _contacts = []

    for _chunk in list(chunks(_group_ids, 500)):
        # For every chunk with size 500.

        
        # Getting contacts.
        try:
            _current_contacts = API.method("groups.getById",{
                "random_id": vk_api.utils.get_random_id(), 
                "group_ids": ",".join([str(_group_id) for _group_id in _chunk]),
                "fields": "contacts"
            })
        except Exception:
            _current_contacts = []

        for _group in _current_contacts:
            # For every group.

            # Adding.
            _contacts.append(_group)

    # Returning.
    return _contacts

def api_get_group_links(_group_id: int) -> list:
    # Function that returns group links
    
    # Getting links.
    try:
        return API.method("groups.getById",{
            "random_id": vk_api.utils.get_random_id(), 
            "group_id": _group_id,
            "fields": "links"
        })[0]["links"]
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
            _groups["items"] = _groups["items"] + api_get_groups(_user_id, _offset + _max_count)
        
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

def api_chat_create(_user_id: int, _title: str) -> None:
    # Function that creates an new chat.

    # Creating chat.
    return API.method("messages.createChat", {
        "user_ids": _user_id, 
        "title": _title
    })

def api_chat_delete_history(_chat_id: int) -> None:
    # Function that deletes chat history.

    # Deleting.
    return API.method("messages.deleteConversation", {
        "user_id": _chat_id, 
        "peer_id": 2000000000 + _chat_id
    })

def api_chat_remove_user(_chat_id: int, _user_id: int) -> None:
    # Function that removes user from chat.

    # Remvoing user.
    return API.method("messages.removeChatUser", {
        "chat_id": _chat_id, 
        "user_id": _user_id
    })

def api_current_user_id() -> int:
    # Function that returns current user id.
    
    # Returning ID.
    return api_get_user(None, "")["id"]

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
            _likes["items"] += api_get_comment_likes(_owner_id, _item_id, _offset + _max_count)
        
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

    # Getting arguments.
    _arguments = _event.message.lower().split(" ")

    # Getting command.
    _command = _arguments[0]

    for _command_name, _command_function in COMMANDS.items():
        if _command.startswith(_command_name):
            # If commands exists.

            # Deleting command.
            _arguments.pop(0)

            # Execute command.
            _command_function(_event.user_id, _event.peer_id, _arguments)

# Commands.

def command_analyse(_user_id: int, _peer_id: int, _arguments: list) -> None:
    # Function for command analyse.
    
    # Fast disabled by default.
    _fast = False

    if len(_arguments) > 0:
        # If argument.
        
        # Getting user id.
        _user_id = _arguments[0]

        if len(_arguments) > 1:
            # If 2 arguments.

            # Setting fast mode.
            _fast = not _fast
    
    # Start message.
    api_send_message(_peer_id, f"[Анализатор] Анализ @id{_user_id}(профиля) успешно начат!" + (" (Быстрый режим, анализ друзей, стены отключён)" if _fast else ""))
    print(f"[Debug] Analysis https://vk.com/id{_user_id} started!")

    # Getting start time.
    _start_time = time()

    # Analysing.
    _analyse_results = _analyse_user(_user_id, _fast)

    # Results.
    api_send_message(_peer_id, f"{_analyse_format_results(_analyse_results, _fast)}")

    # End message.
    api_send_message(_peer_id, f"[Анализатор] Анализ @id{_user_id}(профиля) закончен! Потрачено: {int(time() - _start_time)}с!")
    print(f"[Debug] Analysis https://vk.com/id{_user_id} completed! Passed {int(time() - _start_time)}s!")

def command_validate_phone_number(_user_id: int, _peer_id: int, _arguments: list) -> None:
    # Function for command that validates phone number.

    if len(_arguments) > 0:
        # If argument.
        
        # Getting phone.
        _phone_number = _arguments[0]
    else:
        # Error.
        return api_send_message(_peer_id, f"[Анализатор] Укажите номер телефона для анализа!")

    # Converting phone number.
    try:
        _phone_number = int(_phone_number)
    except (ValueError, TypeError):
        return api_send_message(_peer_id, f"[Анализатор] Не корректный номер телефона!")

    # Getting phone nubmer data.
    _result = api_validate_phone_number(_phone_number)

    if _result is not None and _result != AuthError:
        # If all ok.

        # Success.
        return api_send_message(_peer_id, f"[Анализатор] Страна: {_result['country_name']},\n Локация: {_result['location']},\n Оператор: {_result['carrier']},\n")
    else:
        if _result == AuthError:
            # Error.
            return api_send_message(_peer_id, f"[Анализатор] Ошибка авторизации! Добавьте ключ в настройке!")
        else:
            # Error.
            return api_send_message(_peer_id, f"[Анализатор] Не удалось найти ничего об этом номере!")

def command_api_method(_user_id: int, _peer_id: int, _arguments: list) -> None:
    # Function for command that executes vk method.

    # Returning.
    return api_send_message(_peer_id, f"[Анализатор] Результат - {eval(' '.join(_arguments))}!")

def command_flood(_user_id: int, _peer_id: int, _arguments: list) -> None:
    # Function for command that floods with conversations.

    # Iterations.
    _iteration_size = 3
    _iteration_count = 10
    _sleep_time_min = 3
    _sleep_time_max = 10

    # Getting current user id.
    _current_user_id = api_current_user_id()

    # Message.
    print("[Debug][Flood] Started!")

    try:
        for _ in range(_iteration_count):
            for _ in range(_iteration_size):
                # Creating new chat with this user.
                _new_chat = api_chat_create(_user_id, f"Flood {randint(-9999999, +9999999)}")

                # Removing users.
                api_chat_remove_user(_new_chat, _user_id)
                api_chat_remove_user(_new_chat, _current_user_id)

                # Sending message.
                api_send_message(2000000000 + _new_chat, "Flood Script by @kirillzhosul!")

                # Deleting for self.
                api_chat_delete_history(_new_chat)

                # Message.
                print(f"[Debug][Flood] New chat {_new_chat} created!")

                # Sleeping.
                sleep(_sleep_time_min)

            # Sleeping.
            sleep(_sleep_time_max)
    except Exception as _exception:
        return api_send_message(_peer_id, f"[Анализатор][Флуд] Ошибка: {_exception}")

def command_search_accounts(_user_id: int, _peer_id: int, _arguments: list) -> None:
    # Function for command that searchs accounts

    if len(_arguments) == 0:
        # If arguments is not passed.

        # Returning.
        return api_send_message(_peer_id, "[Анализатор][Аккаунты] Вы не указали ник для поиска!")

    # Getting accounts.
    _accounts = [_account[0] + " = " + _account[1] for _account in api_search_accounts(_arguments[0])]

    # Returning.
    return api_send_message(_peer_id, f"[Анализатор][Аккаунты] Результат для ника {_arguments[0]}:\n" + ",\n".join(_accounts))

def command_help(_user_id: int, _peer_id: int, _arguments: list) -> None:
    # Function for command help

    # Returning.
    return api_send_message(_peer_id, f"[Анализатор] Команды:\n!анализ [id] [any=fastmode],\n!номер number,\n!метод [pycode],\n!флуд,\n!аккаунты [nickname],\n!помощь")

def command_groups_show_old(_user_id: int, _peer_id: int, _arguments: list) -> None:
    # Function for command groups old.

    # Result list.
    _groups_old = []
    _groups_ban = []

    # Max date.
    _date_max = 2021
    
    # Argument.
    if len(_arguments) > 0:
        _date_max = int(_arguments[0])

    # Message.
    api_send_message(_peer_id, f"[Анализатор][Группы] Анализ старых групп начат!")

    # Getting groups.
    _groups = api_get_groups(_user_id)

    # Current.
    _current = 0

    for _group in _groups:
        # For every group.

        # Message.
        _current += 1
        print(f"Group {_current} / {len(_groups)}")

        try:
            # Getting posts.
            _posts = API.method("wall.get", {
                "random_id": vk_api.utils.get_random_id(), 
                "owner_id": -_group["id"], 
                "count": 10
            })["items"]
        except:
            # If error.
            
            # Banned.
            _groups_ban.append(_analyse_format_group(_group["screen_name"], _group["name"]))
            continue

        if len(_posts) == 0:
            # If no posts.

            # Banned.
            _groups_ban.append(_analyse_format_group(_group["screen_name"], _group["name"]))
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
            _groups_old.append(_analyse_format_group(_group["screen_name"], _group["name"]))

    # Formatting.
    _groups_old = ", ".join(_groups_old)
    _groups_ban = ", ".join(_groups_ban)

    # Returning.
    return api_send_message(_peer_id, f"[Анализатор][Группы]\nСтарые (до {_date_max}):\n{_groups_old},\n Удалены или в бане или пустые:\n{_groups_ban}.")

# Other.

def chunks(_list: list, _size: int) -> list:
    # Function that chunks list.
    for _index in range(0, len(_list), _size):
        yield _list[_index:_index + _size]

# Connecting to the api.
API = vk_api.VkApi(token=getenv("VK_USER_TOKEN"))

# Key for nubmer verify.
# You may get this there: https://numverify.com/
NUMVERIFY_KEY = getenv("NUMVERIFY_KEY")

# Commands.
COMMANDS = {
    "!анализ": command_analyse,
    "!номер": command_validate_phone_number,
    "!метод": command_api_method,
    "!флуд": command_flood,
    "!аккаунты": command_search_accounts,
    "!помощь": command_help,
    "!группы_мусорные": command_groups_show_old,
}

# Message.
if NUMVERIFY_KEY is None:
    # If key is not set.

    # Message.
    print("[Debug] Numverify key is not set! Please add key if you want to analyse phone numbers!")

# Message.
print("[Debug] Launched!")

# Starting listener.
api_longpoll_listener(message_handler)