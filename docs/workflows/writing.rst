Writing
=======

TLDR Reference
--------------

If you have successfully contributed to a knowledge repository before, this
section is probably for you. It provides a quick reference for the commands
associated with each step of a knowledge post submission for the most common
scenario (i.e. where the repository is backed by a Git repository). If you want
more detail, you can find it in the sections below.

In this quick reference, Jupyter / IPython notebooks are used as an example.
Other file types, such R Markdown work identically, simply substituting 'ipynb'
for 'Rmd', etc. It is also assumed that you have configured the KNOWLEDGE_REPO
environment variable to point to a locally accessible uri for the knowledge
repository.

1. `knowledge_repo create ipynb ~/Documents/my_post.ipynb`: creates a template with required yaml headers. Templates can also be downloaded by clicking "Write a Post!" the web application. *Make sure your post has these headers with correct values for your post*
2. Do your work in the generated my_post.Rmd file. *Make sure the post runs through from start to finish before attempting to add to the Knowledge Repo!*
3. `knowledge_repo add ~/Documents/my_post.Rmd [-p projects/test_project] [--update]`
4. `knowledge_repo preview projects/test_project`
5. `knowledge_repo submit projects/test_project`
6. From your remote git hosting service, request a review for merging the post. (ie. open a pull request on Github)
7. After it has been reviewed, merge it in to the master branch.

Full Guide
----------

Creating
^^^^^^^^

Once the knowledge data repository has been initialized, it is possible to start
adding posts. Each post in the knowledge repository requires a specific header
format, used for metadata formatting. To create a new post using a provided
template, which has both the header information and example content, run the
following command:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> create {ipynb, Rmd, md} filename

The first argument indicates the type of the file that you want created, while
the second argument indicates where the file should be created.

If the knowledge data repository is created at `knowledge_data_repo`, running

.. code-block:: shell

  $ knowledge_repo --repo knowledge_data_repo create md ~/Documents/my_first_knowledge_post.md

will create a file, `~/Documents/my_first_knowledge_post.md`, the contents of
which will be the boilerplate template of the knowledge post.

The help menu for this command (and all following commands) can be reached by
adding the `-h` flag, `knowledge_repo --repo <repo_path> create -h`.

Alternatively, by going to the `/create` route in the webapp, you can click the
button for whichever template you would like to have, and that will download the
correct template.

It is also possible to manually add headers to an existing document (if using
Jupyter Notebooks, add these headers to a "raw" cell at the top of your
notebook). An valid example header looks something like:

.. code-block:: yaml

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

For a complete set of valid headers, refer to the header reference table
below.

Adding
^^^^^^

Once you've finished writing a post, the next step is to add it to the knowledge
data repository. To do this, run the following command:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> add <file with format {ipynb, Rmd, md}> [-p <location in knowledge repo>]


Using the example from above, if we wanted to add the post
`~/Documents/my_first_knowledge_post.md` to `knowledge_data_repo`, we would run:

.. code-block:: shell

  $ knowledge_repo --repo knowledge_data_repo add ~/Documents/my_first_knowledge_post.md -p projects/test_knowledge


The `-p` flag specifies the location of the post in the knowledge data
repository - in this case, `knowledge_data_repo/projects/test_knowledge`. The
`-p` flag does not need to be specified if `path` is included in the header of
the knowledge post.

Updating
^^^^^^^^

To update an existing knowledge post, pass the `--update` flag to the `add`
command. This will allow the add operation to override exiting knowledge posts.

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> add --update <file with format {ipynb, Rmd, md}> <location in knowledge repo>

Previewing
^^^^^^^^^^

If you would like to see how the post would render on the web app before
submitting the post for review, run the following command:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> preview <path of knowledge post to preview>


In the case from above, we would run:

.. code-block:: shell

  $ knowledge_repo --repo knowledge_data_repo preview projects/test_knowledge

There are other arguments that can be passed to this command, adding the `-h`
flag shows them all along with further information about them.

Submitting
^^^^^^^^^^
After running the add command, two things should have happened:
1. A new folder should have been created at the path specified in the add command, which ends in `.kp`. This is added automatically to indicate that the folder is a knowledge post.
2. This folder will have been committed to the repository on the branch named `<repo_path>/path_in_add_command`

Running the example command: :code:`knowledge_repo --repo knowledge_data_repo add ~/Documents/my_first_knowledge_post.md -p projects/test_knowledge`, we would
have seen:

1. A new folder: `knowledge_data_repo/projects/test_knowledge.kp` which was committed on
2. A branch (that you are now on), called `knowledge_data_repo/projects/test_knowledge`

To submit this post for review, simply run the command:

.. code-block:: shell

  $ knowledge_repo --repo <repo_path> submit <the path of the knowledge post>

In this case, we would run:

.. code-block:: shell

  $ knowledge_repo --repo knowledge_data_repo submit knowledge_data_repo/projects/test_knowledge.kp

Post Headers Reference
^^^^^^^^^^^^^^^^^^^^^^

The complete list of supported headers, their purpose and an example is provided below.

==============  =========  ==================================================================================  ===========================================================================================
    header      required                                       purpose                                                                      example
==============  =========  ==================================================================================  ===========================================================================================
title           required   String at top of post                                                               title: This post proves that 2+2=4                                                               |
authors         required   User entity that wrote the post in organization specified format                    authors: <br> - kanye_west<br> - beyonce_knowles                                          |
tags            required   Topics, projects, or any other uniting principle across posts                       tags: <br> - hiphop<br> - yeezy                                                           |
created_at      required   Date when post was written                                                          created_at: 2016-04-03                                                                    |
updated_at      optional   Date when post was last updated                                                     created_at: 2016-10-10                                                                    |
tldr            required   Summary of post takeaways that will be visible in /feed                             tldr: I'ma let you finish, but Beyonce had one of the best videos of all time!            |
path            optional   Instead of specifying post path in the CLI, specify with this post header           path: projects/path/to/post/on/repo                                                       |
thumbnail       optional   Specify which image is shown in /feed                                               thumbnail: 3 OR thumbnail: http://cdn.pcwallart.com/images/giraffe-tongue-wallpaper-1.jpg |
private         optional   If included, post is only visible to authors and editors set in repo configuration  private: true                                                                             |
allowed_groups  optional   If the post is private, specify additional users or groups who can see the post     allowed_groups: ['jay_z', 'taylor_swift', 'rap_community']                                |
==============  =========  ==================================================================================  ===========================================================================================
