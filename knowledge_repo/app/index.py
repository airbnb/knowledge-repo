from __future__ import absolute_import
import logging
import datetime
import threading
from flask import has_app_context

from .proxies import db_session, current_repo, current_app
from .models import Post, IndexMetadata
from .utils.emails import send_subscription_emails
from .utils.search import get_keywords
from .utils.time import time_since

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Some global aliases to be used below for enhanced readability
LOCKED = CHECKED = '1'
UNLOCKED = '0'


def is_indexing():
    timeout = current_app.config.get("INDEXING_TIMEOUT", 10 * 60)  # Default index timeout to 10 minutes (after which indexing will be permitted to run again)
    last_update = time_since_index()
    return IndexMetadata.get('lock', 'index', UNLOCKED) == LOCKED and last_update is not None and (last_update < timeout)


def time_since_index(human_readable=False):
    last_update = IndexMetadata.get_last_update('lock', 'index')
    ts = time_since(last_update, human_readable=human_readable)
    if human_readable:
        if is_indexing():
            return 'Currently indexing'
        if ts is None:
            return "Never"
    return ts


def time_since_index_check(human_readable=False):
    last_update = IndexMetadata.get_last_update('check', 'index')
    if human_readable and last_update is None:
        return "Never"
    return time_since(last_update, human_readable=human_readable)


def get_indexed_revisions():
    indexed = {}
    for uri in current_repo.uris.values():
        indexed_revision = IndexMetadata.get('repository_revision', uri)
        indexed[uri] = indexed_revision
    return indexed


def update_index_required(check_timeouts=True):
    if not current_app.config.get('REPOSITORY_INDEXING_ENABLED', True):
        return False

    if is_indexing():
        return False

    interval = current_app.config.get("INDEXING_INTERVAL", 5 * 60)  # Default to 6 minutes between indexing tasks
    seconds = time_since_index()
    seconds_check = time_since_index_check()

    if check_timeouts and (seconds is not None and seconds_check is not None) and (seconds < interval or seconds_check < interval):
        return False
    try:
        for uri, revision in current_repo.revisions.items():
            indexed_revision = IndexMetadata.get('repository_revision', uri)
            if indexed_revision is None or indexed_revision < str(revision):
                return True
        return False
    finally:
        IndexMetadata.set('check', 'index', CHECKED)
        db_session.commit()


def update_index(check_timeouts=True):
    """
    Initialize the db from a KnowledgeRepository object
    """

    if not update_index_required(check_timeouts=check_timeouts):
        return

    app = current_app._get_current_object()
    index_db = current_app.config['SQLALCHEMY_DATABASE_URI']

    if not index_db.startswith('sqlite://'):
        t = threading.Thread(target=_update_index, args=(app,))
        t.daemon = True
        t.start()
    else:
        _update_index(current_app)


def _update_index(app, force=False, reindex=False):

    context = None
    if not has_app_context():
        context = app.app_context()
        context.__enter__()

    if not force and is_indexing():
        return
    IndexMetadata.set('lock', 'index', LOCKED)
    db_session.commit()

    kr_dir = {kp.path: kp for kp in current_repo.posts()}
    kr_uuids = {kp.uuid: kp for kp in kr_dir.values()}
    posts = db_session.query(Post).all()

    for post in posts:

        # If UUID has changed, check if we can find it elsewhere in the repository, and if so update index path
        if post.uuid and ((post.path not in kr_dir) or (post.uuid != kr_dir[post.path].uuid)):
            if post.uuid in kr_uuids:
                logger.info('Updating location of post: {} -> {}'.format(post.path, kr_uuids[post.uuid].path))
                post.path = kr_uuids[post.uuid].path

        # If path of post no longer in directory, mark as unpublished
        if post.path not in kr_dir:
            logger.info('Recording unpublished status for post at {}'.format(post.path))
            post.status = current_repo.PostStatus.UNPUBLISHED
            continue

        # Update database according to current state of existing knowledge post and
        # remove from kp_dir. This means that when this loop finishes, kr_dir will
        # only contain posts which are new to the repo.
        kp = kr_dir.pop(post.path)

        # Update metadata of post if required
        if reindex or (kp.revision > post.revision or not post.is_published or kp.uuid != post.uuid):
            if kp.is_valid():
                logger.info('Recording update to post at: {}'.format(kp.path))
                post.update_metadata_from_kp(kp)
            else:
                logger.warning('Update to post at "{}" is corrupt.'.format(kp.path))

    # Add the new posts that remain in kr_dir
    for kp_path, kp in kr_dir.items():
        if not kp.is_valid():
            logger.warning('New post at "{}" is corrupt.'.format(kp.path))
            continue
        logger.info('creating new post from path {}'.format(kp_path))
        post = Post()
        db_session.add(post)
        db_session.flush()  # (matthew) Fix groups logic so this is not necessary
        post.update_metadata_from_kp(kp)
        send_subscription_emails(post)

    # Record revision
    for uri, revision in current_repo.revisions.items():
        IndexMetadata.set('repository_revision', uri, str(revision))

    IndexMetadata.set('lock', 'index', UNLOCKED)
    db_session.commit()

    if context is not None:
        context.__exit__(None, None, None)
