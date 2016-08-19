"""
Check the health of the app.

This view defines routes that allow us to check
the health of the server.
Ultimately, we can do something more complex
"""
from flask import Blueprint

blueprint = Blueprint('health', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/health')
def health():
    """Return OK when a request to the health view is received."""
    return "OK"


@blueprint.route('/ping')
def ping():
    """Return OK when a request to the ping view is received."""
    return "OK"
