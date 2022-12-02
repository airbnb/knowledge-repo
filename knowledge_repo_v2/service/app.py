from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
CORS(app)
app.config.from_object("config.Config")
db = SQLAlchemy(app)


# [TODO] migrate to flask-migrate
class User(db.Model):
    __tablename__ = "knowledge_post_author"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)

    def __init__(self, email):
        self.email = email

@app.route("/")
def hello():
    return "Hello, we are building knowledge repo v2!"


# placeholder api to list all post in the landing page
@app.route("/feed")
def feed():
    return [{"title": "test", "content": "placeholder"}]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
