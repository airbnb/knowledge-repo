#!/usr/bin/env python
import os
from flask import current_app, request
from flask_sqlalchemy import SQLAlchemy
import functools

from werkzeug.local import LocalProxy
from sqlalchemy import func, distinct, and_, select
import base64
import mimetypes
import logging

from knowledge_repo.repository import KnowledgeRepository
from .constants import WebPostStatus, GitPostStatus, TagConstants
from .proxies import current_repo
from .utils.models import unique_constructor
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

logger = logging.getLogger(__name__)

db = SQLAlchemy()
db_session = LocalProxy(lambda: current_app.db.session)

PostAuthors = db.Table(
    'knowledge_post_author',
    db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
)

PostTags = db.Table(
    'knowledge_post_tags',
    db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    type = db.Column(db.String(100), default='post')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class PageView(db.Model):
    __tablename__ = 'pageviews'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(512))
    endpoint = db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(100))
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=func.now())
    error_message = db.Column(db.Text())

    @classmethod
    def log_pageview(cls, f):
        """Decorator to log user actions"""
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            dct = request.args.to_dict()
            dct.update(kwargs)

            username = current_app.config.get(
                'AUTH_USERNAME_DEFAULT') or 'knowledge_default'
            if current_app.config.get('AUTH_USERNAME_REQUEST_HEADER'):
                username = request.headers.get(current_app.config.get(
                    'AUTH_USERNAME_REQUEST_HEADER'), username)

            user = User.query.filter(User.username == username).first()
            if not user:
                user = User(username=username)
                db.session.add(user)
                db.session.commit()

            user_id = user.id

            ip_address = request.remote_addr

            page = request.full_path
            endpoint = request.endpoint
            blueprint = request.blueprint

            object_id, object_type = None, None

            if 'markdown' in request.args:
                # we're looking at a post
                object_type = 'post'
                post_path = request.args.get('markdown', '')
                object_id = Post.query.filter(Post.path == post_path).first().id

            if blueprint == 'comments':
                object_type = 'comment'
                comment_id = request.args.get('comment_id', '')
                object_id = comment_id if comment_id else None

            if blueprint == 'tag':
                object_type = 'tag'
                tag_name = None
                if endpoint in ['tag.delete_tag_post', 'tag.toggle_tag_subscription']:
                    tag_name = request.args.get('tag_name', '')

                if endpoint == 'tag.tag_pages':
                    tag_name = request.args.get('tag', '')

                if endpoint == 'tag.edit_tag_description':
                    data = request.get_json()
                    tag_name = data['tagName']

                if endpoint == 'tag.rename_tag':
                    data = request.get_json()
                    old_tag = data['oldTag']
                    tag_name = old_tag.replace('__', '/')

                if tag_name:
                    tag_obj = (Tag.query
                                  .filter(Tag.name == tag_name)
                                  .first())
                    object_id = tag_obj.id

                if endpoint == 'tag.remove_posts_tags':
                    data = request.get_json()
                    tag_id = data['tagId']
                    object_id = int(tag_id)

                if endpoint == 'tag.tag_list':
                    object_type = 'post'
                    post_path = request.args.get('post_id', '')
                    object_id = Post.query.filter(Post.path == post_path).first().id

            if blueprint == 'vote':
                object_type = 'post'
                post_path = request.args.get('post_id', '')
                object_id = Post.query.filter(Post.path == post_path).first().id

            log = cls(
                page=page,
                endpoint=endpoint,
                user_id=user_id,
                object_id=object_id,
                object_type=object_type,
                ip_address=ip_address
            )
            db.session.add(log)
            db.session.commit()
            return f(*args, **kwargs)
        return wrapped


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(100), default='post')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


@unique_constructor(
    lambda username: username,
    lambda query, username: query.filter(User.username == username)
)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=func.now())

    # posts field created by backreferences

    @property
    def format_name(self):
        username_to_name = current_app.config['repo'].config.username_to_name
        return username_to_name(self.username)

    @property
    def get_subscriptions(self):
        """Get the subscriptions associated with a user.

        Return an array of strings of tag_names
        """
        subscriptions = (db.session.query(Subscription)
                         .filter(Subscription.user_id == self.id)
                         .all())
        out_subscriptions = []
        for s in subscriptions:
            if s.object_type == 'tag':
                tag_obj = (db.session.query(Tag)
                           .filter(Tag.id == s.object_id)
                           .first())
                if tag_obj:
                    full_name = tag_obj.name
                    out_subscriptions.append(full_name)
                else:
                    db.session.delete(s)
        return out_subscriptions

    @property
    def get_liked_posts(self):
        """
        :return: Posts that a user has liked
        :rtype: list
        """
        votes = (db.session.query(Vote)
                 .filter(Vote.user_id == self.id)
                 .all())
        post_ids = [vote.object_id for vote in votes]
        posts = (db.session.query(Post)
                 .filter(Post.id.in_(post_ids))
                 .all())
        return posts


