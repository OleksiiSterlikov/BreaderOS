from app import app
from flask import render_template
from services.fswalker import read_folder, print_tree


@app.route("/")
def hello_world():
    hello = "Hello! This is the Book Reader!"
    print_tree(read_folder('./bookdata'))
    return render_template("index.html", hello=hello, bookdata=read_folder('./bookdata'))

