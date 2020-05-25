from flask import current_app
from flask_login import current_user
from werkzeug.local import LocalProxy

__all__ = ['db_session', 'current_repo', 'current_user']

db_session = LocalProxy(lambda: current_app.db.session)
current_repo = LocalProxy(lambda: current_app.repository)
