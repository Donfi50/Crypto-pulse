import tempfile
import unittest
from pathlib import Path

import createlab_auth
import createlab_db


class AccountAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_and_case_insensitive_login(self):
        user = createlab_auth.register("Person@Example.com", "Person", "correct horse battery", self.db_path)
        signed_in = createlab_auth.authenticate("person@example.com", "correct horse battery", self.db_path)
        self.assertEqual(signed_in["id"], user["id"])
        self.assertNotIn("password_hash", signed_in)

    def test_bad_password_does_not_authenticate(self):
        createlab_auth.register("person@example.com", "Person", "correct horse battery", self.db_path)
        self.assertIsNone(createlab_auth.authenticate("person@example.com", "wrong password", self.db_path))
        self.assertIsNone(createlab_auth.authenticate("missing@example.com", "wrong password", self.db_path))

    def test_registration_validates_password_and_email(self):
        with self.assertRaises(ValueError):
            createlab_auth.register("invalid", "Person", "short", self.db_path)

    def test_password_hash_uses_salt(self):
        first = createlab_auth.hash_password("same password")
        second = createlab_auth.hash_password("same password")
        self.assertNotEqual(first, second)
        self.assertTrue(createlab_auth.verify_password("same password", first))
        self.assertFalse(createlab_auth.verify_password("wrong password", first))


if __name__ == "__main__":
    unittest.main()
