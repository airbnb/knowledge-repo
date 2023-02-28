from ..index import get_indexed_revisions, is_indexing
from ..proxies import current_repo
from ..utils.shared import get_blueprint
from urllib.parse import unquote
from flask import (
    current_app,
    request,
    url_for,
    Response,
)
from knowledge_repo.constants import DEBUG
import knowledge_repo
import logging
import platform
import sys
import tabulate
import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blueprint = get_blueprint(DEBUG, __name__)


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
    for module_name in sorted(set(name.split('.')[0]
                              for name in sys.modules.keys())):
        if module_name.startswith('_'):
            continue
        module = __import__(module_name)
        if not hasattr(module, '__file__') or 'site-packages' \
                not in module.__file__:
            continue
        versions.append([module_name, get_version(__import__(module_name))])

    # Show revision for mountpoint. Don't show actual
    # uri because database passwords will be leaked
    revisions = []
    repo_revisions = current_repo.revisions
    indexed_revisions = get_indexed_revisions()
    for mountpoint, uri in current_repo.uris.items():
        revisions.append([mountpoint or '&lt;root&gt;',
                         repo_revisions[uri],
                         indexed_revisions.get(uri, 'None')])

    return (f"Knowledge Repo Version: {knowledge_repo.__version__}<br/>\n" +
            f"Python Version: {sys.version}<br/>\n" +
            f"Platform: {platform.version()}<br/>\n" +
            "<h2>Repository Revisions</h2>" +
            ("<i>Currently indexing</i><br />\n" if is_indexing() else "") +
            tabulate.tabulate(revisions, tablefmt='html') +
            "<h2>Loaded Packages</h2>\n" +
            tabulate.tabulate(versions, tablefmt='html', headers=(
                'Mount Point', 'Revision', 'Indexed Revision')))


@blueprint.route('/debug/force_reindex', methods=['GET'])
def force_reindex():
    reindex = bool(request.args.get('reindex', ''))
    current_app.db_update_index(
        check_timeouts=False, force=True, reindex=reindex)
    return "Index Updated"


@blueprint.route('/debug/views')
def show_views():
    output = []
    for rule in current_app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = f'[{arg}]'

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = unquote(f'{rule.endpoint:50s} {methods:20s} {url}')
        output.append(line)

    return "<br />".join(sorted(output))


@blueprint.route('/debug/headers')
def show_headers():
    return Response(str(request.headers).encode(), mimetype='text/plain')
