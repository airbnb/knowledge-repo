Installation
============

To install the knowledge repository tooling (and all its dependencies), simply
run:

.. code-block:: shell

  $ pip install --upgrade "knowledge-repo[all]"

You can also skip installing dependencies which are only required in special
cases by replacing `all` with one or more of the following (separated by
commas):
- `ipynb` : Installs the dependencies required for adding/converting
Jupyter notebook files
- `pdf` : Installs the dependencies required for uploading PDFs using the web
editor
- `dev`: Installs the dependencies required for doing development, including
running the tests

In addition to the `knowledge_repo` Python library, this also installs a
`knowledge_repo` script that is used to interact with the Knowledge Repository
on the command line. You can verify that everything is set up appropriately by
running:

.. code-block:: shell

  $ knowledge_repo --version

This should should run and show the current version of the Knowledge Repo. It
may then throw an exception due to a Knowledge Repository not being specified,
but this is expected. If your shell environment cannot find the `knowledge_repo`
executable, you may need to check your `$PATH` and ensure that your Python's
executable "bin" folder is on it.

If you are a user expecting to interact with an existing Knowledge Repo, please
refer to :doc:`quickstart`. Otherwise, if you are looking to create a new
Knowledge Repo installation, please refer to :doc:`deployment`.
