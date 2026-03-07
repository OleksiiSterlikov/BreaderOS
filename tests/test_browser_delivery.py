import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

from werkzeug.serving import make_server

from app import create_app
from services import fswalker


class BrowserDeliveryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temp_dir = tempfile.TemporaryDirectory()
        cls.books_root = Path(cls._temp_dir.name)
        cls.original_books_root = fswalker.BOOKS_ROOT

        chapter = cls.books_root / "Sample Book" / "Chapter 1"
        chapter.mkdir(parents=True, exist_ok=True)
        (chapter / "page1.html").write_text(
            "<html><body><h1>Sample page</h1></body></html>",
            encoding="utf-8",
        )

        fswalker.BOOKS_ROOT = str(cls.books_root)

        cls.app = create_app()
        cls.app.config["TESTING"] = True
        try:
            cls.server = make_server("127.0.0.1", 0, cls.app)
        except PermissionError as exc:
            raise unittest.SkipTest(
                "HTTP integration test requires local socket permissions"
            ) from exc
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=2)
        fswalker.BOOKS_ROOT = cls.original_books_root
        cls._temp_dir.cleanup()

    def test_index_html_contains_navigation_toolbar(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as response:
            html = response.read().decode("utf-8")

        self.assertIn('id="viewer-toolbar"', html)
        self.assertIn('id="nav-prev"', html)
        self.assertIn('id="nav-next"', html)
        self.assertIn('id="viewer"', html)


if __name__ == "__main__":
    unittest.main()
