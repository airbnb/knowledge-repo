from ._version import *
from .utils.dependencies import check_dependencies
check_dependencies(__dependencies__)

from .repository import KnowledgeRepository  # nopep8
from .post import KnowledgePost  # nopep8

from . import converters  # nopep8
from . import postprocessors  # nopep8
from . import repositories  # nopep8

import logging  # nopep8
logging.basicConfig(level=logging.INFO)
