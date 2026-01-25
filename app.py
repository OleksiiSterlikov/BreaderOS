from flask import Flask
from routes.main import bp as main_bp

app = Flask(__name__)

# Register Blueprint
app.register_blueprint(main_bp)

with app.app_context():
    from routes.main import *

if __name__ == "__main__":
    app.run()

