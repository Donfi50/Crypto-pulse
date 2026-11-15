import tempfile
import unittest
from pathlib import Path

import createlab_db


class CreationDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        createlab_db.initialize_database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def creation(self, creation_id="one", kind="Game"):
        return {
            "id": creation_id,
            "kind": kind,
            "prompt": "A tiny forest adventure",
            "style": "Pixel art",
            "detail": "Browser (HTML5)",
            "result": "A game plan",
            "created_at": "2026-01-02T03:04:05+00:00",
        }

    def test_saves_and_retrieves_creation(self):
        expected = self.creation()
        createlab_db.save_creation(expected, self.db_path)
        self.assertEqual(createlab_db.get_creation("one", self.db_path), expected)

    def test_filters_and_counts_by_kind(self):
        createlab_db.save_creation(self.creation("game", "Game"), self.db_path)
        createlab_db.save_creation(self.creation("video", "Video"), self.db_path)
        self.assertEqual(len(createlab_db.list_creations("Game", path=self.db_path)), 1)
        self.assertEqual(createlab_db.creation_counts(self.db_path), {"Video": 1, "Game": 1})

    def test_delete_is_idempotent(self):
        createlab_db.save_creation(self.creation(), self.db_path)
        self.assertTrue(createlab_db.delete_creation("one", self.db_path))
        self.assertFalse(createlab_db.delete_creation("one", self.db_path))

    def test_rejects_invalid_kind(self):
        with self.assertRaises(Exception):
            createlab_db.save_creation(self.creation(kind="Other"), self.db_path)


if __name__ == "__main__":
    unittest.main()
