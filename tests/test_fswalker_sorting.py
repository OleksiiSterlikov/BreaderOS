import tempfile
import unittest
from pathlib import Path

from services import fswalker


class FswalkerSortingTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.books_root = Path(self.temp_dir.name)
        self.original_books_root = fswalker.BOOKS_ROOT
        fswalker.BOOKS_ROOT = self.books_root

        chapter_root = self.books_root / "Introduction to Networks v6 (ITN) Extended Ru" / "Глава 0. Знакомство с курсом"
        chapter_root.mkdir(parents=True, exist_ok=True)

        ordered_dirs = [
            "0.0.1.1 Добро пожаловать!",
            " 0.0.1.2 Мировое сообщество ",
            " 0.0.1.3 Больше чем просто информация ",
            " 0.0.1.4 Методика преподавания ",
            " 0.0.1.5 Освоение практический опыт ",
            " 0.0.1.6 Открытость новым знаниям ",
            " 0.0.1.7 Инженерно-технические журналы ",
            "0.0.1.8 Изучение мировых технологий",
            "0.0.1.9 Создание собственного сетевого мира",
            "0.0.1.10 Packet Tracer помогает понять принципы",
            "0.0.1.11 Обзор курса",
        ]

        for index, directory in enumerate(ordered_dirs, start=1):
            folder = chapter_root / directory
            folder.mkdir(parents=True, exist_ok=True)
            page_number = directory.strip().split(" ", 1)[0]
            (folder / f"{page_number}.html").write_text(f"<html>{index}</html>", encoding="utf-8")

    def tearDown(self):
        fswalker.BOOKS_ROOT = self.original_books_root
        self.temp_dir.cleanup()

    def test_list_folder_uses_natural_sort_even_with_wrapped_spaces(self):
        items = fswalker.list_folder("Introduction to Networks v6 (ITN) Extended Ru/Глава 0. Знакомство с курсом")
        names = [item["name"].strip().split(" ", 1)[0] for item in items]

        self.assertEqual(
            names,
            [
                "0.0.1.1",
                "0.0.1.2",
                "0.0.1.3",
                "0.0.1.4",
                "0.0.1.5",
                "0.0.1.6",
                "0.0.1.7",
                "0.0.1.8",
                "0.0.1.9",
                "0.0.1.10",
                "0.0.1.11",
            ],
        )

    def test_extract_all_pages_fs_preserves_natural_page_order(self):
        pages = fswalker.extract_all_pages_fs()
        page_numbers = [Path(page).stem for page in pages]

        self.assertEqual(
            page_numbers,
            [
                "0.0.1.1",
                "0.0.1.2",
                "0.0.1.3",
                "0.0.1.4",
                "0.0.1.5",
                "0.0.1.6",
                "0.0.1.7",
                "0.0.1.8",
                "0.0.1.9",
                "0.0.1.10",
                "0.0.1.11",
            ],
        )


if __name__ == "__main__":
    unittest.main()
