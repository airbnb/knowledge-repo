from ..repository import KnowledgeRepository


class StubKnowledgeRepository(KnowledgeRepository):
    _registry_keys = None

    def init(self):
        pass

    # ------------- Repository actions / state ------------------------------------

    def session_begin(self):
        pass

    def session_end(self):
        pass

    @property
    def revision(self):
        raise NotImplementedError

    def update(self):
        pass

    def set_active_draft(self, path):
        pass

    @property
    def status(self):
        raise NotImplementedError

    @property
    def status_message(self):
        raise NotImplementedError

    # -------------- Post retrieval methods --------------------------------------

    def _dir(self, prefix, statuses):
        raise NotImplementedError

    # -------------- Post submission / addition user flow --------------------

    def _add_prepare(self, kp, path, update=False):
        raise NotImplementedError

    def _add_cleanup(self, kp, path, update=False):
        raise NotImplementedError

    def _submit(self, path):  # Submit a post for review
        raise NotImplementedError

    def _accept(self, path):
        raise NotImplementedError

    def _publish(self, path):  # Publish a post for general perusal
        raise NotImplementedError

    def _unpublish(self, path):
        raise NotImplementedError

    def _remove(self, path, all=False):
        raise NotImplementedError

    # ----------- Knowledge Post Data Retrieval/Pushing Methods --------------------

    def _kp_uuid(self, path):
        raise NotImplementedError

    def _kp_exists(self, path, revision=None):
        raise NotImplementedError

    def _kp_status(self, path, revision=None, detailed=False):
        raise NotImplementedError

    def _kp_get_revision(self, path, status=None):
        raise NotImplementedError

    def _kp_get_revisions(self, path):
        raise NotImplementedError

    def _kp_read_ref(self, path, reference, revision=None):
        raise NotImplementedError

    def _kp_dir(self, path, parent=None, revision=None):
        raise NotImplementedError

    def _kp_has_ref(self, path, reference, revision=None):
        raise NotImplementedError

    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        raise NotImplementedError

    def _kp_new_revision(self, path, uuid=None):
        raise NotImplementedError
