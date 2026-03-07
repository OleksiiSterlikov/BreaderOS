import tempfile
import unittest
from pathlib import Path

from tools.import_book import import_book


class ImportBookTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.source = self.base / "source-book"
        self.books_root = self.base / "books-root"

        chapter = self.source / "Chapter 1"
        chapter.mkdir(parents=True, exist_ok=True)
        (chapter / "page1.html").write_text("<html>book</html>", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_import_book_copies_directory(self):
        destination = import_book(self.source, self.books_root)

        self.assertTrue(destination.exists())
        self.assertTrue((destination / "Chapter 1" / "page1.html").exists())

    def test_import_book_supports_target_subdir(self):
        destination = import_book(
            self.source,
            self.books_root,
            target_subdir="Networking/CCNA",
        )

        self.assertEqual(destination, self.books_root / "Networking" / "CCNA" / "source-book")
        self.assertTrue(destination.exists())

    def test_import_book_requires_replace_for_existing_destination(self):
        import_book(self.source, self.books_root)

        with self.assertRaises(FileExistsError):
            import_book(self.source, self.books_root)

    def test_import_book_replaces_existing_destination(self):
        destination = import_book(self.source, self.books_root)
        (destination / "old.txt").write_text("old", encoding="utf-8")

        replaced_destination = import_book(self.source, self.books_root, replace=True)

        self.assertEqual(destination, replaced_destination)
        self.assertFalse((destination / "old.txt").exists())

    def test_import_book_rejects_unsafe_target_subdir(self):
        with self.assertRaises(ValueError):
            import_book(self.source, self.books_root, target_subdir="../unsafe")


if __name__ == "__main__":
    unittest.main()
