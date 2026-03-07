import unittest

from tools.check_docs_consistency import run_checks


class DocsConsistencyTestCase(unittest.TestCase):
    def test_documentation_matches_current_runtime(self):
        self.assertEqual(run_checks(), [])


if __name__ == "__main__":
    unittest.main()
