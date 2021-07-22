# Utils Module tests.


# Importing.


# Importing tests.
from unittest import TestCase

# Importing utils.
import utils


# Tests.

class Test(TestCase):
    # Test case.

    def test_get_user_mention(self):
        # Testing utils.get_user_mention()

        # Default.
        self.assertEqual(utils.get_user_mention(1, "FName", "LName"), "@id1(FName LName)")

        # Blank.
        self.assertEqual(utils.get_user_mention(0, "", ""), "@id0()")

    def test_chat_to_peer_id(self):
        # Testing utils.chat_to_peer_id()

        # Defaults.
        self.assertEqual(utils.chat_to_peer_id(1), 2000000001)
        self.assertEqual(utils.chat_to_peer_id(2000000000), 4000000000)

        # Raises Value error?
        with self.assertRaises(ValueError):
            utils.chat_to_peer_id(-1)

    def test_get_group_mention(self):
        # Testing utils.get_group_mention()

        # Default.

        # Default.
        self.assertEqual(utils.get_group_mention("cool_screen_name", "cool_name"), "@cool_screen_name(cool_name)")

        # Blank.
        self.assertEqual(utils.get_group_mention("", ""), "@()")

    def test_chunks(self):
        # Testing utils.chunks()

        # Default.
        self.assertEqual(list(utils.chunks([1, 2, 3, 4], 2)), [[1, 2], [3, 4]])

        # Empty.
        self.assertEqual(list(utils.chunks([], 2)), [])

        # Not round.
        self.assertEqual(list(utils.chunks([1], 1000)), [[1]])
