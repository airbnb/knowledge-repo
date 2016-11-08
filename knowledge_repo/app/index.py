from __future__ import absolute_import
import logging
import datetime
import threading
from flask import has_app_context

from .proxies import db_session, current_repo, current_app
from .models import Post, IndexMetadata
from .utils.emails import send_subscription_emails
from .utils.search import get_keywords

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_indexing():
    return int(IndexMetadata.get('lock', 'index', '0'))


def seconds_since_index():
    last_update = IndexMetadata.get_last_update('lock', 'index')
    if last_update is None:
        return None
    else:
        return (datetime.datetime.utcnow() - last_update).total_seconds()


def seconds_since_index_check():
    last_update = IndexMetadata.get_last_update('check', 'index')
    if last_update is None:
        return None
    else:
        return (datetime.datetime.utcnow() - last_update).total_seconds()


def human_readable_time_since_index():
    if is_indexing():
        return 'Currently indexing'
    seconds = seconds_since_index()
    if seconds is None:
        return "Never"
    elif seconds < 60:
        return "{:d} seconds ago".format(int(round(seconds)))
    else:
        return "{:d} minutes ago".format(int(round(seconds / 60)))


def update_index_required():
    if not current_app.config.get('REPOSITORY_INDEXING_ENABLED', True):
        return False

    seconds = seconds_since_index()
    seconds_check = seconds_since_index_check()
    if is_indexing() or (seconds is not None) and (seconds < 5 * 60) and (seconds_check < 5 * 60):
        return False
    try:
        for uri, revision in current_repo.revisions.items():
            indexed_revision = IndexMetadata.get('repository_revision', uri)
            if indexed_revision is None or indexed_revision < revision:
                return True
        return False
    finally:
        IndexMetadata.set('check', 'index', False)


def update_index():
    """
    Initialize the db from a KnowledgeRepository object
    """

    if not update_index_required():
        return

    app = current_app._get_current_object()
    index_db = current_app.config['SQLALCHEMY_DATABASE_URI']

    if not index_db.startswith('sqlite://'):
        t = threading.Thread(target=_update_index, args=(app,))
        t.daemon = True
        t.start()
    else:
        _update_index(current_app)


def _update_index(app):

    context = None
    if not has_app_context():
        context = app.app_context()
        context.__enter__()

    if is_indexing():
        return
    IndexMetadata.set('lock', 'index', True)
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

        # TODO(nikki_ray): This is to support the backfilling of this column. Remove this.
        if not post.keywords:
            post.keywords = get_keywords(post)

        # Update database according to current state of existing knowledge post and
        # remove from kp_dir. This means that when this loop finishes, kr_dir will
        # only contain posts which are new to the repo.
        kp = kr_dir.pop(post.path)

        # Update metadata of post if required
        if (kp.revision > post.revision or not post.is_published or kp.uuid != post.uuid):
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
        IndexMetadata.set('repository_revision', uri, revision)

    IndexMetadata.set('lock', 'index', False)
    db_session.commit()

    if context is not None:
        context.__exit__(None, None, None)
