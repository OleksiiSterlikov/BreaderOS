from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


with app.app_context():
    from routes.main import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
