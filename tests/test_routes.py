import tempfile
import unittest
from pathlib import Path

from app import create_app
from services import fswalker


class RoutesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temp_dir = tempfile.TemporaryDirectory()
        cls.books_root = Path(cls._temp_dir.name)
        cls.original_books_root = fswalker.BOOKS_ROOT

        sample_dir = cls.books_root / "Sample Book" / "Chapter 1"
        sample_dir.mkdir(parents=True, exist_ok=True)
        (sample_dir / "page1.html").write_text(
            "<html><body><h1>Sample page</h1></body></html>",
            encoding="utf-8",
        )
        (sample_dir / "note.txt").write_text("ignore", encoding="utf-8")
        chapter_two = cls.books_root / "Sample Book" / "Chapter 2"
        chapter_two.mkdir(parents=True, exist_ok=True)
        (chapter_two / "page2.html").write_text(
            "<html><body><h1>Next page</h1></body></html>",
            encoding="utf-8",
        )

        fswalker.BOOKS_ROOT = str(cls.books_root)
        app = create_app()
        app.config["TESTING"] = True
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        fswalker.BOOKS_ROOT = cls.original_books_root
        cls._temp_dir.cleanup()

    def test_index_page_opens(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<iframe id="viewer"', response.data)
        self.assertIn(b"window.BookPages = []", response.data)

    def test_api_folder_lists_book_tree(self):
        response = self.client.get("/api/folder")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload[0]["name"], "Sample Book")
        self.assertTrue(payload[0]["is_dir"])

    def test_api_folder_blocks_traversal(self):
        response = self.client.get("/api/folder?path=..")

        self.assertEqual(response.status_code, 403)

    def test_api_pages_returns_html_page_index(self):
        response = self.client.get("/api/pages")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(
            payload,
            [
                "Sample Book/Chapter 1/page1.html",
                "Sample Book/Chapter 2/page2.html",
            ],
        )

    def test_api_navigation_returns_prev_next(self):
        response = self.client.get("/api/navigation?path=Sample%20Book/Chapter%201/page1.html")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsNone(payload["prev"])
        self.assertEqual(payload["next"], "Sample Book/Chapter 2/page2.html")

    def test_book_serves_html_file(self):
        response = self.client.get("/book/Sample%20Book/Chapter%201/page1.html")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sample page", response.data)
        response.close()

    def test_book_blocks_traversal(self):
        response = self.client.get("/book/../app.py")

        self.assertEqual(response.status_code, 403)
        response.close()


if __name__ == "__main__":
    unittest.main()
