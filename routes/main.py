from app import app
from flask import render_template
from services.fswalker import read_folder, print_tree
import json


@app.route("/")
def hello_world():
    data = read_folder('./static/books')
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    # hello = "Hello! This is the Book Reader!"
    # print_tree(read_folder('./static/books')) # Uncomment to view the folder structure in the console
    return render_template("tree.html", tree=data)
