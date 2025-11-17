from app import app
from flask import render_template


@app.route("/")
def hello_world():
    hello = "Hello! This is the Book Reader!"
    return render_template("index.html", hello=hello)
