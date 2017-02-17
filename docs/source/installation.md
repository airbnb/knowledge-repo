.. _test:

# Installation and Configuration

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
export KNOWLEDGE_REPO=repo_path
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

This configuration file will allow you to:

 - Add postprocessors to post contributions from the repo. (see the `postprocessors` array of functions)
 - Add rules for which subdirectories posts can be added to. (see the `path_parse()` function)
 - Check and manage the format of author names at contribution time
    - Add logic to `username_parse()` to check post author names and raise exceptions when they don't match
    - Add logic to `username_to_name()` to manage how user/author names are displayed, ex. "sally_smarts" --> "Sally Smarts"
    - Add logic to `username_to_email()` to manage how user/author names are matched to emails, ex. "sally_smarts" --> "sally.smarts@mycompany.com"

See the file itself for more detail.

#### Knowledge Web Application Configuration

Specify a configuration file when running the web application by adding the flag `--config path/to/config_file.py`. An example configuration file is provided [here](https://github.com/airbnb/knowledge-repo/blob/master/resources/server_config.py).

This configuration file lets you specify details specific to the web server. For instance, one can specify the database connection string or the request header that contains usernames. See the file itself for more detail.
