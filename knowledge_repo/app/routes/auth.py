""" Define the routes for the authentication machinery

This includes:
  - /login
  - /oauth/authorized
"""
from flask import redirect, Blueprint, current_app

blueprint = Blueprint(
    'auth', __name__, template_folder='../templates', static_folder='../static')


@blueprint.route('/login')
def login():
    try:
        authenticator = current_app.authenticator
    except AttributeError:
        raise RuntimeError("No authenticator has been set")
    return authenticator.login()

@blueprint.route("/oauth/authorized")
def oauth_authorized():
    return ('', 204)
