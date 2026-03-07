import tempfile
import unittest
from pathlib import Path

from tools.audit_book_names import analyze_book_names, apply_rename_plan, normalize_name


class AuditBookNamesTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.books_root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_normalize_name_strips_edge_spaces(self):
        self.assertEqual(normalize_name(" 0.0.1.2 Test "), "0.0.1.2 Test")

    def test_analyze_book_names_builds_dry_run_plan(self):
        folder = self.books_root / " Course " / " 0.0.1.2 Topic "
        folder.mkdir(parents=True, exist_ok=True)
        (folder / " page.html ").write_text("<html></html>", encoding="utf-8")

        report = analyze_book_names(self.books_root)

        planned_pairs = {(plan.source.name, plan.destination.name) for plan in report.rename_plans}
        self.assertIn((" Course ", "Course"), planned_pairs)
        self.assertIn((" 0.0.1.2 Topic ", "0.0.1.2 Topic"), planned_pairs)
        self.assertIn((" page.html ", "page.html"), planned_pairs)
        self.assertEqual(report.collisions, ())

    def test_analyze_book_names_detects_collisions(self):
        (self.books_root / "Course" / "Topic").mkdir(parents=True, exist_ok=True)
        (self.books_root / "Course" / " Topic ").mkdir(parents=True, exist_ok=True)

        report = analyze_book_names(self.books_root)

        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.collisions[0].normalized_name, "Topic")

    def test_apply_rename_plan_renames_files_and_directories(self):
        folder = self.books_root / " Course " / " 0.0.1.2 Topic "
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / " page.html "
        file_path.write_text("<html></html>", encoding="utf-8")

        report = analyze_book_names(self.books_root)
        renamed = apply_rename_plan(report)

        self.assertEqual(renamed, 3)
        self.assertTrue((self.books_root / "Course" / "0.0.1.2 Topic" / "page.html").exists())
        self.assertFalse((self.books_root / " Course ").exists())

    def test_apply_rename_plan_rejects_collisions(self):
        (self.books_root / "Course" / "Topic").mkdir(parents=True, exist_ok=True)
        (self.books_root / "Course" / " Topic ").mkdir(parents=True, exist_ok=True)

        report = analyze_book_names(self.books_root)

        with self.assertRaises(RuntimeError):
            apply_rename_plan(report)


if __name__ == "__main__":
    unittest.main()
