from flask import Blueprint, render_template, jsonify, request, send_file, abort
from services.fswalker import (
    list_folder,
    extract_all_pages_fs,
    resolve_books_path,
)
import os


bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    root_items = list_folder("")
    return render_template("tree.html", tree=root_items, pages=[])


@bp.route("/api/folder")
def api_folder():
    rel = request.args.get("path", "")
    try:
        items = list_folder(rel)
    except ValueError:
        abort(403)
    return jsonify(items)


@bp.route("/api/pages")
def api_pages():
    return jsonify(extract_all_pages_fs())

@bp.route("/book/<path:rel_path>")
def serve_book(rel_path):
    try:
        abs_path = resolve_books_path(rel_path)
    except ValueError:
        return abort(403)

    if not os.path.isfile(abs_path):
        return abort(404)

    return send_file(abs_path)
