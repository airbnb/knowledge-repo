"""
This file deals with all of the email functions.
"""
from ..models import Email, Subscription, User
from ..proxies import db_session
from ..proxies import current_repo
from flask import render_template, current_app, url_for
from flask_mail import Message
import base64
import logging
import re
import requests

logger = logging.getLogger(__name__)


def usernames_to_emails(usernames):
    username_to_email = current_repo.config.username_to_email
    return [username_to_email(username) for username in usernames]


def subscription_email_recipients(post, tag):
    """Check who should receive a subscription email about this post"""
    db_session.expire_on_commit = False

    subscriptions = (db_session.query(Subscription)
                               .filter(Subscription.object_type == 'tag')
                               .filter(Subscription.object_id == tag.id)
                               .all())

    subscriber_ids = list(set([s.user_id for s in subscriptions]))  # uniqify
    emails_sent = (db_session.query(Email)
                             .filter(Email.object_id == post.id)
                             .all())

    users_rcvd_emails = [e.user_id for e in emails_sent]
    new_email_recipient_ids = [
        user_id for user_id in subscriber_ids
        if user_id not in users_rcvd_emails]

    if not new_email_recipient_ids:
        return []
    new_email_recipients = (db_session.query(User)
                                      .filter(User.id.in_(
                                          new_email_recipient_ids
                                      ))
                            .all())
    return new_email_recipients


def send_subscription_emails(post):
    """ Send an email to all those subscribed to a tag if a new post
        with that tag was published to the repo
    """
    if 'mail' not in current_app.config:
        logger.warning(
            'Mail subsystem is not configured. Silently dropping email.')
        return

    # if this post is tagged as private - send no emails
    post_full_tags = [tag.name for tag in post.tags]
    for full_tag in post_full_tags:
        if full_tag in current_app.config.get('EXCLUDED_TAGS', []):
            return

    for tag in post.tags:
        send_subscription_email(post, tag)


def send_subscription_email(post, tag):
    """
    Send an email to all those subscribed to a tag if a new post
    with that tag was published to the repo

    :param post: The new post that the email is sent about
    :type post: The Post object
    :param tag: The tag that people are subscribed to
    :type tag: The Tag object
    :return: No return
    :rtype: None
    """
    # format recipients for email and mark as sent
    recipient_users = subscription_email_recipients(post, tag)

    if not recipient_users:
        return

    recipients_bcc = [usernames_to_emails([user.identifier])[
        0] for user in recipient_users]

    if not recipients_bcc:
        return

    default_recipients = ['knowledge_consumer@notreal.com']
    subject = f'New knowledge post: {post.title}'
    post_authors = [p.format_name for p in post.authors]
    post_tags = [t.name for t in post.tags]
    msg = Message(subject=subject, recipients=default_recipients,
                  bcc=recipients_bcc)

    # Extract bytes from post thumbnail or fallback to the default one
    thumb_bytes = None
    if post.thumbnail:
        try:
            reg_search = re.search('data:.*;base64,(.*)', post.thumbnail)
            if reg_search:
                thumb_bytes = base64.b64decode(reg_search.group(1))
            else:
                # Download image from url
                response = requests.get(post.thumbnail)
                if response.ok:
                    thumb_bytes = response.content
        except Exception as e:
            logger.warning(f'Exception encountered: {e}')
            pass

    if not thumb_bytes:
        with current_app.open_resource(
                'static/images/default_thumbnail.png') as f:
            thumb_bytes = f.read()

    # Attach thumbnail to the email (base64 embedded images are not
    # supported by many email clients)
    msg.attach('thumb.png', 'image/png', thumb_bytes, 'inline',
               headers=[['Content-ID', '<Thumb>']])

    # Plain mail
    msg.body = render_template(
        'email_templates/subscription_email.txt',
        full_tag=tag.name,
        page_id=post.path,
        post_title=post.title,
        post_tldr=post.tldr,
        post_authors=post_authors,
        post_tags=post_tags,
        knowledge_app_base_url=current_app.config['SERVER_NAME'])

    # Rich email
    msg.html = render_template(
        'email_templates/subscription_email.html',
        full_tag=tag.name,
        page_id=post.path,
        post_title=post.title,
        post_tldr=post.tldr,
        post_authors=post_authors,
        post_tags=post_tags,
        post_thumbnail=thumb_bytes,
        knowledge_app_base_url=current_app.config['SERVER_NAME'])

    for user in recipient_users:
        # mark email as sent just before you send the email
        email_sent = Email(user_id=user.id,
                           trigger_id=tag.id,
                           trigger_type='subscription',
                           object_id=post.id,
                           object_type='post',
                           subject=subject,
                           text=msg.html)
        db_session.add(email_sent)
        db_session.commit()

    current_app.config['mail'].send(msg)


def send_comment_email(path, comment_text, commenter='Someone'):
    if 'mail' not in current_app.config:
        logger.warning('Mail subsystem is not configured. '
                       'Silently dropping email.')
        return

    kp = current_repo.post(path)
    headers = kp.headers

    msg = Message('Someone commented on your post!',
                  usernames_to_emails(headers['authors']))
    msg.body = render_template(
        'email_templates/comment_email.txt',
        commenter=commenter,
        comment_text=comment_text,
        post_title=headers['title'],
        post_url=url_for('posts.render', path=path, _external=True))
    current_app.config['mail'].send(msg)


def send_internal_error_email(subject_line, **kwargs):
    if 'mail' not in current_app.config:
        logger.warning('Mail subsystem is not configured. '
                       'Silently dropping email.')
        return
    recipients = usernames_to_emails(current_repo.config.editors)
    msg = Message(subject_line, recipients)
    msg.body = render_template(
        'email_templates/internal_error_email.txt', **kwargs)
    current_app.config['mail'].send(msg)


def send_reviewer_request_email(path, reviewer):
    if 'mail' not in current_app.config:
        logger.warning('Mail subsystem is not configured. '
                       'Silently dropping email.')
        return
    subject = 'Someone requested a web post review from you!'
    msg = Message(subject, [reviewer])
    msg.body = render_template('email_templates/reviewer_request_email.txt',
                               post_url=url_for('editor.editor',
                                                path=path, _external=True))
    current_app.config['mail'].send(msg)


def send_review_email(path, comment_text, commenter='Someone'):
    if 'mail' not in current_app.config:
        logger.warning('Mail subsystem is not configured. '
                       'Silently dropping email.')
        return

    kp = current_repo.post(path)
    headers = kp.headers

    msg = Message('Someone reviewed your post!',
                  usernames_to_emails(headers['authors']))
    msg.body = render_template(
        'email_templates/review_email.txt',
        commenter=commenter,
        comment_text=comment_text,
        post_title=headers['title'],
        post_url=url_for('editor.editor', path=path, _external=True))
    current_app.config['mail'].send(msg)
