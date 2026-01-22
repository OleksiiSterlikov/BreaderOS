from flask import Blueprint, render_template, jsonify, request, send_file, abort
from services.fswalker import list_folder, BOOKS_ROOT, extract_all_pages_fs
import os


bp = Blueprint("main", __name__)
BOOKS_ROOT = os.path.join(os.path.dirname(__file__), "..", "static", "books")

@bp.route("/")
def index():
    root_items = list_folder("")
    pages = extract_all_pages_fs()   # <<< НЕ через lazy-data
    print("PAGES:", pages)
    return render_template("tree.html", tree=root_items, pages=pages)


@bp.route("/api/folder")
def api_folder():
    rel = request.args.get("path", "")
    items = list_folder(rel)
    return jsonify(items)

@bp.route("/book/<path:rel_path>")
def serve_book(rel_path):

    # абсолютний шлях до файлу
    abs_path = os.path.realpath(os.path.join(BOOKS_ROOT, rel_path))

    # абсолютний шлях до кореня книг
    root_path = os.path.realpath(BOOKS_ROOT)

    # 🔥 Перевірка безпеки без багів
    if os.path.commonpath([abs_path, root_path]) != root_path:
        return abort(403)

    # файл існує?
    if not os.path.exists(abs_path):
        return abort(404)

    return send_file(abs_path)

@bp.route("/book/<path:filename>")
def book(filename):
    # прибираємо .. та інші небезпечні речі
    safe = filename.replace("..", "").lstrip("/")

    abs_path = os.path.join(BOOKS_ROOT, safe)

    print("BOOK REQUEST:", abs_path)

    if not os.path.isfile(abs_path):
        print("NOT FOUND:", abs_path)
        abort(404)

    return send_file(abs_path)
