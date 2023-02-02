"""
Check the health of the app.

This view defines routes that allow us to check
the health of the server.
Ultimately, we can do something more complex
"""
from ..utils.shared import get_blueprint

blueprint = get_blueprint('health', __name__)


@blueprint.route('/health')
def health():
    """Return OK when a request to the health view is received."""
    return "OK"


@blueprint.route('/ping')
def ping():
    """Return OK when a request to the ping view is received."""
    return "OK"
