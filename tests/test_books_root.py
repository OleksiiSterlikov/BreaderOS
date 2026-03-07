import os
import unittest
from pathlib import Path
from unittest import mock

from services import fswalker


class BooksRootTestCase(unittest.TestCase):
    def test_default_books_root_uses_repo_static_books_when_env_missing(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            expected = fswalker.PROJECT_ROOT / "static" / "books"
            self.assertEqual(fswalker.default_books_root(), expected)

    def test_default_books_root_uses_env_override_when_present(self):
        with mock.patch.dict(os.environ, {"BOOKS_ROOT": "/tmp/custom-books"}, clear=True):
            self.assertEqual(fswalker.default_books_root(), Path("/tmp/custom-books"))


if __name__ == "__main__":
    unittest.main()
