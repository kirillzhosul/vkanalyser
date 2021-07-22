# Tests.


# Importing.


# Importing tests.
import unittest

# Importing tests.
import test_foaf
import test_utils
import test_vk


class Test(unittest.TestCase):
    # Test case.

    def test_foaf(self):
        # Testing FOAF.

        # Test.
        suite = unittest.TestLoader().loadTestsFromModule(test_foaf)
        unittest.TextTestRunner(verbosity=2).run(suite)

    def test_utils(self):
        # Testing utils.

        # Test.
        suite = unittest.TestLoader().loadTestsFromModule(test_utils)
        unittest.TextTestRunner(verbosity=2).run(suite)

    def test_vk(self):
        # Testing vk.

        # Test.
        suite = unittest.TestLoader().loadTestsFromModule(test_vk)
        unittest.TextTestRunner(verbosity=2).run(suite)
