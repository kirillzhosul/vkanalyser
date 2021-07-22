# Tests.


# Importing.


# Importing tests.
import unittest

# Importing tests.
import test_foaf
import test_utils


class Test(unittest.TestCase):
    # Test case.

    def test_foaf(self):
        # Testing FOAF.

        # Test.
        test_foaf.Test()

    def test_utils(self):
        # Testing utils.

        # Test.
        test_utils.Test()
