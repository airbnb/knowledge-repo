from __future__ import absolute_import

import logging
import multiprocessing
import os
import time
from builtins import str

from .proxies import db_session, current_repo, current_app
from .models import ErrorLog, Post, IndexMetadata
from .utils.emails import send_subscription_emails
from .utils.time import time_since

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Some global aliases to be used below for enhanced readability
LOCKED = CHECKED = '1'
UNLOCKED = '0'


def set_up_indexing_timers(app):
    if not app.config['INDEXING_ENABLED']:
        return False

    if app.check_thread_support(check_index=True, check_repositories=app.config['INDEXING_UPDATES_REPOSITORIES']):
        if os.environ['KNOWLEDGE_REPO_MASTER_UUID'] != app.uuid:
            logger.info("Not spawning index-sync timers for non-master application instance: {}".format(app.uuid))
            return

        def index_watchdog(app):
            while True:
                if not hasattr(app, 'sync_thread') or not app.sync_thread.is_alive():
                    logger.warning("Master indexing thread has died. Restarting...")
                    with app.app_context():
                        app.sync_thread = multiprocessing.Process(target=index_sync_loop, args=(app,))
                        app.sync_thread.start()
                time.sleep(app.config['INDEXING_TIMEOUT'])

        def index_sync_loop(app):
            while True:
                with app.app_context():
                    update_index(check_timeouts=False)
                time.sleep(app.config['INDEXING_INTERVAL'])

        app.index_watchdog = multiprocessing.Process(target=index_watchdog, args=(app,))
        app.index_watchdog.start()
    else:
        @app.before_request
        def update_index_if_required():
            update_index()


def acquire_index_lock():
    if IndexMetadata.get('lock', 'master_check', None) is None:
        try:
            IndexMetadata.set('lock', 'master_check', current_app.uuid)
            db_session.commit()
            if (
                IndexMetadata.get('lock', 'index_master') == current_app.uuid or
                time_since(IndexMetadata.get_last_update('lock', 'index_master'), default=current_app.config["INDEXING_TIMEOUT"] + 1) > current_app.config["INDEXING_TIMEOUT"]
            ):
                IndexMetadata.set('lock', 'index_master', current_app.uuid)  # Update/set lock and update timestamp
                return True
        finally:
            IndexMetadata.set('lock', 'master_check', None)
            db_session.commit()
    return False


def is_indexing():
    timeout = current_app.config["INDEXING_TIMEOUT"]  # Default index timeout to 10 minutes (after which indexing will be permitted to run again)
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
    last_update = IndexMetadata.get_last_update('lock', 'index_master')
    if human_readable and last_update is None:
        return "Never"
    return time_since(last_update, human_readable=human_readable)


def get_indexed_revisions():
    indexed = {}
    for uri in current_repo.uris.values():
        indexed_revision = IndexMetadata.get('repository_revision', uri)
        indexed[uri] = indexed_revision
    return indexed


def index_due_for_update():
    if not current_app.config['INDEXING_ENABLED']:
        return False

    interval = current_app.config["INDEXING_INTERVAL"]
    seconds = time_since_index()
    seconds_check = time_since_index_check()

    if (seconds is not None and seconds_check is not None) and (seconds < interval or seconds_check < interval):
        return False

    return True


def index_up_to_date():
    for uri, revision in current_repo.revisions.items():
        indexed_revision = IndexMetadata.get('repository_revision', uri)
        if indexed_revision is None or indexed_revision < str(revision):
            return False
    return True


@ErrorLog.logged
def update_index(check_timeouts=True, force=False, reindex=False):

    if not current_app.config['INDEXING_ENABLED']:
        return False

    if check_timeouts and not index_due_for_update():
        return False

    is_index_master = acquire_index_lock()

    # Check for update to repositories if configured to do so
    if (
        current_app.config['INDEXING_UPDATES_REPOSITORIES'] and
        (is_index_master or current_app.config['INDEXING_UPDATES_REPOSITORIES_WITHOUT_LOCK'])
    ):
        current_repo.update()

    # Short-circuit if not the index master (unless force is True)
    if not is_index_master and not force or index_up_to_date():
        return False

    try:
        IndexMetadata.set('lock', 'index', LOCKED)
        db_session.commit()

        kr_dir = {kp.path: kp for kp in current_repo.posts()}
        kr_uuids = {kp.uuid: kp for kp in kr_dir.values()}
        posts = db_session.query(Post).all()

        for post in posts:

            # If UUID has changed, check if we can find it elsewhere in the repository, and if so update index path
            if post.uuid and ((post.path not in kr_dir) or (post.uuid != kr_dir[post.path].uuid)):
                if post.uuid in kr_uuids:
                    logger.info(u'Updating location of post: {} -> {}'.format(post.path, kr_uuids[post.uuid].path))
                    post.path = kr_uuids[post.uuid].path

            # If path of post no longer in directory, mark as unpublished
            if post.path not in kr_dir:
                logger.info(u'Recording unpublished status for post at {}'.format(post.path))
                post.status = current_repo.PostStatus.UNPUBLISHED
                continue

            # Update database according to current state of existing knowledge post and
            # remove from kp_dir. This means that when this loop finishes, kr_dir will
            # only contain posts which are new to the repo.
            kp = kr_dir.pop(post.path)

            # Update metadata of post if required
            if reindex or (kp.revision > post.revision or not post.is_published or kp.uuid != post.uuid):
                if kp.is_valid():
                    logger.info(u'Recording update to post at: {}'.format(kp.path))
                    post.update_metadata_from_kp(kp)
                else:
                    logger.warning(u'Update to post at "{}" is corrupt.'.format(kp.path))

        # Add the new posts that remain in kr_dir
        for kp_path, kp in kr_dir.items():
            if not kp.is_valid():
                logger.warning(u'New post at "{}" is corrupt.'.format(kp.path))
                continue
            logger.info(u'creating new post from path {}'.format(kp_path))
            post = Post()
            db_session.add(post)
            db_session.flush()  # (matthew) Fix groups logic so this is not necessary
            post.update_metadata_from_kp(kp)
            send_subscription_emails(post)

        # Record revision
        for uri, revision in current_repo.revisions.items():
            IndexMetadata.set('repository_revision', uri, str(revision))
    finally:
        IndexMetadata.set('lock', 'index', UNLOCKED)
        db_session.commit()
