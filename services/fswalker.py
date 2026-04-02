import os
import re
from pathlib import Path, PurePosixPath

from services.book_names import ensure_book_names_normalized

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def default_books_root() -> Path:
    configured = os.getenv("BOOKS_ROOT")
    if configured:
        return Path(configured)
    return PROJECT_ROOT / "static" / "books"


BOOKS_ROOT = default_books_root()


def resolve_books_path(relative_path: str) -> Path:
    """Resolve a path under BOOKS_ROOT and reject traversal outside it."""
    ensure_book_names_normalized(BOOKS_ROOT)
    root = Path(BOOKS_ROOT)
    root_path = root.resolve()
    abs_path = (root / relative_path).resolve()

    if os.path.commonpath([str(abs_path), str(root_path)]) != str(root_path):
        raise ValueError("Path escapes books root")

    return abs_path


def list_folder(relative_path: str):
    """
    Returns list of items inside folder.
    Does NOT recurse deeper (lazy loading).
    """
    abs_path = resolve_books_path(relative_path)

    if not abs_path.exists():
        return []

    entries = []

    for name in sorted(abs_path.iterdir(), key=lambda p: natural_key(p.name)):

        # Skip technical folders
        if name.name.lower() == "data":
            continue

        rel = (Path(relative_path) / name.name).as_posix()

        entries.append({
            "name": name.name,
            "fullpath": rel,
            "is_dir": name.is_dir(),
            "children": None
        })

    return entries

def extract_all_pages(nodes):
    pages = []

    def walk(items):
        for item in items:
            if not item["is_dir"] and item["name"].lower().endswith(".html"):
                pages.append(item["fullpath"])

            if item.get("children"):
                walk(item["children"])

    walk(nodes)
    return pages

def extract_all_pages_fs():
    ensure_book_names_normalized(BOOKS_ROOT)
    pages = []

    for root, dirs, files in os.walk(BOOKS_ROOT):
        # Пропускаємо всі папки data
        dirs[:] = [d for d in dirs if d.lower() != "data"]

        for f in files:
            if f.lower().endswith(".html"):
                full = os.path.join(root, f)

                rel = os.path.relpath(full, BOOKS_ROOT).replace("\\", "/")
                pages.append(rel)

    # Сортування за числовими частинами
    def num_sort_key(s):
        import re
        return [int(x) if x.isdigit() else x.lower()
                for x in re.split(r"(\d+)", s)]

    pages.sort(key=path_sort_key)
    return pages
# View to the console tree structure for testing
def print_tree(items, level=0):
    prefix = "  " * level  # -, --, ---, ---- ...

    for item in items:
        if isinstance(item, list):
            # item = ["folder", [...] ]
            name, children = item
            print(f"{prefix}{name}:")
            print_tree(children, level + 1)
        else:
            # item = "filename"
            print(f"{prefix}{item}")


# -------------------------------
# NATURAL SORT ("1", "2", "10")
# -------------------------------
def natural_key(text: str):
    normalized = normalize_sort_text(text)
    return [
        int(num) if num.isdigit() else num.lower()
        for num in re.split(r"(\d+)", normalized)
    ]


def normalize_sort_text(text: str) -> str:
    return text.strip()


def path_sort_key(path: str):
    return tuple(tuple(natural_key(part)) for part in PurePosixPath(path).parts)


def normalize_lookup_path(path: str) -> str:
    return "/".join(part.strip() for part in PurePosixPath(path).parts)


def get_page_navigation(current_path: str, pages: list[str] | None = None) -> dict[str, str | None]:
    pages = pages or extract_all_pages_fs()
    normalized_current = normalize_lookup_path(current_path)
    normalized_pages = [normalize_lookup_path(page) for page in pages]

    try:
        idx = normalized_pages.index(normalized_current)
    except ValueError:
        raise LookupError(f"page not found in index: {current_path}")

    prev_path = pages[idx - 1] if idx > 0 else None
    next_path = pages[idx + 1] if idx < len(pages) - 1 else None
    return {"prev": prev_path, "next": next_path}

def flatten_html(tree):
    """Повертає список всіх html-файлів у правильному порядку."""
    pages = []

    def walk(items):
        for item in items:
            if item["children"]:
                walk(item["children"])
            if item["name"].lower().endswith(".html"):
                pages.append(item["fullpath"].replace("\\", "/"))

    walk(tree)
    return pages
