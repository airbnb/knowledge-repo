import errno
import os
import shutil
import tempfile

import git

from knowledge_repo._version import __git_uri__


def clone_kr_to_directory(dir):
    dir = os.path.expanduser(dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
    assert os.path.isdir(dir)

    try:
        repo = git.Repo(dir)
        repo.remote().fetch()
    except git.InvalidGitRepositoryError:
        repo = git.Repo.clone_from(__git_uri__, dir)


def checkout_revision_to_dir(repo_path, revision, dir):
    repo_path = os.path.expanduser(repo_path)
    dir = os.path.expanduser(dir)
    repo = git.Repo(repo_path)
    repo.remote().fetch()
    repo.git.checkout(revision)
    return repo.git.checkout_index('-a', '-f', prefix=dir)


class CheckedOutRevision(object):

    def __init__(self, repo_path, revision):
        self.repo_path = repo_path
        self.revision = revision

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        checkout_revision_to_dir(self.repo_path, self.revision, self.dir + '/')
        return self.dir

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.dir)
