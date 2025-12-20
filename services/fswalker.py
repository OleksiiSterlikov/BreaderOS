from flask import Response, request
import os
import re


BOOKS_ROOT = os.path.join("static", "books")

# -------------------------------
# READ ONE FOLDER (lazy)
# -------------------------------
def list_folder(relative_path: str):
    """
    Returns list of items inside folder.
    Does NOT recurse deeper (lazy loading).
    """
    abs_path = os.path.join(BOOKS_ROOT, relative_path)

    if not os.path.exists(abs_path):
        return []

    entries = []

    for name in sorted(os.listdir(abs_path), key=natural_key):

        # Skip technical folders
        if name.lower() == "data":
            continue

        full_abs = os.path.join(abs_path, name)
        full_rel = os.path.join(relative_path, name).replace("\\", "/")

        is_dir = os.path.isdir(full_abs)

        entries.append({
            "name": name,
            "fullpath": full_rel,
            "is_dir": is_dir,
            "children": None if is_dir else []   # lazy token
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