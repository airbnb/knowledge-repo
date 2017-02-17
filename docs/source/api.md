

## Using the API

### What is a Knowledge Repository

A knowledge repository is a virtual filesystem (such as a git repository or database). A GitKnowledgeRepository, for example, has the following structure:

	<repo>
	    + .git  # The git repository metadata
	    + .resources  # A folder into which the knowledge_repo repository is checked out (as a git submodule)
	    - .knowledge_repo_config.py  # Local configuration for this knowledge repository
	    - <knowledge posts>

The use of a git submodule to checkout the knowledge_repo into `.resources` allows use to ensure that the client and server are using the same version of the code. When one uses the `knowledge_repo` script, it actually passes the options to the version of the `knowledge_repo` script in `.resources/scripts/knowledge_repo`. Thus, updating the version of knowledge_repo used by client and server alike is as simple as changing which revision is checked out by git submodule in the usual way. That is:

	pushd .resources
	git pull
	git checkout <revision>/<branch>
	popd
	git commit -a -m 'Updated version of the knowledge_repo'
	git push

Then, all users and servers associated with this repository will be updated to the new version. This prevents version mismatches between client and server, and all users of the repository.

In development, it is often useful to disable this chaining. To use the local code instead of the code in the checked out knowledge repository, pass the `--dev` option as:

`knowledge_repo --repo <repo_path> --dev <action> ...`

### What is a Knowledge Post?

A knowledge post is a directory, with the following structure:

	<knowledge_post>
		- knowledge.md
		+ images/* [Optional]
		+ orig_src/* [Optional; stores the original converted file]

Images are automatically extracted from the local paths on your computer, and placed into images. `orig_src` contains the file(s) from which the knowledge post was converted from.
