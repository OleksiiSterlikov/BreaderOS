import os

def read_folder(path):
    items = []

    for item in sorted(os.listdir(path)):
        full = os.path.join(path, item)

        if os.path.isdir(full):
            # Папка → ["имя_папки", [...содержимое...]]
            items.append([item, read_folder(full)])
        else:
            # Файл → "имя_файла"
            items.append(item)

    return items

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
