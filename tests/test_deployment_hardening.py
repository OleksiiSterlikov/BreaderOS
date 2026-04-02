import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class DeploymentHardeningTestCase(unittest.TestCase):
    def test_compose_avoids_mounting_whole_repository(self):
        compose = read_text("docker-compose.yml")

        self.assertNotIn("- .:/app", compose)
        self.assertNotIn("- .:/app:ro", compose)
        self.assertNotIn("- ./static:/app/static", compose)
        self.assertIn("${BOOKS_HOST_PATH:-./static/books}:/opt/breaderos/static/books:rw", compose)
        self.assertIn("./static/css:/srv/static/css:ro", compose)
        self.assertIn("./static/js:/srv/static/js:ro", compose)
        self.assertIn("${BOOKS_HOST_PATH:-./static/books}:/opt/breaderos/static/books:ro", compose)
        self.assertGreaterEqual(compose.count("read_only: true"), 2)
        self.assertGreaterEqual(compose.count("no-new-privileges:true"), 2)

    def test_runtime_configs_match_hardened_mount_layout(self):
        nginx_conf = read_text("nginx/nginx.conf")
        gunicorn_conf = read_text("gunicorn.conf.py")

        self.assertIn("alias /srv/static/;", nginx_conf)
        self.assertIn("alias /opt/breaderos/static/books/;", nginx_conf)
        self.assertIn('worker_tmp_dir = "/tmp"', gunicorn_conf)


if __name__ == "__main__":
    unittest.main()
