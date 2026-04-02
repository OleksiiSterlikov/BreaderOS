import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class RequirementsTestCase(unittest.TestCase):
    def test_gunicorn_is_pinned_for_reproducible_builds(self):
        requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        requirement_lines = [line.strip() for line in requirements if line.strip() and not line.strip().startswith("#")]

        self.assertIn("gunicorn==25.3.0", requirement_lines)


if __name__ == "__main__":
    unittest.main()
