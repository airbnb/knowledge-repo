import logging
from .proxies import db_session, current_repo
from .models import Post
from .utils.emails import send_subscription_emails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_index():
    """ Initialize the db from a KnowledgeRepository object
    """
    kr_dir = {kp.path: kp for kp in current_repo.posts()}
    posts = db_session.query(Post).all()

    for post in posts:
        # Check if post is reverted
        if post.path not in kr_dir:
            logger.info('Recording unpublished status for post at {}'.format(post.path))
            post.status = current_repo.PostStatus.UNPUBLISHED
            continue

        # Otherwise, update database according to current state of knowledge post and
        # remove from kp_dir. This means that when this loop finishes, kr_dir will
        # only contain posts which are new to the repo.
        kp = kr_dir.pop(post.path)

        # TODO : Update with new logic using upcoming uuid
        if (kp.revision > post.revision or not post.is_published):
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
        post.update_metadata_from_kp(kp)
        send_subscription_emails(post)

    db_session.commit()