@unique_constructor(
    lambda name: name,
    lambda query, name: query.filter(Tag.name == name)
)
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    _description = db.Column('description', db.Text())
    created_at = db.Column(db.DateTime, default=func.now())

    @hybrid_property
    def description(self):
        if self._description:
            return self._description
        return "All posts with tag '{}'.".format(self.name)

    @description.expression
    def description(self):
        raise NotImplementedError


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(100))  # Currently just tag
    created_at = db.Column(db.DateTime, default=func.now())


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    # uuid = db.Column(db.String, unique=True)
    path = db.Column(db.String(512), unique=True)
    project = db.Column(db.String(512), nullable=True)  # DEPRECATED
    repository = db.Column(db.String(512))
    revision = db.Column(db.Integer())

    title = db.Column(db.Text())
    tldr = db.Column(db.Text)
    keywords = db.Column(db.Text)
    thumbnail = db.Column(db.Text())

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now())

    _authors = db.relationship("User", secondary=PostAuthors, backref='posts')

    @property
    def authors(self):
        return self._authors

    @authors.setter
    def authors(self, authors):
        """
        Sets the tags of the post to the tags given in comma delimited string
        form in tags_string
        """
        user_objs = []

        for author in authors:
            if not isinstance(author, User):
                author = author.strip()
                author = User(username=author)
            user_objs.append(author)

        self._authors = user_objs

    @hybrid_property
    def authors_string(self):
        return ', '.join([author.format_name for author in self.authors])

    @authors_string.expression
    def authors_string(self):
        raise NotImplementedError

    _tags = db.relationship("Tag", secondary=PostTags, backref='posts',
                            lazy='subquery')

    @hybrid_property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags):
        """
        Sets the tags of the post to the tags given in comma delimited string
        form in tags_string
        """
        tag_objs = []

        for tag in tags:
            if not isinstance(tag, Tag):
                tag = tag.strip()
                if tag[0] == "#":
                    tag = tag[1:]
                tag = Tag(name=tag)
            tag_objs.append(tag)

        self._tags = tag_objs

    _status = db.Column('status', db.Integer(), default=0)

    @hybrid_property
    def status(self):
        return current_repo.PostStatus.for_value(self._status or 0)

    @status.expression
    def status(self):
        return func.coalesce(self._status, 0)

    @status.setter
    def status(self, status):
        if status is None:
            self._status = None
        else:
            assert isinstance(status, KnowledgeRepository.PostStatus.Status), "Status must be an instance of KnowledgeRepository.PostStatus.Status or None"
            self._status = status.value

    @hybrid_property
    def is_published(self):
        return self.status == current_repo.PostStatus.PUBLISHED

    @is_published.expression
    def is_published(self):
        return func.coalesce(self._status, 0) == current_repo.PostStatus.PUBLISHED.value

    _views = db.relationship("PageView", lazy='dynamic',
                             primaryjoin="and_(foreign(PageView.object_id)==Post.id, "
                                         "PageView.object_type=='post')")

    @hybrid_property
    def views(self):
        return self._views.all()

    @hybrid_property
    def view_count(self):
        return self._views.count()

    @view_count.expression
    def view_count(self):
        return (select([func.count(PageView.id)])
                .where(PageView.object_id == self.id)
                .where(PageView.object_type == 'post')
                .label("view_count"))

    @hybrid_property
    def view_user_count(self):
        return (db.session.query(func.count(distinct(PageView.user_id)))
                          .filter(PageView.object_id == self.id)
                          .filter(PageView.object_type == 'post')
                          .scalar())

    @view_user_count.expression
    def view_user_count(self):
        return (select([func.count(distinct(PageView.user_id))])
                .where(PageView.object_id == self.id)
                .where(PageView.object_type == 'post')
                .label("view_user_count"))

    _votes = db.relationship("Vote", lazy='dynamic',
                             primaryjoin="and_(foreign(Vote.object_id)==Post.id, "
                                         "Vote.object_type=='post')")

    @hybrid_property
    def votes(self):
        return self._votes.all()

    @hybrid_property
    def vote_count(self):
        """ Given the path of a post, return the total likes """
        return self._votes.count()

    @vote_count.expression
    def vote_count(self):
        return (select([func.count(Vote.id)])
                .where(Vote.object_id == self.id)
                .where(Vote.object_type == 'post')
                .label("vote_count"))

    def vote_counted_for_user(self, user_id):
        return (db_session.query(Vote)
                          .filter(and_(Vote.object_id == self.id, Vote.object_type == 'post', Vote.user_id == user_id))
                          .first()) is not None

    _comments = db.relationship("Comment", lazy="dynamic",
                                primaryjoin="and_(foreign(Comment.post_id)==Post.id, "
                                            "Comment.type=='post')")

    @hybrid_property
    def comments(self):
        return self._comments.all()

    @hybrid_property
    def comment_count(self):
        """ Given the path of the a post, return the total comments """
        return self._comments.count()

    @comment_count.expression
    def comment_count(self):
        return (select([func.count(Comment.id)])
                .where(Comment.post_id == self.id)
                .where(Comment.object_type == 'post')
                .label("comments_count"))

    @property
    def kp(self):
        return current_repo.post(self.path)

    @property
    def text(self):
        return self.kp.read()

    def update_metadata_from_kp(self, kp):
        """
        :param kp: Maps fields of the model to values
        :type kp: KnowledgePost
        :param kp: Maps fields of the model to values
        :type kr: KnowledgeRepository
        :return: None
        :rtype: None
        """
        headers = kp.headers

        self.path = kp.path
        self.project = headers.get('project')
        self.repository = kp.repository_uri
        self.revision = kp.revision
        self.title = headers['title']
        self.tldr = headers['tldr']
        self.keywords = ",".join(headers.get('keywords', []))
        self.thumbnail = kp.thumbnail_uri

        self.created_at = headers['created_at']
        self.updated_at = headers['updated_at']
        if self.created_at > self.updated_at:
            self.updated_at = self.created_at

        self.authors = headers.get('authors', [])
        self.tags = headers.get('tags', [])
        self.status = kp.status


class Email(db.Model):

    __tablename__ = 'emails'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    trigger_id = db.Column(db.Integer)
    trigger_type = db.Column(db.String(100))
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(100))
    sent_at = db.Column(db.DateTime, default=func.now())
    subject = db.Column(db.Text)
    text = db.Column(db.Text)


from .utils.requests import from_request_get_user_info  # noqa
