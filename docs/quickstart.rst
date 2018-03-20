Quickstart
==========

This section is targetted toward users who are setting their computers up to
work with an existing Knowledge Repo installation, and guides a user through
their first knowledge post submission. If you are looking to create a new
Knowledge Repo repository or server, please refer instead to :doc:`deployment`.

Submitting your first Knowledge Post
------------------------------------

There are several ways to create a Knowledge Post, of which what follows is just
one way. For more workflows, refer to: :doc:`workflows/writing`.

.. topic:: Step 1: Install the knowledge_repo tooling

  If you have not already done so, follow the installation instructions:
  :doc:`installation`.

.. topic:: Step 2: Clone the knowledge repository locally [Git repositories only]

  If the repository with which you are going to be contributing is a git
  repository, clone it locally onto your machine. **Note:** if you have direct
  access to a database knowledge repository, this step is not required.

  .. code-block:: shell

    $ git clone <git url> <local path>

  **Note:** If you are just testing the workflow, you can create a test git repository
  using:

  .. code-block:: shell

    $ knowledge_repo --repo ./test_repo init

  .. note::

    If you will be primarily using a single knowledge repository, it is possible
    to avoid passing it to the `knowledge_repo` command every time by setting
    the :code:`KNOWLEDGE_REPO` environment variable. For example:

    .. code-block:: shell

      export KNOWLEDGE_REPO=<repository uri/path>

    For this to be persistent accross sessions, add it to your shell
    initialization script. If :code:`KNOWLEDGE_REPO` is set, and points to the
    knowledge repository with which you would like to interact, you can drop
    the :code:`--repo` options in the following.

.. topic:: Step 3: Create a Knowledge Post template

  Knowledge Post templates are sample files in their original format which you
  can use to avoid having to remember how metadata is stored and/or added to
  the underlying post documents.

  For a Jupyter notebook template:

  .. code-block:: shell

    $ knowledge_repo --repo <path/uri_of_repo> create ipynb example_post.ipynb

  For an R Markdown template:

  .. code-block:: shell

    $ knowledge_repo --repo <path/uri_of_repo> create Rmd example_post.Rmd

  Other templates may be available. You can see all available templates
  `here <templates_>`__.

.. _`templates`: https://github.com/airbnb/knowledge-repo/tree/master/knowledge_repo/templates

.. topic:: Step 4: Edit the template as normal

  Create whatever code cells / plots / LaTeX / etc that you normally would in your
  work.

.. topic:: Step 5: Add your post to the knowledge repository

  .. code-block:: shell

    $ knowledge_repo --repo <path/uri_of_repo> add example_post.ipynb -p project/example_ipynb
    $ knowledge_repo --repo <path/uri_of_repo> add example_post.Rmd -p project/example_rmd

  Note that the `-p` option specifies the path in the repository to which the post
  should be added.

.. topic:: Step 6: Preview the added post

  Sometimes formatting may differ in the Knowledge Web Application compared to
  that shown in your native environment. Checking that the rendering is what you
  expect is a good idea before submitting it for peer review.

  .. code-block:: shell

    $ knowledge_repo --repo <path/uri_of_repo> preview <post_path_in_repository>

.. topic:: Step 7: Submit post for review

  If everything looks good when previewed, the final step of post submission is
  submitting your local posts upstream for review, and ultimately, publishing.

  .. code-block:: shell

    $ knowledge_repo --repo <path/uri_of_repo> submit <post_path_in_repository>
