from app import app
from flask import render_template, send_from_directory, abort
from werkzeug.utils import safe_join
from services.fswalker import read_folder, print_tree
import os


@app.route("/")
def main():
    data = read_folder('./static/books')
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    # hello = "Hello! This is the Book Reader!"
    # print_tree(read_folder('./static/books')) # Uncomment to view the folder structure in the console
    return render_template("tree.html", tree=data)


#@app.route("/book/<path:file_path>")
#def serve_book(file_path):
#    base_dir = os.path.join(app.static_folder, "books")
#    abs_path = safe_join(base_dir, file_path)
#
#    if abs_path is None:
#        return abort(404)
#
#    # Додаємо підтримку довгих шляхів Windows
#    if os.name == "nt":
#        abs_path = "\\\\?\\" + os.path.abspath(abs_path)
#
#    if not os.path.isfile(abs_path):
#        return abort(404)
#
#    directory = os.path.dirname(abs_path)
#    filename = os.path.basename(abs_path)
#
#    return send_from_directory(directory, filename)