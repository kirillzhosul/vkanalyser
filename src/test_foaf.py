# FOAF Module tests.


# Importing.


# Importing tests.
from unittest import TestCase

# Importing FOAF.
import foaf


# Tests.

class Test(TestCase):
    # Test case.

    def test_get(self):
        # Testing foaf.get()

        # Returns dict?
        self.assertIsInstance(foaf.get(1), dict)

        # Contains fields?
        self.assertIn("flag_state", foaf.get(2))
        self.assertIn("flag_access", foaf.get(3))
        self.assertIn("date_logged", foaf.get(4))
        self.assertIn("date_created", foaf.get(5))
        self.assertIn("date_modified", foaf.get(6))
        self.assertIn("person_name", foaf.get(7))

        # Raises Type error?
        with self.assertRaises(TypeError):
            foaf.get("string")

    def test_parse(self):
        # Testing foaf.parse()

        # Returns dict?
        self.assertIsInstance(foaf.parse(""), dict)

        # Raises Type error?
        with self.assertRaises(TypeError):
            foaf.parse(1)

    def test_load(self):
        # Testing foaf.load()

        # Contains default RDF, XML fields.
        self.assertIn("<rdf:RDF", foaf.load(1))
        self.assertIn("<?xml version=", foaf.load(2))

        # Raises Type error?
        with self.assertRaises(TypeError):
            foaf.load("string")

    def test_profile_state(self):
        # Testing foaf.ProfileState enum.

        # Checking fields.
        self.assertEquals(foaf.ProfileState.active, foaf.ProfileState["active"])
        self.assertEquals(foaf.ProfileState.banned, foaf.ProfileState["banned"])
        self.assertEquals(foaf.ProfileState.deactivated, foaf.ProfileState["deactivated"])
        self.assertEquals(foaf.ProfileState.deleted, foaf.ProfileState["deleted"])
        self.assertEquals(foaf.ProfileState.verified, foaf.ProfileState["verified"])

    def test_profile_access(self):
        # Testing foaf.ProfileAccess enum.

        # Checking fields.
        self.assertEquals(foaf.ProfileAccess.disallowed, foaf.ProfileAccess["disallowed"])
        self.assertEquals(foaf.ProfileAccess.allowed, foaf.ProfileAccess["allowed"])
