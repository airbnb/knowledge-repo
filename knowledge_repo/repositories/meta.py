import posixpath

from ..repository import KnowledgeRepository


class MetaKnowledgeRepository(KnowledgeRepository):
    _registry_keys = None

    def init(self):
        pass

    def __repos_for_prefix(self, path_prefix=None):
        repo_prefixes = sorted(self.uri.keys(), key=lambda x: len(x), reverse=True)
        for repo_prefix in repo_prefixes:
            if path_prefix is None or path_prefix.startswith(repo_prefix):
                repo_prefix, repo, repo_path = self.__repo_for_path(path_prefix or repo_prefix)
                repo_path = None if not repo_path else repo_path
                yield repo_prefix, repo, repo_path

    def __repo_for_path(self, path):
        path_prefixes = sorted(self.uri.keys(), key=lambda x: len(x), reverse=True)
        for prefix in path_prefixes:
            if path.startswith(prefix):
                relpath = posixpath.relpath(path, prefix or '.') if path else ''
                return prefix, self.uri[prefix], relpath if relpath != '.' else None
        raise ValueError("No KnowledgeRepository found for '{}'.".format(path))

    def __distribute_method(self, method, **kwargs):
        return {name: getattr(repo, method)(**kwargs) for name, repo in list(self.uri.items())}

    def __distribute_attribute(self, attribute):
        return {name: getattr(repo, attribute) for name, repo in list(self.uri.items())}

    def __delegate_for_path(self, path, method, **kwargs):
        prefix, repo, path = self.__repo_for_path(path)
        return getattr(repo, method)(path=path, **kwargs)

    def __delegate_for_kp(self, kp, path, method, **kwargs):
        prefix, repo, path = self.__repo_for_path(path)
        return getattr(repo, method)(kp=kp, path=path, **kwargs)

    # ------------- Repository actions / state ------------------------------------

    def session_begin(self):
        return self.__distribute_method('session_begin')

    def session_end(self):
        return self.__distribute_method('session_end')

    @property
    def revision(self):
        return self.__distribute_attribute('revision')

    def update(self):
        return self.__distribute_method('update')

    def set_active_draft(self, path):
        return self.__delegate_for_path(path, 'set_active_draft')

    @property
    def status(self):
        return self.__distribute_attribute('status')

    @property
    def status_message(self):
        return self.__distribute_attribute('status_message')

    # -------------- Post retrieval methods --------------------------------------

    def _dir(self, prefix, statuses):
        # TODO: Handle masked paths
        for (repo_prefix, repo, nested_prefix) in self.__repos_for_prefix(prefix):
            for path in repo.dir(prefix=nested_prefix, status=statuses):
                yield posixpath.join(repo_prefix, path)

    # -------------- Post submission / addition user flow --------------------

    def _add_prepare(self, kp, path, update=False, **kwargs):
        return self.__delegate_for_kp(kp, path, '_add_prepare', update=update, **kwargs)

    def _add_cleanup(self, kp, path, update=False, **kwargs):
        return self.__delegate_for_kp(kp, path, '_add_cleanup', update=update, **kwargs)

    def _submit(self, path):  # Submit a post for review
        return self.__delegate_for_path(path, '_submit')

    def _accept(self, path):
        return self.__delegate_for_path(path, '_accept')

    def _publish(self, path):  # Publish a post for general perusal
        return self.__delegate_for_path(path, '_publish')

    def _unpublish(self, path):
        return self.__delegate_for_path(path, '_unpublish')

    def _remove(self, path, all=False):
        return self.__delegate_for_path(path, '_remove', all=all)

    # ----------- Knowledge Post Data Retrieval/Pushing Methods --------------------

    def _kp_repository_uri(self, path):
        prefix, repository, repo_path = self.__repo_for_path(path)
        return '{{{prefix}}}{repository_uri}'.format(prefix=prefix, repository_uri=repository._kp_repository_uri(repo_path))

    def _kp_uuid(self, path):
        return self.__delegate_for_path(path, '_kp_uuid')

    def _kp_exists(self, path, revision=None):
        return self.__delegate_for_path(path, '_kp_exists', revision=revision)

    def _kp_status(self, path, revision=None, detailed=False):
        return self.__delegate_for_path(path, '_kp_status', revision=revision, detailed=detailed)

    def _kp_is_published(self, path):
        return self.__delegate_for_path(path, '_kp_is_published')

    def _kp_get_revision(self, path):
        return self.__delegate_for_path(path, '_kp_get_revision')

    def _kp_get_revisions(self, path):
        return self.__delegate_for_path(path, '_kp_get_revisions')

    def _kp_read_ref(self, path, reference, revision=None):
        return self.__delegate_for_path(path, '_kp_read_ref', reference=reference, revision=revision)

    def _kp_dir(self, path, parent=None, revision=None):
        return self.__delegate_for_path(path, '_kp_dir', parent=parent, revision=revision)

    def _kp_has_ref(self, path, reference, revision=None):
        return self.__delegate_for_path(path, '_kp_has_ref', reference=reference, revision=revision)

    def _kp_diff(self, path, head, base):
        return self.__delegate_for_path(path, '_kp_diff', head=head, base=base)

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        return self.__delegate_for_path(path, '_kp_write_ref', reference=reference, data=data, uuid=uuid, revision=revision)

    def _kp_new_revision(self, path, uuid=None):
        return self.__delegate_for_path(path, '_kp_new_revision', uuid=uuid)
