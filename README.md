# The Knowledge Repository

**Note:** The Knowledge Repository is a work in progress. There are lots of code cleanups and feature extensions TBD. Your assistance and involvement is more than encouraged.

## Beta Release Information

### Feedback for Beta

The Knowledge Repo is currently in a private beta, and we are rolling it out to more people to get feedback. In particular, we'd love to hear about the following:

 - How easy is it to set up the git knowledge post repository?
 - How easy is it to set up the web application, and make it live internally within your organization?
 - Where are the gaps in our documentation that we should fill in to assist others in understanding the system?
 - At a higher level, are there any blockers or barriers to setting up the Knowledge Repo in your organization?

### Known Issues

Here's a running list of known issues we are working on:

 - The in-app webeditor needs refactoring to:
    - Rely completely on KnowledgePost objects instead of interacting with db records
    - Trigger "save" actions when necessary
    - Allow for image uploading
    - Only reveal the "Write a Post!" button if webeditor is properly configured (non-empty `WEB_EDITOR_PREFIXES` in server_config.py, dbrepo specified on webapp runtime call)
 - The Python configuration for git knowledge repositories currently reads directly out of the `master` branch, allowing (depending on your organization's git policy) a malicious user to commit arbitrary code into the master branch, which then gets run on client and server machines during interactions with the git repository using the inbuilt knowledge repository abstractions.

## Introduction

The Knowledge Repository project is focussed on facilitating the sharing of knowledge between data scientists and other technical roles using data formats and tools that make sense in these professions. It provides various data stores (and utilities to manage them) for "knowledge posts", which are a general markdown format that is automatically generated from the following common formats:

 - Jupyter/Ipython notebooks
 - Rmd notebooks
 - Markdown files

Users add these notebooks/files to the knowledge repository through the `knowledge_repo` tool, as described below; which allows them to be rendered and curated in the knowledge repository's web app.

If your favourite format is missing, we welcome contributions; and are happy to work with you to get it supported. See the "Contributing" section below to see how to add support for more formats.


Note that the web application can live on top of multiple Knowledge Repo backends. Supported types so far are:

 - Github Repo
 - Web Application SQL db

## Getting started

### Installation
To install the knowledge repository tooling, simply run:

`pip install git+ssh://git@github.com/airbnb/knowledge-repo.git`

### Setup
If your organization already has a knowledge data repository setup, check it out onto your computer as you normally would; for example:

`git clone git@example.com:example_data_repo.git`

If not, or for fun, you can create a new knowledge repository using:

`knowledge_repo --repo <repo_path> init`

Running this same script if a repo already exists at `<repo_path>` will have no effect.

You can drop the `--repo` option if you set the `$KNOWLEDGE_REPO` environment variable to the location of that repository.

For more details about the structure of a knowledge repository, see the technical details section below.

### Adding knowledge

The whole point of a knowledge repository is to host knowledge posts. You can add a knowledge post using:

`knowledge_repo --repo <repo_path> add <supported knowledge format> [-p <location in knowledge repo>]`

Specifying the target location is not necessary if 'path' is in the knowledge post's headers. For example, if my knowledge repository is in a folder named `test_repo`, and I have an IPython notebook at `Documents/notebook.ipynb`, and I want it to be added to the knowledge repository under `projects/test_knowledge`, I can run:

`knowledge_repo --repo test_repo add Documents/notebook.ipynb -p projects/test_knowledge`

If you look in `test_repo` you will see a new folder `test_repo/projects/test_knowledge.kp`, which is checked into the repository on a branch named `test_repo/projects/test_knowledge.kp`. To submit it for review, simply run `knowledge_repo --repo ... submit <path>`.

Note that the folder ends in '.kp'. This is added automatically to indicate that this folder is a knowledge post. Explicitly adding the '.kp' is optional.

To update an existing knowledge post, simply pass the `--update` option, which will allow the add operation to override existing knowledge posts. e.g.

`knowledge_repo --repo <repo_path> add --update <supported knowledge format> <location in knowledge repo>`

### Running the web app

Running the web app allows you to locally view all the knowledge posts in the repository, or to serve it for others to view. It is also useful when developing on the web app.

#### Running the development server

Running the web app in development/local/private mode is as simple as running:

`knowledge_repo --repo <repo_path> runserver`

Supported options are `--port` and `--dburi` which respectively change the local port on which the server is running, and the sqlalchemy uri where the database can be found and/or initiated. The default port is 7000, and the default dburi is `sqlite:////tmp/knowledge.db`. If the database does not exist, it is created (if that is possible) and initialised. Database migrations are automatic (unless disabled to prevent accidental data loss), but can be performed manually using:

`knowledge_repo --repo <repo_path> db_upgrade --dburi <db>`

#### Running the Web App on Multiple Repos

The web application can be run on top of multiple knowledge repo backends. To do this, include each repo with a name and path, prefixed by --repo. For example:

`knowledge_repo --repo {git}/path/to/github/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable runserver`

If including a dbrepo, add the name of the dbrepo to the `WEB_EDITOR_PREFIXES` in the server config, and add it as config when running the app:

`knowledge_repo --repo {git}/path/to/github/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable runserver --config resources/server_config.py`

Note that this is required for the webeditor, the "Write a Post!" section of the application.

#### Deploying the web app

Deploying the web app is much like running the development server, except that the web app is deployed on top of gunicorn. It also allows for enabling server-side components such as sending emails to subscribed users.

Deploying is as simple as:
`knowledge_repo --repo <repo_path> deploy`

or if using multiple repos:
`knowledge_repo --repo {git}/path/to/github/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable deploy --config resources/server_config.py`

Supported options are `--port`, `--dburi`,`--workers`, `--timeout` and `--config`. The `--config` option allows you to specify a python config file from which to load the extended configuration. A template config file is provided in `resources/server_config.py`. The `--port` and `--dburi` options are as before, with the `--workers` and `--timeout` options specifying the number of threads to use when serving through gunicorn, and the timeout after which the threads are presumed to have died, and will be restarted.

## Contributing

We would love to work with you to create the best knowledge repository software possible. If you have ideas or would like to have your own code included, add an issue or pull request and we will review it.

### Adding new filetype support

Support for conversion of a particular filetype to a knowledge post is added by writing a new `KnowledgePostConverter` object. Each converter should live in its own file in `knowledge_repo/converters`. Refer to the implementation for ipynb, Rmd, and md for more details. If your conversion is site-specific, you can define these subclasses in `.knowledge_repo_config`, whereupon they will be picked up by the conversion code.

### Adding extra structure and/or verifications to the knowledge post conversion process

When a KnowledgePost is constructed by converting from support filetypes, the resulting post is then passed through a series of postprocessors (defined in `knowledge_repo/postprocessors`). This allows one to modify the knowledge post, upload images to remote storage facilities (such as S3), and/or verify some additional structure of the knowledge posts. As above, defining or importing these classes in `.knowledge_repo_config.py` allows for postprocessors to be used locally.

### More

Is the Knowledge Repository missing something else that you would like to see? Let us know, and we'll see if we cannot help you.

## Technical Details

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
