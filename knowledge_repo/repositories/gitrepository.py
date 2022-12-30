from ..repository import KnowledgeRepository
from ..utils.encoding import encode
from ..utils.files import get_path
from io import open
from knowledge_repo.utils.files import read_binary, write_binary
import git
import logging
import os
import re
import shutil
import yaml

logger = logging.getLogger(__name__)


class GitKnowledgeRepository(KnowledgeRepository):
    _registry_keys = ["git"]

    TEMPLATES = {
        "README.md": get_path(__file__, "../templates", "repository_readme.md"),
        ".knowledge_repo_config.yml": get_path(
            __file__, "../templates", "repository_config.yml"
        ),
    }

    @classmethod
    def create(cls, uri):
        path = uri.replace("git://", "")
        if os.path.exists(path):
            try:
                repo = git.Repo(path)
                logger.warning(
                    f"Repository already exists for uri '{uri}'. "
                    "Checking if configuration is needed..."
                )
            except git.InvalidGitRepositoryError:
                if os.path.isdir(path):
                    logger.warning(
                        f"Upgrading existing directory at '{path}' "
                        "to a git knowledge repository..."
                    )
                else:
                    raise RuntimeError(
                        f"File exists at nominated path: {path}. "
                        "Cannot proceed with repository initialization."
                    )

        repo = git.Repo.init(path, mkdir=True)

        # Add README and configuration templates
        added_files = 0

        for filename, template in cls.TEMPLATES.items():
            target = os.path.join(path, filename)
            if not os.path.exists(target):
                shutil.copy(template, target)
                repo.index.add([filename])
                added_files += 1
            else:
                logger.warning(f"Not overriding existing file '{filename}'.")

        if added_files > 0:
            repo.index.commit("Initial creation of knowledge repository.")

        return GitKnowledgeRepository(path)

    def init(self, config="git:///.knowledge_repo_config.yml", auto_create=False):
        self.config.update_defaults(published_branch="master")
        self.config.update_defaults(remote_name="origin")
        self.auto_create = auto_create
        self.path = self.uri.replace("git://", "")

        # Check if a legacy configuration exists, and if so, print a warning
        try:
            self.git_read(".knowledge_repo_config.py")
            logger.warning(
                "This knowledge repository has a legacy configuration file "
                "that will not be loaded due to security issues "
                "(.knowledge_repo_config.py). This may lead to unexpected "
                "behavior. Please talk to your local Knowledge Repo admins "
                "for advice if you are unsure."
            )
        except Exception as ex:
            # No need to print out the exception, as it is expected
            # print(f'Exception encountered: {ex}')
            logger.info(".knowledge_repo_config.py was not found.")
            pass

        if config.startswith("git:///"):
            assert config.endswith(
                ".yml"
            ), "In-repository configuration must be a YAML file."
            try:
                self.config.update(
                    yaml.safe_load(self.git_read(config.replace("git:///", "")))
                )
            except KeyError:
                logger.warning(f"Repository missing configuration file: {config}")
        else:
            self.config.update(config)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        assert isinstance(path, str), "The path specified must be a string."
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            path = os.path.abspath(path)
            if self.auto_create:
                self.create(path)
            else:
                raise ValueError(f"Provided path '{path}' does not exist.")
        assert self.__is_valid_repo(
            path
        ), f"Provided path '{path}' is not a valid repository."
        self._path = path
        self.uri = path  # Update uri to point to absolute path of repository

    def __is_valid_repo(self, path):
        try:
            git.Repo(path)
            return True
        except git.InvalidGitRepositoryError:
            return False

    @property
    def git(self):
        if not hasattr(self, "_git"):
            self._git = git.Repo(self.path)
        return self._git

    @property
    def git_has_remote(self):
        return hasattr(self.git.remotes, self.config.remote_name)

    @property
    def git_remote(self):
        if self.git_has_remote:
            return self.git.remote(self.config.remote_name)
        return None

    # ----------- Repository actions / state ----------------------------------
    @property
    def revision(self):
        c = self.git.commit()
        return f"{c.committed_date}_{c.hexsha}"

    def update(self, branch=None):
        branch = branch or self.config.published_branch
        if not self.git_has_remote:
            return

        logger.info("Fetching updates to the knowledge repository...")
        try:
            self.git_remote.fetch()
        except git.exc.GitCommandError:
            logger.warning(
                "Cannot fetch from remote repository hosted "
                f"on {self.__remote_host}. Continuing locally "
                "with potentially outdated code."
            )
            return

        current_branch = self.git.active_branch
        self.git.branches[branch].checkout()
        self.git_remote.pull(branch)
        current_branch.checkout()

    def set_active_draft(self, path):  # TODO: deprecate
        branch = self.git_branch_for_post(self._kp_path(path))
        self.config.published_branch = branch.name
        branch.checkout()

    @property
    def status(self):
        return {
            "branch": self.git.active_branch.name,
            "changed_files": [str(diff.a_path) for diff in self.git_diff()],
        }

    @property
    def status_message(self):
        status = self.status
        branch = status["branch"]
        message = f"Currently checked out on the `{branch}` branch."
        if len(status["changed_files"]) > 0:
            modified = "\n\t- ".join(status["changed_files"])
            message += f"Files modified: \n {modified}"
        return message

    # ---------------- Git properties and actions -------------------------
    def git_dir(self, prefix=None, commit=None):
        commit = self.git.commit(commit or self.config.published_branch)
        tree = commit.tree
        if prefix is not None:
            tree = tree[prefix]
        return [
            o.path
            for o in tree.traverse(
                prune=lambda i, d: isinstance(i, git.Submodule)
                or os.path.dirname(i.path).endswith(".kp"),
                visit_once=False,
                predicate=lambda i, d: i.path.endswith(".kp"),
            )
        ]

    def git_read(self, path, commit=None):
        commit = self.git.commit(commit or self.config.published_branch)
        return commit.tree[path].data_stream.read()

    @property
    def git_local_branches(self):
        unmerged_branches = [
            branch.replace("*", "").strip()
            for branch in self.git.git.branch(
                "--no-merged", self.config.published_branch
            ).split("\n")
        ]
        return unmerged_branches

    def __get_path_from_ref(self, ref):
        refs = ref.split("/")
        for i, ref in enumerate(refs):
            if ref.endswith(".kp"):
                break
        if not ref.endswith(".kp"):
            return None
        return "/".join(refs[: i + 1])

    def git_local_posts(self, branches=None, as_dict=False):
        if branches is None:
            branches = self.git_local_branches
        posts = {}
        for branch in branches:
            posts[branch] = set(
                [
                    self.__get_path_from_ref(diff.a_path)
                    for diff in self.git_diff(branch)
                ]
            )
            posts[branch].discard(None)

        if not as_dict:
            out_posts = set()
            for branch, ps in posts.items():
                out_posts.update(ps)
            return list(out_posts)
        return posts

    def git_branch_for_post(self, path, interactive=False):
        if path is None:
            return None
        if path in self.git_local_branches:
            return self.git_branch(path)

        branches = []
        for branch in self.git_local_branches:
            if path in self.git_local_posts(branches=[branch]):
                branches.append(branch)

        if len(branches) == 0:
            if path in self.dir():
                return self.git_branch(self.config.published_branch)
            return None

        if len(branches) == 1:
            return self.git_branch(branches[0])

        # Deal with ambiguity
        if interactive:
            print(f"There are multiple branches for post '{path}'.")
            for i, branch in enumerate(branches):
                print(f"{i}. {branch}")
            response = None
            while not isinstance(response, int):
                response = input("Please select the branch you would like to use: ")
                try:
                    response = int(response)
                except Exception as e:
                    print(f"Exception encountered: {e}")
                    response = None
        else:
            response = 0

        return self.git_branch(branches[response])

    def git_branch(self, branch=None):
        if isinstance(branch, git.Head):
            return branch
        if branch is None:
            return self.git.active_branch

        if not isinstance(branch, str):
            raise ValueError(
                f"'{branch}' of type `{type(branch)}` "
                "is not a valid branch descriptor."
            )

        try:
            return self.git.branches[branch]
        except IndexError:
            raise ValueError(f"Specified branch `{branch}` does not exist.")

    def git_checkout(self, branch, soft=False, reset=False, create=False):
        if not create:
            branch_obj = self.git_branch(branch)
            branch_obj.checkout()
            return branch_obj

        if (
            soft
            and self.git.active_branch.name
            not in [self.config.published_branch, branch]
            and not self.git.active_branch.name.endswith(".kp")
        ):
            response = None
            while response not in ["y", "n"]:
                active_branch = self.git.active_branch.name
                response = input(
                    f"It looks like you have checked out the `{active_branch}`"
                    f" branch, whereas we were expecting to use `{branch}`. Do"
                    " you want to use your current branch instead? (y/n) "
                )
                if response == "y":
                    branch = self.git.active_branch.name

        if reset or branch not in [b.name for b in self.git.branches]:
            ref_head = None
            if self.git_has_remote:
                for ref in self.git_remote.refs:
                    if ref.name == branch:
                        ref_head = ref
                        break
            if not ref_head:
                ref_head = (
                    self.git_remote.refs.master
                    if self.git_has_remote
                    else self.git.branches.master
                )
            else:
                logger.warning(
                    f"The branch `{ref_head.name}` already exists as upstream,"
                    " and you maybe clobbering someone's work. Please check."
                )
            branch = self.git.create_head(branch, ref_head, force=True)
        else:
            branch = self.git_branch(branch)
        branch.checkout()
        return branch

    def git_diff(self, ref=None, ref_base=None, patch=False):
        commit = self.git.commit(ref)
        ref = self.git.merge_base(
            self.git.commit(ref_base or self.config.published_branch), commit
        )[0]
        return commit.diff(ref, create_patch=patch)

    # ---------------- Post retrieval methods --------------------------------

    def _dir(self, prefix, statuses):
        posts = set()

        if any([status != self.PostStatus.PUBLISHED for status in statuses]):
            local_posts = self.git_local_posts(as_dict=True)

        for status in statuses:
            if status == self.PostStatus.PUBLISHED:
                posts.update(
                    self.git_dir(prefix=prefix, commit=self.config.published_branch)
                )
            else:
                for branch in local_posts:
                    for post_path in local_posts[branch]:
                        if prefix is not None and not post_path.startswith(prefix):
                            continue
                        if self._kp_status(post_path, branch=branch) in statuses:
                            posts.add(post_path)
        for post in sorted(posts):
            yield post

    # ------------- Post submission / addition user flow ----------------------
    def _add_prepare(
        self, kp, path, update=False, branch=None, squash=False, message=None
    ):
        target = os.path.abspath(os.path.join(self.path, path))
        if self.git_has_remote:
            branch = branch or path
        else:
            logger.warning(
                "This repository does not have a remote, so post review is "
                "being skipped. Adding post directly into published branch..."
            )
            branch = self.config.published_branch

        # Create or checkout the appropriate branch for this project
        logger.info(f"Checking out (and/or creating) a new branch `{branch}`...")
        branch_obj = self.git_checkout(branch, soft=True, reset=squash, create=True)
        branch = branch_obj.name

        # Verify that post path does not exist (unless we are updating
        # the post)
        assert update or not os.path.exists(target), (
            f"A knowledge post already exists at '{path}'! "
            + "If you wanted to update it, please pass the '--update' flag."
        )

        # Add knowledge post to local branch
        logger.info(f"Adding and committing '{path}' to local branch `{branch}`...")

    def _add_cleanup(
        self, kp, path, update=False, branch=None, squash=False, message=None
    ):
        self.git.index.add([path])

        # Commit the knowledge post and rollback if it fails
        try:
            if message is None:
                message = input("Please enter a commit message for this post: ")
            self.git.index.commit(message)
        except (KeyboardInterrupt, Exception) as e:
            if message is None:
                logger.warning(
                    f"No commit message input for post '{path}'. "
                    "Rolling back post addition..."
                )
            else:
                logger.error("Something went wrong. Rolling back post addition...")
            self.git.index.reset()
            try:
                self.git.git.clean("-df", path)
                self.git.git.checkout("--", path)
            except Exception as e:
                print(f"Exception encountered: {e}")
                pass
            raise e

    def _submit(self, path=None, branch=None, force=False):
        if not self.git_has_remote:
            remote_name = self.config.remote_name
            raise RuntimeError(
                f"Could not find remote repository `{remote_name}` into "
                "which this branch should be submitted."
            )
        if branch is None and path is None:
            raise ValueError(
                "To submit a knowledge post, a path to the post "
                "and/or a git branch must be specified."
            )
        if branch is None:
            branch = self.git_branch_for_post(path)
        if branch is None:
            raise ValueError(
                "It does not appear that you have "
                f"any drafts in progress for '{path}'."
            )

        try:
            self.git_remote.push(branch, force=force)
        except git.exc.GitCommandError as e:
            remote_name = self.config.remote_name
            remote_url = self.git_remote.url
            err = e.stderr.strip()
            raise RuntimeError(
                f"Failed to push to remote repository {remote_name} "
                f"({remote_url}). Please check the following error, "
                f"and then try again:\n\n{err}"
            )

        logger.info(
            f"Pushed local branch `{branch}` to upstream branch "
            f"`{branch}`. Please consider starting a pull request, "
            "or otherwise merging into master."
        )

    def _publish(self, path):  # Publish a post for general perusal
        raise NotImplementedError

    def _unpublish(self, path):  # unpublish a post for general perusal
        raise NotImplementedError

    def _accept(self, path):  # Approve to publish a post for general perusal
        pass

    def _remove(self, path, all=False):
        raise NotImplementedError

    # ------------ Knowledge Post Data Retrieval Methods ----------------------

    def _kp_uuid(self, path):
        try:
            return self._kp_read_ref(path, "UUID")
        except Exception as e:
            print(f"Exception encountered: {e}")
            return None

    def _kp_path(self, path, rel=None):
        return KnowledgeRepository._kp_path(
            self, os.path.expanduser(path), rel=rel or self.path
        )

    def _kp_exists(self, path, revision=None):
        # For speed, first check whether it exists in the
        # checked out branch, then search more deeply
        return os.path.isdir(os.path.join(self.path, path)) or (
            self.git_branch_for_post(path, interactive=False) is not None
        )

    def _kp_status(self, path, revision=None, detailed=False, branch=None):
        if not hasattr(self, "_dir_cache"):
            self._dir_cache = {path: None for path in self.dir()}
        if path in self._dir_cache:
            return self.PostStatus.PUBLISHED
        if branch is None:
            branch = self.git_branch_for_post(path, interactive=False)
        else:
            branch = self.git_branch(branch)

        if branch is None:
            return ValueError(f"No such post: {path}")

        if branch.name == self.config.published_branch:
            status = self.PostStatus.PUBLISHED, None
        elif self.git_has_remote and branch.name in self.git_remote.refs:
            remote_branch = self.git_remote.refs[branch.name].name
            behind = len(list(self.git.iter_commits(f"{branch}..{remote_branch}")))
            ahead = len(list(self.git.iter_commits(f"{remote_branch}..{branch}")))

            status = (
                self.PostStatus.SUBMITTED,
                (f" - {behind} commits behind" if behind else "")
                + (f" - {ahead} commits ahead" if ahead else "")
                + (f" [On branch: {branch}]" if branch != path else ""),
            )
        else:
            status = self.PostStatus.DRAFT, None

        if detailed:
            return status
        return status[0]

    def _kp_get_revision(self, path):
        # We use a 'REVISION' file in the knowledge post folder rather
        # than using git revisions because using git rev-parse is slow.
        try:
            return int(self._kp_read_ref(path, "REVISION"))
        except Exception as e:
            print(f"Exception encountered: {e}")
            return 0

    def _kp_get_revisions(self, path):  # slow
        # TODO: In the future, we may want to use something like:
        #    self.git.iter_commits(paths=os.path.join(
        #                          self.path, path, 'knowledge.md'))
        # But this will require a lot of piping and may not make sense
        # in the context of a non-bare git repository.
        raise NotImplementedError

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        ref_path = os.path.join(self.path, path, reference)
        ref_dir = os.path.dirname(ref_path)
        if not os.path.exists(ref_dir):
            os.makedirs(ref_dir)
        write_binary(ref_path, data)

    # TODO: Account for revision
    def _kp_dir(self, path, parent=None, revision=None):
        if parent:
            path = os.path.join(path, parent)
        for dirpath, dirnames, filenames in os.walk(os.path.join(self.path, path)):
            for filename in filenames:
                if dirpath == "" and filename == "REVISION":
                    continue
                yield os.path.relpath(
                    os.path.join(dirpath, filename), os.path.join(self.path, path)
                )

    # TODO: Account for revision
    def _kp_has_ref(self, path, reference, revision=None):
        return os.path.isfile(os.path.join(self.path, path, reference))

    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    def _kp_new_revision(self, path, uuid=None):
        self._kp_write_ref(path, "REVISION", encode(self._kp_get_revision(path) + 1))
        if uuid:
            self._kp_write_ref(path, "UUID", encode(uuid))

    def _kp_read_ref(self, path, reference, revision=None):
        return read_binary(os.path.join(self.path, path, reference))

    # ------------- Utility methods --------------------------------------
    def __abspath(self, path):
        return os.path.abspath(os.path.join(self.path, path))

    @property
    def __remote_host(self):
        if self.git_has_remote:
            # TODO: support more types of hosts
            m = re.match(r".*?@(.*?):\.*?", self.git_remote.url)
            if m:  # shorthand ssh uri
                return m.group(1)
        return None

    @property
    def __remote_port(self):
        port = 22
        if self.git_has_remote:
            m = re.match(r"^(.*?)?@([^/:]*):?([0-9]+)?", self.git_remote.url)
            if m:
                if m.group(3):
                    port = m.group(3)
        return int(port)
