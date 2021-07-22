# VK Module tests.


# Importing.


# Importing tests.
from unittest import TestCase

# Importing vk.
import vk


# Tests.

class Test(TestCase):
    # Test case.

    def test_api_wall_get(self):
        # Testing vk.api_wall_get()

        # Getting wall.
        _wall = vk.api_wall_get(self.__test_group)

        for _post in _wall:
            # For every post.

            # Assert default fields.
            self.assertIn("id", _post)
            self.assertIn("from_id", _post)
            self.assertIn("owner_id", _post)
            self.assertIn("marked_as_ads", _post)
            self.assertIn("date", _post)
            self.assertIn("text", _post)
            self.assertIn("post_type", _post)
            self.assertIn("post_source", _post)
            self.assertIn("type", _post["post_source"])
            self.assertIn("comments", _post)
            self.assertIn("likes", _post)
            self.assertIn("reposts", _post)
            self.assertIn("is_favorite", _post)

            # Optional field for old posts.
            # self.assertIn("views", _post)

            # Comments.
            _comments = _post["comments"]
            self.assertIn("count", _comments)
            self.assertIn("can_post", _comments)
            self.assertIn("groups_can_post", _comments)

            # Likes.
            _likes = _post["likes"]
            self.assertIn("count", _likes)
            self.assertIn("user_likes", _likes)
            self.assertIn("can_like", _likes)
            self.assertIn("can_publish", _likes)

            # Reposts.
            _reposts = _post["reposts"]
            self.assertIn("count", _reposts)
            self.assertIn("user_reposted", _reposts)
            # Optional.
            # self.assertIn("can_publish", _reposts)
            # self.assertIn("views", _reposts)
            # self.assertIn("count", _reposts["views"])

    def test_api_wall_get_comments(self):
        # Testing vk.api_wall_get_comments()

        # Getting comments.
        _comments = vk.api_wall_get_comments(self.__test_group, self.__test_post)

        # Valid response.
        self.assertIsNotNone(_comments, "Can`t get comments from post!")

        # Default.
        self.assertGreater(len(_comments), 0, "Invalid comment amount!")

        for _comment in _comments:
            # For comment.

            # Assert default fields.
            self.assertIn("id", _comment)
            self.assertIn("from_id", _comment)
            self.assertIn("post_id", _comment)
            self.assertIn("owner_id", _comment)
            self.assertIn("parents_stack", _comment)
            self.assertIn("date", _comment)
            self.assertIn("text", _comment)
            self.assertIn("likes", _comment)
            self.assertIn("thread", _comment)

            # Asserting likes fields.
            _likes = _comment["likes"]
            self.assertIn("count", _likes)
            self.assertIn("user_likes", _likes)
            self.assertIn("can_like", _likes)

            # Asserting thread fields.
            _thread = _comment["thread"]
            self.assertIn("count", _thread)
            self.assertIn("items", _thread)
            self.assertIn("can_post", _thread)
            self.assertIn("show_reply_button", _thread)
            self.assertIn("groups_can_post", _thread)

    def test_api_utils_resolve_screen_name(self):
        # Testing vk.api_utils_resolve_screen_name()

        # Default.
        self.assertEqual(-vk.api_utils_resolve_screen_name("api_updates"), self.__test_group)

    def setUp(self) -> None:
        # Setup.

        self.__test_post = 4090
        self.__test_group = -28551727
        # Connecting.
        vk.connect()
