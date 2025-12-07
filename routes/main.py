from flask import Blueprint, render_template, jsonify, request, send_file, abort
from services.fswalker import list_folder, BOOKS_ROOT
import os


bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    root_items = list_folder("")
    return render_template("tree.html", tree=root_items)


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