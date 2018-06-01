Deployment
==========

Deploying the Knowledge Repo in an organization is done in two steps.

 1. A knowledge repository (or repositories) must be created. These
    repositories are where knowledge posts are pooled and made accessible to
    users.
 2. Deploy the Knowledge Repo web application on top of this repository (or
    repositories), which then acts as the primary gateway for users to access
    the stored knowledge posts.

Creating Knowledge Repositories
-------------------------------

The Knowledge Repo project supports multiple repository backends, all offering
the same programmatic API (and being subclasses of `KnowledgeRepository`). At
this stage, two backends have been fully implemented:
- `GitKnowledgeRepository`: A repository backed by a local git repository
(optionally synced with remote git repository).
- `DbKnowledgeRepository`: A repository backed by a database backend (most
databases supported by SQLAlchemy can be used).

All backends also allow configuration using a YAML configuration file at
'/.knowledge_repo_config.yml' within the repository. A template for creating
this file is available `here <repo_config_>`__, if one does not already exist or
the repository configuration has grown out of sync with upstream changes.

.. _`repo_config`: https://github.com/airbnb/knowledge-repo/blob/master/knowledge_repo/templates/repository_config.yml

Git Knowledge Repositories
^^^^^^^^^^^^^^^^^^^^^^^^^^

The following command will create a new repository at `<repo_path>`:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> init

The result is a git repository at `<repo_path>` with a `.knowledge_repo_config`
copied from the defaults found `in the repository source code <repo_config_>`__.
If a git repository was already found at `<repo_path>` it will upgrade it to be
a knowledge data repository. This is useful if you are starting a repository on
a remote service like GitHub, as this allows you to clone the remote repository
as per normal; run this script; and then push the initialization back into the
remote service using `git push`. Otherwise, if you plan to host this repository
on a remote service like GitHub, you must push this repository to that remote
service. This can be done by creating the remote repository through GitHub (or
whichever service you plan to use) and then running:

.. code-block:: shell

  $ git remote add origin <url_of_remote_repository>
  $ git push -u origin master

Users can then clone this repository, and point their local `knowledge_repo`
script at it using :code:`--repo <path_of_cloned_repository>`.

Database Knowledge Repositories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Database knowledge repositories are the only backends that currently allow
end-to-end publishing of knowledge posts via the web app interface. They are
created on demand, where possible. Simply point the `knowledge_repo` script at
it using something akin to
:code:`--repo mysql://username:password@hostname/database:table_name`. If the
table does not exist it will be created if the active user has the appropriate
permissions.

**Note**: Database Knowledge repositories also support having a `.knowledge_repo_config`
configuration, but one is not automatically added.

Repository Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

As noted earlier, all knowledge repository backends support configuration via
a Python file that is imported from the repository. This configuration can
override the defaults in the default repository configuration found
`here <repo_config_>`__.

This configuration file will allow you to:

 - Add postprocessors to post contributions from the repo. (see the `postprocessors` array of functions)
 - Add rules for which subdirectories posts can be added to. (see the `path_parse()` function)
 - Check and manage the format of author names at contribution time
    - Add logic to `username_parse()` to check post author names and raise exceptions when they don't match
    - Add logic to `username_to_name()` to manage how user/author names are displayed, ex. "sally_smarts" --> "Sally Smarts"
    - Add logic to `username_to_email()` to manage how user/author names are matched to emails, ex. "sally_smarts" --> "sally.smarts@mycompany.com"

Please refer to the default configuration file itself for further documentation.

.. note::

  Image handling is a good example of where post-processor configuration can be
  very useful. Knowledge repositories' default behavior is to add the markdown's
  contents as is to your knowledge post git repository, including images. If you
  do not have git LFS set up, it may be in your interest to have these images
  hosted on some type of cloud storage, so that cloning the git repository
  locally is less cumbersome.

  We provide an `example postprocessor <extract_images_postprocessor_>`__ that
  adds support for pushing images to cloud storage. To use it, simply import
  or paste it into your `.knowledge_repo_config` file, and add it by name to
  your `postprocessors` configuration key.

.. _`extract_images_postprocessor`: https://github.com/airbnb/knowledge-repo/blob/master/knowledge_repo/postprocessors/extract_images_to_s3.py

Deploying the Web Application
-----------------------------

Any user with access to knowledge repositories can create an instance of the
Knowledge Repo Web Application that acts as a portal to them. This is achieved
by running:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> runserver

which starts a web application instance on `http://127.0.0.1:7000` with the
default (insecure) options. The command line also supports some high-level
options, such as `--port` and `--dburi` which respectively change the local
port on which the server is running, and the sqlalchemy uri where the database
can be found and/or initiated.

For shared deployments, however, you will probably need to create a server
configuration file. A complete server configuration template can be found
`here <server_template_>`__. The configuration file gives you fine-grained
control over the deployment, including authentication, access policies, indexing
behavior.

.. _`server_template`: https://github.com/airbnb/knowledge-repo/blob/master/knowledge_repo/app/config_defaults.py

Once a configuration file has been created according to the documentation
provided in the template, deploying the web application is as simple as:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> deploy --config <config_file>

Supported options are `--port`, `--dburi`,`--workers`, `--timeout` and
`--config`. The `--config` option allows you to specify a python config file
from which to load the extended configuration. A template config file is
provided in `knowledge_repo/app/config_defaults.py`. The `--port` and `--dburi`
options are as before, with the `--workers` and `--timeout` options specifying
the number of threads to use when serving through gunicorn, and the timeout
after which the threads are presumed to have died, and will be restarted.

Database Migrations
^^^^^^^^^^^^^^^^^^^

No matter which knowledge repository backends are used, the web application
itself requires a database backend in order to store its cache of the post
index and user permissions. The database to be used can be specified via the
CLI using the :code:`--dburi` option or via the config file passed in using
:code:`--config`. Most datatabase backends supported by SQLAlchemy should work.
Database URIs will look something like:
:code:`mysql://username:password@hostname/database:table_name`.

If the database does not exist, it is created (if that is possible) and
initialised. When updates to the Knowledge Repo require changes to the database
structure, migrations are automatically performed (unless disabled in the config
to prevent accidental data loss). They can also be performed manually using:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> db_upgrade --dburi <db>

Multiple Repositories
^^^^^^^^^^^^^^^^^^^^^

Multiple repositories can be stitched together into a single knowledge
repository and served via a single web application instance. This is achieved
using a `MetaKnowledgeRepository` instance, which creates a virtual filesystem
into which the knowledge repositories are "mounted".

For example, you can mount a git repostory at `/` and a database repository
at `/webposts` using:

.. code-block:: shell

  $ knowledge_repo --repo {}/path/to/git/repo --repo {webposts}<db_uri>:<table> ...

Web Editor
^^^^^^^^^^

The web editor allows the entire post creation and publication process to be
done through the web application. To enable the web editor, simply add the
path(s) under which web edited posts are allowed to be created to the
`WEB_EDITOR_PREFIXES` option in the server configuration. Note that these
paths **must** be backed by a database repository.
