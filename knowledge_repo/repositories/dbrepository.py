from builtins import object

import logging
import posixpath

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, mapper
from sqlalchemy.sql import func

from sqlalchemy import Table, Column, Integer, String, DateTime, BLOB, MetaData
from ..repository import KnowledgeRepository

logger = logging.getLogger(__name__)


class DbKnowledgeRepository(KnowledgeRepository):
    _registry_keys = ['postgresql',
                      'postgresql+psycopg2',
                      'postgresql+pg8000',
                      'mysql',
                      'mysql+mysqldb',
                      'mysql+mysqlconnector',
                      'mysql+oursql',
                      'oracle',
                      'oracle+cx_oracle',
                      'mssql',
                      'mssql+pyodbc',
                      'mssql+pymssql',
                      'sqlite']  # TODO: Use regex matching and add the rest?

    def init(self, auto_create=True):

        # TODO handle if user does not pass in table sqlite://path.db
        uri_splt = self.uri.split(":")
        engine_uri = ":".join(uri_splt[:-1])
        table_name = uri_splt[-1]

        metadata = MetaData()
        postref_table = Table(table_name, metadata,
                              Column('id', Integer, primary_key=True),
                              Column('created_at', DateTime, default=func.now()),
                              Column('uuid', String(512)),
                              Column('path', String(512)),
                              Column('revision', Integer, default=0),
                              Column('status', Integer, default=self.PostStatus.DRAFT.value),
                              Column('ref', String(512)),
                              Column('data', BLOB))
        self.engine = create_engine(engine_uri)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        if auto_create:
            postref_table.create(self.engine, checkfirst=True)

        class PostRef(object):
            pass
        mapper(PostRef, postref_table)
        self.PostRef = PostRef

    # ------------- Repository actions / state ------------------------------------
    def session_begin(self):
        pass

    def session_end(self):
        self.session.remove()

    @property
    def revision(self):
        return self.session.query(func.max(self.PostRef.created_at))

    def update(self):
        pass

    def set_active_draft(self, path):
        pass

    @property
    def status(self):
        try:
            session = self.Session()
            session.remove()
        except:
            return {'status': 'unable to connect to uri {}'.format(self.uri)}
        return {'status': 'super'}

    @property
    def status_message(self):
        return self.status['status']

    # -------------- Post retrieval methods --------------------------------------

    def _dir(self, prefix, statuses):
        query = self.session.query(self.PostRef.path)
        if prefix is not None:
            query = query.filter(self.PostRef.status.like('{}%'.format(prefix)))
        query = query.filter(self.PostRef.status.in_([status.value for status in statuses]))

        for (prefix,) in query.distinct():
            if prefix is not None:
                yield prefix

    # -------------- Post submission / addition user flow --------------------

    def _add_prepare(self, kp, path, update=False):
        pass

    def _add_cleanup(self, kp, path, update=False):
        self.__set_post_status(path, self.PostStatus.DRAFT, kp.revision)

    def _submit(self, path):  # Submit a post for review
        # Latest revision for draft
        revision = self._kp_get_revision(path, self.PostStatus.DRAFT, enforce_exists=True)
        self.__set_post_status(path, status=self.PostStatus.SUBMITTED, revision=revision)

    def _accept(self, path):  # Approve a post to publish
        # Latest revision for submitted draft
        revision = self._kp_get_revision(path, self.PostStatus.SUBMITTED, enforce_exists=True)
        if self.__get_post_status(path, revision) != self.PostStatus.PUBLISHED:
            self.__set_post_status(path, status=self.PostStatus.UNPUBLISHED, revision=revision)

    def _publish(self, path):  # Publish a post for general perusal
        # Latest revision for unpublished
        revision = self._kp_get_revision(path, self.PostStatus.UNPUBLISHED, enforce_exists=True)
        if self.__get_post_status(path, revision) == self.PostStatus.UNPUBLISHED:
            self.__set_post_status(path, status=self.PostStatus.PUBLISHED, revision=revision)

    def _unpublish(self, path):  # Unpublish a post
        # Latest revision for published post
        revision = self._kp_get_revision(path, self.PostStatus.PUBLISHED, enforce_exists=True)
        self.__set_post_status(path, status=self.PostStatus.UNPUBLISHED, revision=revision)

    def _remove(self, path, all=False):
        raise NotImplementedError

    def __set_post_status(self, path, status, revision=None):
        revision = revision or self._kp_get_revision(path, enforce_exists=True)
        postrefs = (self.session.query(self.PostRef)
                                .filter(self.PostRef.path == path)
                                .filter(self.PostRef.revision == revision)).all()
        for postref in postrefs:
            postref.status = status.value
        self.session.commit()

    def __get_post_status(self, path, revision=None):
        revision = revision or self._kp_get_revision(path, enforce_exists=True)
        post_refs = (self.session.query(self.PostRef)
                                 .filter(self.PostRef.path == path)
                                 .filter(self.PostRef.revision == revision)
                                 .distinct()).all()
        return self.PostStatus(min([pr.status if pr.status else 0 for pr in post_refs]))  # return the most 'open' status

    # ----------- Knowledge Post Data Retrieval/Pushing Methods --------------------

    def _kp_uuid(self, path):
        result = self.session.query(self.PostRef.uuid).filter(self.PostRef.path == path).first()
        if result:
            return result[0]
        return None

    def _kp_exists(self, path, revision=None):
        query = (self.session.query(self.PostRef)
                             .filter(self.PostRef.path == path))
        if revision:
            query = query.filter(self.PostRef.revision == revision)
        postref = query.first()
        return postref

    def _kp_status(self, path, revision=None, detailed=False):
        revision = revision or self._kp_get_revision(path, enforce_exists=True)

        postref = (self.session.query(self.PostRef)
                               .filter(self.PostRef.path == path)
                               .filter(self.PostRef.revision == revision)).first()

        if not postref:
            raise ValueError("No such post exists for path '{}' and revision '{}'.".format(path, revision))

        if detailed:
            return self.__get_post_status(path, revision), None
        return self.__get_post_status(path, revision)

    def _kp_get_revision(self, path, status=None, enforce_exists=False):
        query = self.session.query(self.PostRef.revision).filter(self.PostRef.path == path)
        if status is not None:
            query.filter(self.PostRef.status == status.value)
        revision = query.order_by(self.PostRef.revision.desc()).first()

        # TODO fix this
        if revision:
            revision = revision[0]
        if enforce_exists and revision is None:
            raise ValueError('No post found at {} (with status of {})'.format(path, status))
        return revision

    def _kp_get_revisions(self, path):
        revisions = (self.session.query(self.PostRef.revision)
                                 .filter(self.PostRef.path == path)
                                 .distinct()).all()
        return revisions

    def _kp_read_ref(self, path, reference, revision=None):
        revision = revision or self._kp_get_revision(path, enforce_exists=True)
        data = (self.session.query(self.PostRef)
                            .filter(self.PostRef.path == path)
                            .filter(self.PostRef.ref == reference)
                            .filter(self.PostRef.revision == revision)).first().data
        return data

    def _kp_dir(self, path, parent=None, revision=None):
        if parent:
            path = posixpath.join(path, parent)
        revision = revision or self._kp_get_revision(path, enforce_exists=True)
        refs = (self.session.query(self.PostRef.ref)
                            .filter(self.PostRef.path == path)
                            .filter(self.PostRef.revision == revision)).all()
        for (ref,) in refs:
            if ref is not None:
                yield ref

    def _kp_has_ref(self, path, reference, revision=None):
        revision = revision or self._kp_get_revision(path, enforce_exists=True)
        ref = (self.session.query(self.PostRef.ref)
                           .filter(self.PostRef.path == path)
                           .filter(self.PostRef.ref == reference)
                           .filter(self.PostRef.revision == revision)).first()

        return ref is not None

    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        revision = revision or self._kp_get_revision(path, enforce_exists=False) or 0

        postref = (self.session.query(self.PostRef)
                               .filter(self.PostRef.path == path)
                               .filter(self.PostRef.ref == reference)
                               .filter(self.PostRef.revision == revision)).first()

        if postref is None:
            postref = self.PostRef()
            postref.path = path
            postref.ref = reference
            postref.uuid = uuid
            postref.revision = revision
            self.session.add(postref)

        postref.data = data
        self.session.commit()

    def _kp_new_revision(self, path, uuid=None):
        revision = self._kp_get_revision(path, enforce_exists=False) or 0
        return revision + 1
