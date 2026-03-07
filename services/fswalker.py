import os
import re
from pathlib import Path

BOOKS_ROOT = Path("/app/static/books")

def resolve_books_path(relative_path: str) -> str:
    """Resolve a path under BOOKS_ROOT and reject traversal outside it."""
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

    pages.sort(key=num_sort_key)
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
    return [
        int(num) if num.isdigit() else num.lower()
        for num in re.split(r"(\d+)", text)
    ]

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
