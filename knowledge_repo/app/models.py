import os
import sys
import traceback
from future.utils import raise_with_traceback
from flask import current_app, request, g
from flask_sqlalchemy import SQLAlchemy
import functools
from collections import defaultdict
import datetime

from werkzeug.local import LocalProxy
from sqlalchemy import func, distinct, and_, select, UniqueConstraint
import logging

from knowledge_repo._version import __version__
from knowledge_repo.repository import KnowledgeRepository
from .proxies import current_repo, db_session
from .utils.models import unique_constructor
from .utils.search import get_keywords
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

logger = logging.getLogger(__name__)

db = SQLAlchemy()
db_session = LocalProxy(lambda: current_app.db.session)


class IndexMetadata(db.Model):
    __tablename__ = 'index_metadata'
    __table_args__ = (
        UniqueConstraint('type', 'name', name='_uc_type_name'),
    )

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    type = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(512), nullable=False)
    value = db.Column(db.String(512), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    @classmethod
    def get(cls, type, name, default=None):
        m = db_session.query(IndexMetadata).filter(IndexMetadata.type == type).filter(IndexMetadata.name == name).first()
        if m is not None:
            return m.value
        return default

    @classmethod
    def set(cls, type, name, value):
        m = db_session.query(IndexMetadata).filter(IndexMetadata.type == type).filter(IndexMetadata.name == name).first()
        if m is not None:
            m.value = value
        else:
            m = IndexMetadata(type=type, name=name, value=value)
            db_session.add(m)

    @classmethod
    def get_last_update(cls, type, name):
        m = db_session.query(IndexMetadata).filter(IndexMetadata.type == type).filter(IndexMetadata.name == name).first()
        if m is not None:
            return m.updated_at
        return None


class PostAuthorAssoc(db.Model):
    __tablename__ = 'assoc_post_author'

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    order = db.Column(db.Integer)

    post = db.relationship('Post', lazy='joined')
    author = db.relationship('User', lazy='joined')


assoc_post_tag = db.Table(
    'assoc_post_tag',
    db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

assoc_post_group = db.Table(
    'assoc_post_group',
    db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

assoc_group_user = db.Table(
    'assoc_group_user',
    db.Model.metadata,
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
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
    object_action = db.Column(db.String(100))
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=func.now())
    error_message = db.Column(db.Text())
    version = db.Column(db.String(100))

    class logged(object):

        def __init__(self, route, object_extractor=None):
            self._route = route
            self._object_extractor = object_extractor

        def __getattr__(self, attr):
            return getattr(self._route, attr)

        def __call__(self, *args, **kwargs):
            if not current_app.config.get('REPOSITORY_INDEXING_ENABLED', True):
                return self._route(*args, **kwargs)

            log = PageView(
                page=request.full_path,
                endpoint=request.endpoint,
                user_id=g.user.id,
                ip_address=request.remote_addr,
                version=__version__
            )
            log.object_id, log.object_type, log.object_action, reextract_after_request = self.extract_objects(*args, **kwargs)
            db_session.add(log)

            try:
                return self._route(*args, **kwargs)
            except Exception as e:
                tb = traceback.extract_tb(sys.exc_info()[2])
                log.error_message = type(e).__name__ + ': ' + str(e) + '\nTraceback (most recent call last):\n' + '\n'.join(traceback.format_list(tb[1:]))
                raise_with_traceback(e)
            finally:
                # Extract object id and type after response generated (if requested) to ensure
                # most recent data is collected
                if reextract_after_request:
                    log.object_id, log.object_type, log.object_action, _ = self.extract_objects(*args, **kwargs)

                db_session.rollback()
                db_session.add(log)
                db_session.commit()

        def object_extractor(self, extractor):
            self._object_extractor = extractor
            return self

        def extract_objects(self, *args, **kwargs):
            if self._object_extractor is None:
                return None, None, None, False
            try:
                object_info = self._object_extractor(*args, **kwargs)
            except Exception as e:
                logger.warning("Error using object extractor: " + str(e))
                object_info = {'id': (-1), 'type': None}
            assert isinstance(object_info, dict), "Object extractors must return a dictionary."
            assert len(set(['id', 'type']).difference(object_info.keys())) == 0 and len(set(object_info.keys()).difference(['id', 'type', 'action', 'may_change'])) == 0, "Object extractors must at least include the keys 'id' and 'type', and optionally 'action' and 'may_change'. Was provided with: {}".format(str(list(object_info.keys())))
            object_info = defaultdict(lambda: None, object_info)
            return object_info['id'], object_info['type'], object_info['action'], object_info['may_change'] or False


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

    _posts_assoc = db.relationship("PostAuthorAssoc")
    posts = association_proxy('_posts_assoc', 'post')  # This property should not directly modified

    @property
    def format_name(self):
        username_to_name = current_repo.config.username_to_name
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
        if len(post_ids) == 0:
            return []
        excluded_tags = current_app.config.get('EXCLUDED_TAGS', [])
        posts = (db.session.query(Post)
                 .filter(Post.id.in_(post_ids))
                 .filter(~Post.tags.any(Tag.name.in_(excluded_tags)))
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
    uuid = db.Column(db.String(100), unique=True)
    path = db.Column(db.String(512), unique=True)
    project = db.Column(db.String(512), nullable=True)  # DEPRECATED
    repository = db.Column(db.String(512))
    revision = db.Column(db.Integer())

    title = db.Column(db.Text())
    tldr = db.Column(db.Text)
    keywords = db.Column(db.Text)
    thumbnail = db.Column(db.Text())

    private = db.Column(db.Integer())

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now())

    _authors_assoc = db.relationship("PostAuthorAssoc",
                                     order_by='PostAuthorAssoc.order',
                                     collection_class=ordering_list('order'),
                                     cascade="all, delete-orphan")
    _authors = association_proxy('_authors_assoc', 'author',
                                 creator=lambda author: PostAuthorAssoc(author=author),)

    @hybrid_property
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

    _tags = db.relationship("Tag", secondary=assoc_post_tag, backref='posts',
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

    @property
    def contains_excluded_tag(self):
        excluded_tags = current_app.config.get('EXCLUDED_TAGS', [])
        return any([tag.name in excluded_tags for tag in self.tags])

    _groups = db.relationship("Group", secondary=assoc_post_group, backref='posts',
                              lazy='subquery')

    @hybrid_property
    def groups(self):
        return self._groups

    @groups.setter
    def groups(self, groups):
        # given a list of group_names, we add it.
        group_objs = []

        for group in groups:
            if not isinstance(group, Group):
                group = Group(name=group.strip())
            group_objs.append(group)

        # create an implicit group, group_post.id, to add
        # single users to
        group = Group(name=":post_group_" + str(self.id))

        # this created group should have the author associated with it
        # so they can add people to the post
        group.users = self.authors
        group_objs.append(group)

        self._groups = group_objs

    _status = db.Column('status', db.Integer(), default=0)

    @hybrid_property
    def status(self):
        return current_repo.PostStatus(self._status or 0)

    @status.expression
    def status(self):
        return func.coalesce(self._status, 0)

    @status.setter
    def status(self, status):
        if status is None:
            self._status = None
        else:
            assert isinstance(status, KnowledgeRepository.PostStatus), "Status must be an instance of KnowledgeRepository.PostStatus.Status or None"
            self._status = status.value

    @hybrid_property
    def is_published(self):
        return self.status == current_repo.PostStatus.PUBLISHED

    @is_published.expression
    def is_published(self):
        return func.coalesce(self._status, 0) == current_repo.PostStatus.PUBLISHED.value

    _views = db.relationship("PageView", lazy='dynamic',
                             primaryjoin="and_(foreign(PageView.object_id)==Post.id, "
                                         "PageView.object_type=='post',"
                                         "PageView.object_action=='view')")

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

        self.uuid = kp.uuid
        self.path = kp.path
        self.project = headers.get('project')
        self.repository = kp.repository_uri
        self.revision = kp.revision
        self.title = headers['title']
        self.tldr = headers['tldr']
        self.authors = headers.get('authors', [])
        self.tags = headers.get('tags', [])
        self.keywords = get_keywords(self)
        self.thumbnail = kp.thumbnail_uri

        self.created_at = headers['created_at']
        self.updated_at = headers['updated_at']
        if self.created_at > self.updated_at:
            self.updated_at = self.created_at

        self.status = kp.status

        self.private = 0
        # we do this check so that no header (None) and False are treated the same
        if headers.get('private', ''):
            self.private = 1
            self.groups = headers.get('allowed_groups', [])


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


@unique_constructor(
    lambda name: name,
    lambda query, name: query.filter(Group.name == name)
)
class Group(db.Model):

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)

    _users = db.relationship("User", secondary=assoc_group_user, backref='users',
                             lazy='subquery')

    @hybrid_property
    def users(self):
        return self._users

    @users.setter
    def users(self, user_objs):
        self._users = self._users + user_objs
