# The Knowledge Repository (BETA)
[![Build Status](https://travis-ci.org/airbnb/knowledge-repo.svg?branch=master)](https://travis-ci.org/airbnb/knowledge-repo)
[![PyPI version](https://badge.fury.io/py/knowledge-repo.svg)](https://badge.fury.io/py/knowledge-repo)
[![Python](https://img.shields.io/pypi/pyversions/knowledge-repo.svg?maxAge=2592000)](https://pypi.python.org/pypi/knowledge-repo)

The Knowledge Repository project is focused on facilitating the sharing of knowledge between data scientists and other technical roles using data formats and tools that make sense in these professions. It provides various data stores (and utilities to manage them) for "knowledge posts", with a particular focus on notebooks (R Markdown and Jupyter / iPython Notebook) to better promote reproducible research.

Check out this [Medium Post](https://medium.com/airbnb-engineering/scaling-knowledge-at-airbnb-875d73eff091) for the inspiration for the project.

**Note:** The Knowledge Repository is a work in progress. There are lots of code cleanups and feature extensions TBD. Your assistance and involvement is more than encouraged.

![](https://cloud.githubusercontent.com/assets/20175104/18972198/116861be-864d-11e6-9850-5a6cdad7ce54.png)

![](https://cloud.githubusercontent.com/assets/20175104/18972218/264f4c00-864d-11e6-8153-3e9833563784.png)

## Quickstart

1\. Install the knowledge-repo tooling
```
pip install  --upgrade knowledge-repo
```

To install dependencies for iPython notebook, PDF uploading, and local development, use `pip install --upgrade knowledge-repo[all]`

2\. Initialize a knowledge repository - your posts will get added here
```
knowledge_repo --repo ./example_repo init
```
3\. Create a post template

for Rmd:
```
knowledge_repo --repo ./example_repo create Rmd example_post.Rmd
```

for ipynb
```
knowledge_repo --repo ./example_repo create ipynb example_post.ipynb
```
4\. Edit the notebook file `example_post.ipynb` or `example_post.Rmd` as you normally would.


5\. Add your post to the repo with path `project/example`
```
knowledge_repo --repo ./example_repo add example_post.Rmd -p project/example_rmd
knowledge_repo --repo ./example_repo add example_post.ipynb -p project/example_ipynb
```
6\. Preview the added post
```
knowledge_repo --repo ./example_repo preview project/example_rmd
#or
knowledge_repo --repo ./example_repo preview project/example_ipynb
```

### Feedback for Beta

The Knowledge Repo is currently in a public beta, and we are rolling it out to more people to get feedback. In particular, we'd love to hear about the following:

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
 - The Python configuration for git knowledge repositories currently reads directly out of the `master` branch, allowing (depending on your organization's git policy) a malicious user to commit arbitrary code into the master branch, which then gets run on client and server machines during interactions with the git repository using the inbuilt knowledge repository abstractions.

## Introduction

Knowledge posts are a general markdown format that is automatically generated from the following common formats:

 - Jupyter/Ipython notebooks
 - Rmd notebooks
 - Markdown files

The Jupyter, Rmd, and Markdown files are required to have a specific set of yaml style headers which are used to organize and discover research:

```
---
title: I Found that Lemurs Do Funny Dances
authors:
- sally_smarts
- wesley_wisdom
tags:
- knowledge
- example
created_at: 2016-06-29
updated_at: 2016-06-30
tldr: This is short description of the content and findings of the post.
---
```

Users add these notebooks/files to the knowledge repository through the `knowledge_repo` tool, as described below; which allows them to be rendered and curated in the knowledge repository's web app.

If your favourite format is missing, we welcome contributions; and are happy to work with you to get it supported. See the "Contributing" section below to see how to add support for more formats.

Note that the web application can live on top of multiple Knowledge Repo backends. Supported types so far are:

 - Git Repo + Remote Git Hosting Service (Primary Use Case)
 - Web Application SQL db

## Getting started
There are two repositories associated with the Knowledge Repository project.
1. This repository, which will be installed first. This is referred to as the knowledge repository tooling.
2. A knowledge data repository, which is created second. This is where the knowledge posts are stored.

### Installation
To install the knowledge repository tooling (and all its dependencies), simply run:

`pip install --upgrade "knowledge-repo[all]"`

You can also skip installing dependencies which are only required in special cases by replacing `all` with one or more of the following (separated by commas):
- `ipynb` : Installs the dependencies required for adding/converting Jupyter notebook files
- `pdf` : Installs the dependencies required for uploading PDFs using the web editor
- `dev`: Installs the dependencies required for doing development, including running the tests

The `knowledge_repo` script is the one that is used for all of the following actions. It requires the `--repo` flag to be passed to it, with the location of the knowledge data repository.

You can drop the `--repo` option by setting the `$KNOWLEDGE_REPO` environment variable with the location of the  knowledge data repo in your bash/zsh/shell configuration. In bash, this would be done as such:
```
export $KNOWLEDGE_REPO=repo_path
```

### Setup of the knowledge data repositories
There are two different ways to do this, depending on whether your organization already has a knowledge data repository or not:

#### Your organization already has a knowledge data repository setup
If your organization already has a knowledge data repository setup, check it out onto your computer as you normally would; for example:

`git clone git@example.com:example_data_repo.git`

Running this same script if a repo already exists at `<repo_path>` will allow you to update it to be a knowledge data repository. This is useful if you are starting a repository on a remote service like GitHub, as this allows you to clone the remote repository as per normal; run this script; and then push the initialization back into the remote service using `git push`.

#### Your organization does not have knowledge data repository setup
The following command will create a new repository at `<repo_path>`
```
knowledge_repo --repo <repo_path> init
```

If you are hosting this repository on a remote service like Github, and you've created the knowledge data repository using the `init` flag, you must push that to that remote service in order for the later commands to work. On Git, this can be done by creating the remote repository through Git and then running

```
git remote add origin url_of_the_repository
git push -u origin master
```

For more details about the structure of a knowledge repository, see the technical details section below.

### Configuration

There are two types of configuration files, one for knowledge-data git repos that holds posts, and another for the web application.

#### Knowledge Data Git Repo Configuration

When running `knowledge_repo init` to make a folder a knowledge-data git repo, a `.knowledge_repo_config` file will be created in the folder. The file will be a copy of the default repo configuration file located [here](https://github.com/airbnb/knowledge-repo/blob/master/knowledge_repo/config_defaults.py).

This configuration file will allow you to add postprocessors to post contributions from the repo, add rules for which subdirectories posts can be added to, and check the format of author names at contribution time. See the file itself for more detail.

#### Knowledge Web Application Configuration

Specify a configuration file when running the web application by adding the flag `--config path/to/config_file.py`. An example configuration file is provided [here](https://github.com/airbnb/knowledge-repo/blob/master/resources/server_config.py). 

This configuration file lets you specify details specific to the web server. For instance, one can specify the database connection string or the request header that contains usernames. See the file itself for more detail.

## Writing Knowledge Posts

### TLDR Guide For Contributing

If you have already set up your system as described below, here is a snapshot of the commands you need to run to upload your knowledge post stored in ~/Documents/my_post.Rmd. For Jupyter / iPython Notebooks, the commands are the same, replacing all instances of `Rmd` with `ipynb`. It assumes you have configured the KNOWLEDGE_REPO environment variable to point to your local copy of the knowledge repository. The code is written for producing and contributing an ipynb file to make the examples clear, R Markdown files are run by using `Rmd` in place of `ipynb` in each command.

1. `knowledge_repo create Rmd ~/Documents/my_post.Rmd`, which creates a template with required yaml headers. Templates can also be downloaded by clicking "Write a Post!" the web application. *Make sure your post has these headers with correct values for your post*
2. Do your work in the generated my_post.Rmd file. *Make sure the post runs through from start to finish before attempting to add to the Knowledge Repo!*
3. `knowledge_repo add ~/Documents/my_post.Rmd [-p projects/test_project] [--update]`
4. `knowledge_repo preview projects/test_project`
5. `knowledge_repo submit projects/test_project`
6. From your remote git hosting service, request a review for merging the post. (ie. open a pull request on Github)
7. After it has been reviewed, merge it in to the master branch.

### Full Guide for Contributing:

#### Creating knowledge
Once the knowledge data repository has been initialized, it is possible to start adding posts. Each post in the knowledge repository requires a specific header format, used for metadata formatting.
To create a new post using a provided template, which has both the header information and example content, run the following command:
```
knowledge_repo --repo <repo_path> create {ipynb, Rmd, md} filename
```

The first argument indicates the type of the file that you want created, while the second argument indicates where the file should be created.

If the knowledge data repository is created at `knowledge_data_repo`, running
```
knowledge_repo --repo knowledge_data_repo create md ~/Documents/my_first_knowledge_post.md
```
will create a file, `~/Documents/my_first_knowledge_post.md`, the contents of which will be the boilerplate template of the knowledge post.

The help menu for this command (and all following commands) can be reached by adding the `-h` flag, `knowledge_repo --repo <repo_path> create -h`.

Alternatively, by going to the `/create` route in the webapp, you can click the button for whichever template you would like to have,
and that will download the correct template.

#### Adding knowledge
Once you've finished writing a post, the next step is to add it to the knowledge data repository.
To do this, run the following command:
```
knowledge_repo --repo <repo_path> add <file with format {ipynb, Rmd, md}> [-p <location in knowledge repo>]
```

Using the example from above, if we wanted to add the post `~/Documents/my_first_knowledge_post.md` to `knowledge_data_repo`,
we would run:
```
knowledge_repo --repo knowledge_data_repo add ~/Documents/my_first_knowledge_post.md -p projects/test_knowledge
```

The `-p` flag specifies the location of the post in the knowledge data repository - in this case, `knowledge_data_repo/projects/test_knowledge`.
The `-p` flag does not need to be specified if `path` is included in the header of the knowledge post.

#### Updating knowledge
To update an existing knowledge post, pass the `--update` flag to the `add` command. This will allow the add operation to override exiting knowledge posts.
```
knowledge_repo --repo <repo_path> add --update <file with format {ipynb, Rmd, md}> <location in knowledge repo>
```

#### Previewing Knowledge
If you would like to see how the post would render on the web app before submitting the post for review, run the following command:
```
knowledge_repo --repo <repo_path> preview <path of knowledge post to preview>
```

In the case from above, we would run:
```
knowledge_repo --repo knowledge_data_repo preview projects/test_knowledge
```

There are other arguments that can be passed to this command, adding the `-h` flag shows them all along with further information about them.

#### Submitting knowledge
After running the add command, two things should have happened:
1. A new folder should have been created at the path specified in the add command, which ends in `.kp`. This is added automatically to indicate that the folder is a knowledge post.
2. This folder will have been committed to the repository on the branch named `<repo_path>/path_in_add_command`

Running the example command: `knowledge_repo --repo knowledge_data_repo add ~/Documents/my_first_knowledge_post.md -p projects/test_knowledge`, we would have seen:
1. A new folder: `knowledge_data_repo/projects/test_knowledge.kp` which was committed on
2. A branch (that you are now on), called `knowledge_data_repo/projects/test_knowledge`

To submit this post for review, simply run the command:
```
knowledge_repo --repo <repo_path> submit <the path of the knowledge post>
```

In this case, we would run:
```
knowledge_repo --repo knowledge_data_repo submit knowledge_data_repo/projects/test_knowledge.kp
```

### Handling Images

The knowledge repo's default behavior is to add the markdown's contents as is to your knowledge post git repository. If you do not have git LFS set up, it may be in your interest to have these images hosted on some type of cloud storage, so that pulling the repo locally isn't cumbersome.

To add support for pushing images to cloud storage, we provide a [postprocessor](https://github.com/airbnb/knowledge-repo/blob/master/resources/extract_images_to_s3.py). This file needs one line to be configured for your organization's cloud storage. Once configured, the postprocessor's registry key can be added to the knowledge git repository's configuration file as a postprocessor.

## Running the web app

Running the web app allows you to locally view all the knowledge posts in the repository, or to serve it for others to view. It is also useful when developing on the web app.

### Running the development server

Running the web app in development/local/private mode is as simple as running:

`knowledge_repo --repo <repo_path> runserver`

Supported options are `--port` and `--dburi` which respectively change the local port on which the server is running, and the sqlalchemy uri where the database can be found and/or initiated. The default port is 7000, and the default dburi is `sqlite:////tmp/knowledge.db`. If the database does not exist, it is created (if that is possible) and initialised. Database migrations are automatic (unless disabled to prevent accidental data loss), but can be performed manually using:

`knowledge_repo --repo <repo_path> db_upgrade --dburi <db>`

### Running the Web App on Multiple Repos

The web application can be run on top of multiple knowledge repo backends. To do this, include each repo with a name and path, prefixed by --repo. For example:

`knowledge_repo --repo {git}/path/to/git/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable runserver`

If including a dbrepo, add the name of the dbrepo to the `WEB_EDITOR_PREFIXES` in the server config, and add it as config when running the app:

`knowledge_repo --repo {git}/path/to/git/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable runserver --config resources/server_config.py`

Note that this is required for the web application's internal post writing UI.

### Deploying the web app

Deploying the web app is much like running the development server, except that the web app is deployed on top of gunicorn. It also allows for enabling server-side components such as sending emails to subscribed users.

Deploying is as simple as:
`knowledge_repo --repo <repo_path> deploy`

or if using multiple repos:
`knowledge_repo --repo {git}/path/to/git/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable deploy --config resources/server_config.py`

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
