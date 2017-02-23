import sys
import platform
import types
import logging
import tabulate
import knowledge_repo

from flask import request, current_app, Blueprint
from ..proxies import current_repo
from ..index import get_indexed_revisions, is_indexing


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


blueprint = Blueprint('debug', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/debug/versions', methods=['GET'])
def show_versions():
    version_keys = ['__version__', 'VERSION', 'version', '__VERSION__']

    def get_version(module):
        for key in version_keys:
            if hasattr(module, key):
                version = getattr(module, key)
                if isinstance(version, types.ModuleType):
                    version = get_version(version)
                return version

        return 'Unknown'

    versions = []
    for module_name in sorted(set(name.split('.')[0] for name in sys.modules.keys())):
        if module_name.startswith('_'):
            continue
        module = __import__(module_name)
        if not hasattr(module, '__file__') or 'site-packages' not in module.__file__:
            continue
        versions.append([module_name, get_version(__import__(module_name))])

    # Show revision for mountpoint. Don't show actual uri because database passwords will be leaked
    revisions = []
    repo_revisions = current_repo.revisions
    indexed_revisions = get_indexed_revisions()
    for mountpoint, uri in current_repo.uris.items():
        revisions.append([mountpoint or '&lt;root&gt;', repo_revisions[uri], indexed_revisions.get(uri, 'None')])

    return ("Knowledge Repo Version: {}<br/>\n".format(knowledge_repo.__version__) +
            "Python Version: {}<br/>\n".format(sys.version) +
            "Platform: {}<br/>\n".format(platform.version()) +
            "<h2>Repository Revisions</h2>" +
            ("<i>Currently indexing</i><br />\n" if is_indexing() else "") +
            tabulate.tabulate(revisions, tablefmt='html') +
            "<h2>Loaded Packages</h2>\n" +
            tabulate.tabulate(versions, tablefmt='html', headers=('Mount Point', 'Revision', 'Indexed Revision')))


@blueprint.route('/debug/force_reindex', methods=['GET'])
def force_reindex():
    reindex = bool(request.args.get('reindex', ''))
    current_app.db_update_index(reindex=reindex)
    return "Index Updated"
