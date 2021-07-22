# Analyse.

import phone
import foaf
import accounts
import utils
import vk

def analyse_user(_user_id: int, _fast: bool) -> dict:
    # Function that analyses page.

    _user_id = int(_user_id)

    # Getting FOAF results.
    print("[Debug][0] Loading user FOAF (foaf.php)...")
    _foaf_results = foaf.get(_user_id)

    # Getting current user.
    print("[Debug][1] Loading user data...")
    _current_user = vk.api_users_get(_user_id)
    _counters = _current_user["counters"]

    # Getting subscriptions.
    print("[Debug][2] Loading user subscriptions...")
    _subscriptions = vk.api_users_get_subscriptions(_user_id)

    # Getting friends IDs.
    print("[Debug][3] Loading friends list...")
    _friends_ids = vk.api_friends_get(_user_id)

    if _friends_ids is None:
        _friends_ids = []

    # Analyse results.
    print("[Debug][5] Making default analyse result...")
    _analyse_results = {
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
        "user_is_closed": "закрытый" if _current_user["is_closed"] else "открытый",
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
        "user_subscriptions_groups": len(vk.api_groups_get(_user_id)),
        "user_subscriptions_pages": len(
            [_subscription for _subscription in _subscriptions if _subscription["type"] == "page"]),
        "user_subscriptions_events": len(
            [_subscription for _subscription in _subscriptions if _subscription["type"] == "event"]),
        "user_subscriptions_private": len([_subscription for _subscription in _subscriptions if
                                           ("is_closed" in _subscription and _subscription["is_closed"])]),
        "user_birthdate": _current_user["bdate"] if "bdate" in _current_user else "НЕИЗВЕСТНО",
        "user_name": _current_user["first_name"] + " " + _current_user["last_name"],
        "user_sex": "Мужской" if _current_user["sex"] == 2 else (
            "Женский" if _current_user["sex"] == 1 else "Не указан"),
        "user_index": _user_id,
        "user_registered_at": _foaf_results["date_created"],
        "user_last_logged_in_at": _foaf_results["date_logged"],
        "user_modified_at": _foaf_results["date_modified"],
        "user_public_access": "открыт" if _foaf_results["flag_access"] == foaf.ProfileAccess.allowed else "закрыт",
        "user_is_active": "активный" if _foaf_results["flag_state"] == foaf.ProfileState.active else "деактивирован",
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
            _friend_data = vk.api_users_get(_friend_id)

            if _friend_data is None:
                # If invalid user.

                # Pass.
                continue

            if "deactivated" in _friend_data:
                # If deactivated.

                # Adding.
                _analyse_results["friends_deactivated"] += 1

            if "counters" not in _friend_data:
                # If invalid result.

                # Pass.
                continue

            # Getting counters.
            _counters = _friend_data["counters"]

            if utils.is_namesakes(_current_user["last_name"], _friend_data["last_name"]):
                # If namesakes.

                # Formatting user.
                _user_formatted = utils.get_user_mention(_friend_data["id"], _friend_data["first_name"],
                                                       _friend_data["last_name"])

                if _user_formatted not in _analyse_results["user_potential_relatives"]:
                    # If not already there.

                    # Adding potential relatives.
                    _analyse_results["user_potential_relatives"].append(_user_formatted)

                    # Message.
                    print(f"[Debug][6][2] Found new potential relative {_user_formatted}!")

            # Counters etc.
            _analyse_results["friends_closed"] += _friend_data["is_closed"]
            _analyse_results["friends_verified"] += _friend_data["verified"]
            _analyse_results["friends_of_friends"] += _counters["friends"] if "friends" in _counters else 0
            _analyse_results["friends_albums"] += _counters["albums"] if "albums" in _counters else 0
            _analyse_results["friends_audios"] += _counters["audios"] if "audios" in _counters else 0
            _analyse_results["friends_gifts"] += _counters["gifts"] if "gifts" in _counters else 0
            _analyse_results["friends_followers"] += _counters["followers"] if "followers" in _counters else 0
            _analyse_results["friends_male"] += (_friend_data["sex"] == 2)
            _analyse_results["friends_female"] += (_friend_data["sex"] == 1)

            # Adding first name.
            _analyse_results["wip_names"].append(_friend_data["first_name"])

    if _current_user["can_access_closed"] and not _fast:
        # If user is not closed and not fast.

        # Getting all wall posts.
        _wall_posts = vk.api_wall_get(_user_id)

        # Message.
        _, _counter, _counted = print("[Debug][7][0] Processing wall posts..."), 0, len(_wall_posts)
        for _wall_post in _wall_posts:
            # For every post in wall.

            # Message.
            _counter += 1
            print(f"[Debug][7][1] Processing wall post... ({_counter} / {_counted})")

            # Analysing wall.
            _analyse_results["user_wall_posts"] += 1
            _analyse_results["user_wall_likes"] += _wall_post["likes"]["count"] if "likes" in _wall_post else 0
            _analyse_results["user_wall_comments"] += _wall_post["comments"][
                "count"] if "comments" in _wall_post else 0
            _analyse_results["user_wall_reposts"] += _wall_post["reposts"]["count"] if "reposts" in _wall_post else 0
            _analyse_results["user_wall_views"] += _wall_post["views"]["count"] if "views" in _wall_post else 0

            # Getting likes and comments.
            _wall_likes = vk.api_likes_get_list(_wall_post["owner_id"], _wall_post["id"], "post")
            _wall_comments = vk.api_wall_get_comments(_wall_post["owner_id"], _wall_post["id"])

            for _comment in _analyse_parse_comments(_wall_comments):
                # For every comment in parsed.

                # Getting comment.
                _comment_creator = _comment["from"]
                _comment_likers = _comment["likes"]
                _comment_creator_last_name = _comment["from_last_name"]
                _comment_creator_id = _comment["from_id"]
                _comment_likes = len(_comment_likers)

                if _comment_likes > _analyse_results["wip_most_popular_comment"][1]:
                    # If new top comment.

                    # Adding most popular.
                    _analyse_results["wip_most_popular_comment"] = (_comment_creator, _comment_likes)

                # Adding commentator.
                _analyse_results["wip_commentators"].append(_comment_creator)

                # Adding user as likers.
                for _liker in _comment_likers:
                    # For likers.

                    # Adding liker.
                    _analyse_results["wip_likers"].append(_liker)

                # Adding likes.
                _analyse_results["user_wall_comments_likes"] += _comment_likes

                if utils.is_namesakes(_current_user["last_name"], _comment_creator_last_name):
                    # If namesakes.

                    if _comment_creator_id != _user_id and \
                            _comment_creator not in _analyse_results["user_potential_relatives"]:
                        # If not already there and not self.

                        # Adding potential relatives.
                        _analyse_results["user_potential_relatives"].append(_comment_creator)

                        # Message.
                        print(f"[Debug][7][2][0] Found new potential relative {_comment_creator}!")

            for _user in _wall_likes:
                # For every user in wall likes.

                # Formatting user.
                _user_formatted = utils.get_user_mention(_user["id"], _user["first_name"], _user["last_name"])

                if utils.is_namesakes(_current_user["last_name"], _user["last_name"]):
                    # If namesakes.

                    if str(_user["id"]) != str(_user_id) and \
                            _user_formatted not in _analyse_results["user_potential_relatives"]:
                        # If not already there and not self.

                        # Adding potential relatives.
                        _analyse_results["user_potential_relatives"].append(_user_formatted)

                        # Message.
                        print(f"[Debug][7][2][1] Found new potential relative {_user_formatted}!")

                # Adding user as likers.
                _analyse_results["wip_likers"].append(_user_formatted)

    # Most popular name.
    if len(_analyse_results["wip_names"]) != 0:
        print("[Debug][8][0] Searching most popular name in friends...")
        _analyse_results["friends_most_popular_name"] = max(set(_analyse_results["wip_names"]),  key=_analyse_results["wip_names"].count)
        _analyse_results["friends_most_popular_name_count"] = _analyse_results["wip_names"].count(_analyse_results["friends_most_popular_name"])

    # Top liker name.
    if len(_analyse_results["wip_likers"]) != 0:
        print("[Debug][8][1] Searching most popular liker on wall...")
        _analyse_results["top_liker_name"] = max(set(_analyse_results["wip_likers"]),
                                                  key=_analyse_results["wip_likers"].count)
        _analyse_results["top_liker_count"] = _analyse_results["wip_likers"].count(
            _analyse_results["top_liker_name"])

    # Top commentator name.
    if len(_analyse_results["wip_commentators"]) != 0:
        print("[Debug][8][2] Searching most popular commentator on wall...")
        _analyse_results["comments_most_popular_name"] = max(set(_analyse_results["wip_commentators"]), key=_analyse_results["wip_commentators"].count)
        _analyse_results["comments_most_popular_count"] = _analyse_results["wip_commentators"].count(_analyse_results["comments_most_popular_name"])

    # Deep admin search.
    print("[Debug][9] Searching for administrated group...")
    _analyse_results["user_admin_groups"] = _analyse_search_admin(_user_id)

    # Getting WIP comments most popular.
    _analyse_results["comments_most_popular_from"], _analyse_results["comments_most_popular_popularity"] = \
        _analyse_results["wip_most_popular_comment"]

    # Getting phone number.
    _phone_number = _current_user["mobile_phone"] if "mobile_phone" in _current_user else (
        _current_user["home_phone"] if "home_phone" in _current_user else None)

    # Converting phone number.
    try:
        _phone_number = int(_phone_number)
    except (ValueError, TypeError):
        _phone_number = None

    if _phone_number is not None:
        # If phone number is public.

        # Adding phone number.
        _analyse_results["user_phone_number"] = _phone_number

        if phone.is_enabled():
            # If enabled phones.

            # Message.
            print("[Debug][10][0] Searching for phone number data (Numverify)...")

            # Getting phone number data.
            _result = phone.lookup(_phone_number)

            if _result is not None:
                # If all ok.

                # Message.
                print("[Debug][10][1] Founded phone number (Numverify)...")

                # Adding results.
                _analyse_results["user_phone_number_validation"] = (
                    _result['country_name'], _result['location'], _result['carrier'])
            else:
                # Message.
                print("[Debug][10][2] Not founded any data about this phone number (Numverify)...")
    # Message.
    print("[Debug][11] Searching accounts links...")

    # Accounts search.
    _analyse_results["potential_links"] = accounts.search(_current_user["screen_name"])

    for _group in _analyse_results["user_admin_groups"]:
        # For every group.

        if str(_group[0]) in _group[1]:
            # If default name.
            continue

        # Accounts search.
        _analyse_results["potential_links"] += accounts.search(_group[1])

    # Getting only formatted.
    _analyse_results["user_admin_groups"] = [_group[2] for _group in _analyse_results["user_admin_groups"]]

    # Clearing memory.
    del _subscriptions

    # Returning results.
    return _analyse_results


def _analyse_search_admin(_user_id) -> list:
    # Generator that searches for admin in contacts.

    def __process_group(_group: dict) -> None:
        # Function that process group.

        # Return if invalid
        if "contacts" not in _group:
            return

        for _ in [_contact for _contact in _group["contacts"] if
                  "user_id" in _contact and _user_id == _contact["user_id"]]:
            # For every contact.

            # Formatting.
            _group_formatted = utils.get_group_mention(_group["screen_name"], _group["name"])

            # Adding groups.
            _result.append((_group["id"], _group["screen_name"], _group_formatted))

            # Message.
            print(f"[Debug][Admin search] Found new group - {_group_formatted}!")

    # Result
    _result = []

    # Groups.
    _groups = []

    # for _subscription in api_get_subscriptions(_user_id):
    #    # For every subscription
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
    # _groups = [_group for _group in api_get_groups_contacts(_groups) if "contacts" in _group]
    # for _group in _groups:
    #    # For every group.
    #
    #    # Process.
    #    __process_group(_group)

    # TODO: Should remove one of this loops?

    _groups = [_group for _group in vk.api_groups_get(_user_id) if "contacts" in _group]
    for _group in _groups:
        # For every group.

        # Process.
        __process_group(_group)

    # Deleting repeating.
    _result = list(set(_result))

    for _group in _result:
        # For every group.

        _links = vk.api_groups_get_by_id([_group[0]], "links")[0]["links"]

        if _links is None:
            continue

        for _link in [_link for _link in _links if "vk.com/" in _link["url"]]:
            # For every link on vk.

            # Getting screen name.
            _screen_name = _link["url"].split("/")[-1]

            # Getting contacts.
            _group = vk.api_groups_get_by_id([vk.api_utils_resolve_screen_name(_screen_name)], "contacts")

            if _group is not None:
                # If not none.

                # Checking admin there.
                __process_group(_group[0])

    # Deleting repeating.
    _result = list(set(_result))

    # Returning result.
    return _result


def _analyse_parse_comments(_wall_comments: list) -> list:
    # Function that parses wall comments.

    # Authors cache.
    _cached_authors = {}

    def __parse_comment(_comment: dict) -> list:
        # Sub function that parses comment.

        # There is also this fields (which may be used):
        # id, text, parents_stack

        # Loading user.
        if _comment["from_id"] not in _cached_authors:
            # If not cached.

            # Getting author.
            _author = vk.api_users_get(_comment["from_id"])

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
            "from": utils.get_user_mention(_comment["from_id"], _author["first_name"], _author["last_name"]),
            "from_last_name": _author["last_name"],
            "likes": [],
            "from_id": _comment["from_id"]
        }]

        if _comment["likes"]["count"] > 0:
            # If likes not 0.

            # Getting comment id.
            _comment_id = _comment["id"]

            # Getting likes
            _likes = vk.api_likes_get_list(_comment["owner_id"], _comment_id, "comment")

            for _liker in _likes:
                # For every user who left like.

                # Adding.
                _result[0]["likes"].append(
                    utils.get_user_mention(_liker["id"], _liker["first_name"], _liker["last_name"]))

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


