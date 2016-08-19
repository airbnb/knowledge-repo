from flask import current_app
from werkzeug.local import LocalProxy

db_session = LocalProxy(lambda: current_app.db.session)
current_repo = LocalProxy(lambda: current_app.repository)
