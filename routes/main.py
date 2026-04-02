from flask import Blueprint, render_template, jsonify, request, send_file, abort
from services.fswalker import (
    list_folder,
    extract_all_pages_fs,
    get_page_navigation,
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


@bp.route("/api/navigation")
def api_navigation():
    current_path = request.args.get("path", "")
    try:
        navigation = get_page_navigation(current_path)
    except LookupError:
        abort(404)
    return jsonify(navigation)


def _serve_book_file(rel_path):
    try:
        abs_path = resolve_books_path(rel_path)
    except ValueError:
        return abort(403)

    if not os.path.isfile(abs_path):
        return abort(404)

    return send_file(abs_path)


@bp.route("/book/<path:rel_path>")
def serve_book(rel_path):
    return _serve_book_file(rel_path)


@bp.route("/books/<path:rel_path>")
def serve_book_compat(rel_path):
    return _serve_book_file(rel_path)