def analyse_format_results(_results: dict, _fast: bool) -> str:
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
        # "[+] Статус: {0}".format(_results["user_is_active"]),
        "[+] {0} друзей".format(_results["user_friends"]),
        "[+] {0} фотоальбомов".format(_results["user_albums"]) if _results["user_albums"] != 0 else "",
        "[+] {0} аудиозаписей".format(_results["user_audios"]) if _results["user_audios"] != 0 else "",
        "[+] {0} подарков".format(_results["user_gifts"]) if _results["user_gifts"] != 0 else "",
        "[+] {0} подписчиков".format(_results["user_followers"]) if _results["user_followers"] != 0 else "",
        "[+] {0} ({4} Приватных, {1} групп, {2} страниц, {3} событий) подписок".format(
            _results["user_subscriptions_count"], _results["user_subscriptions_groups"],
            _results["user_subscriptions_pages"], _results["user_subscriptions_events"],
            _results["user_subscriptions_private"]),
    ]

    # Phone (Profile).
    if _results["user_phone_number"] is not None:
        # If phone exists.

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
                "[+] Телефон: {0} ({1} {2} {3})".format(_results["user_phone_number"],
                                                        _results["user_phone_number_validation"][0],
                                                        _results["user_phone_number_validation"][1],
                                                        _results["user_phone_number_validation"][2]),
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
            "[+] Самый популярный комментарий от {0} ({1} Лайков)".format(_results["comments_most_popular_from"],
                                                                          _results[
                                                                              "comments_most_popular_popularity"]) if
            _results["comments_most_popular_from"] != "" else "",
            "[+] Больше всего комментариев от {0} (x{1})".format(_results["comments_most_popular_name"],
                                                                 _results["comments_most_popular_count"]) if _results["comments_most_popular_name"] != "" else "",
            "[+] Больше всего лайков от {0} (x{1})".format(_results["top_liker_name"], _results["top_liker_count"]) if
            _results["top_liker_name"] != "" else "",
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
            "[+] Самое популярное имя - {} ({} Друзей)".format(_results["friends_most_popular_name"],
                                                               _results["friends_most_popular_name_count"]) if _results["friends_most_popular_name"] != "" else "",
            "[--------] Подсчёт друзей",
            "[+] У всех друзей, в сумме",
            "[+] {0} друзей".format(_results["friends_of_friends"]),
            "[+] {0} фотоальбомов".format(_results["friends_albums"]),
            "[+] {0} аудиозаписей".format(_results["friends_audios"]),
            "[+] {0} подарков".format(_results["friends_gifts"]),
            "[+] {0} подписчиков".format(_results["friends_followers"]),
        ]

    # Potential relatives.
    if len(_results["user_potential_relatives"]) > 0:
        _results_lines += [
            "[--------] Родственники, Однофамильцы",
            "[+] Вероятные сходства: {0}".format(", ".join(_results["user_potential_relatives"]) if len(
                _results["user_potential_relatives"]) > 0 else "Не найдено"),
        ]

    # Admin in groups.
    if len(_results["user_admin_groups"]) > 0:
        _results_lines += [
            "[--------] Управление",
            "[+] Группы под управлением: {0}".format(
                ", ".join(_results["user_admin_groups"]) if len(_results["user_admin_groups"]) > 0 else "Не найдено")
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

