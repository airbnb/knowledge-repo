from os import path
import sys

from . import context  # noqa
from . import op  # noqa
from .runtime import environment
from .runtime import migration

__version__ = '1.0.7'

package_dir = path.abspath(path.dirname(__file__))

sys.modules["alembic.migration"] = migration
sys.modules["alembic.environment"] = environment
