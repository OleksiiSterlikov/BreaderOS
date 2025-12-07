from app import app
from flask import abort, render_template, send_file
from werkzeug.utils import safe_join
from services.fswalker import read_folder, partial_response
import os



@app.route("/")
def main():
    data = read_folder('./static/books')
    return render_template("tree.html", tree=data)


@app.route("/book/<path:file_path>")
def serve_book(file_path):
    base_dir = os.path.join(app.static_folder, "books")
    abs_path = safe_join(base_dir, file_path)

    if abs_path is None:
        return abort(404)

    if abs_path.lower().endswith(".mp4"):
        return partial_response(abs_path)

    # Enable Windows long path support
    if os.name == "nt":
        abs_path = "\\\\?\\" + os.path.abspath(abs_path)

    if not os.path.isfile(abs_path):
        return abort(404)

    print("ABS PATH CHECK:", abs_path)
    print("EXISTS:", os.path.exists(abs_path))
    print("Sending:", abs_path)

    # SEND FILE DIRECTLY — THIS FIXES LONG PATHS!
    return send_file(abs_path)

