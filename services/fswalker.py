from flask import Response, request
import os
import re


def read_folder(root_path, relative=""):
    structure = []

    # Використовуємо натуральне сортування для Chapter 1..10 і 0.0.1.1..10
    for name in sorted(os.listdir(root_path), key=natural_key):

        # Пропускаємо data/
        if name.lower() == "data":
            continue

        abs_path = os.path.join(root_path, name)
        rel_path = os.path.join(relative, name).replace("\\", "/")

        if os.path.isdir(abs_path):
            structure.append({
                "name": name,
                "fullpath": rel_path,
                "children": read_folder(abs_path, rel_path)
            })
        else:
            structure.append({
                "name": name,
                "fullpath": rel_path,
                "children": []
            })

    return structure

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

def partial_response(path):
    file_size = os.path.getsize(path)
    range_header = request.headers.get('Range', None)

    if not range_header:
        # Без Range повертаємо весь файл
        with open(path, 'rb') as f:
            data = f.read()
        return Response(
            data,
            200,
            mimetype="video/mp4",
            direct_passthrough=True,
            headers={"Accept-Ranges": "bytes"}
        )

    # Парсимо Range
    byte1, byte2 = 0, None
    m = re.search(r'(\d+)-(\d*)', range_header)
    if m:
        g = m.groups()
        byte1 = int(g[0])
        if g[1]:
            byte2 = int(g[1])

    if byte2 is None:
        byte2 = file_size - 1

    length = byte2 - byte1 + 1

    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(
        data,
        206,
        mimetype="video/mp4",
        direct_passthrough=True,
        headers={
            "Content-Range": f"bytes {byte1}-{byte2}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
        }
    )
    return rv


def natural_key(text):
    """Ключ для натурального сортування — числа в рядках сортуються правильно."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', text)]
