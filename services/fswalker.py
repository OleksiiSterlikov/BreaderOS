import os

def read_folder(root_path, relative=""):
    structure = []

    for name in sorted(os.listdir(root_path)):
        abs_path = os.path.join(root_path, name)
        rel_path = os.path.join(relative, name)
        if os.path.isdir(abs_path):
            structure.append({
                "name": name,
                "fullpath": rel_path.replace("\\", "/"),
                "children": read_folder(abs_path, rel_path)
            })
        else:
            structure.append({
                "name": name,
                "fullpath": rel_path.replace("\\", "/"),
                "children": []})
    return structure


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
