from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
CORS(app)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route("/")
def hello():
    return "Hello, we are building knowledge repo v2!"


# placeholder api to list all post in the landing page
@app.route("/feed")
def feed():
    return [{"title": "test", "content": "placeholder"}]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
