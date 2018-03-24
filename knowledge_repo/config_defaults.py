# Default configuration for knowledge repositories

import re


# A function called to see whether a specified path is permitted in the repository
# Only enforced when creating/modifying posts. It should return the path as a standard
# unix path (virtual folders separated by '/' and the final node should end in '.kp').
# It should raise an exception if the provided path is is not permitted in the knowledge
# repository. A default implementation is provided using `path_patterns`, which
# can be provided more readily in a YAML configuration file.
def path_parse(repo, path):
    if not path.endswith('.kp'):
        path += '.kp'
    for pattern in repo.config.path_patterns:
        if re.match(pattern, path):
            return path
    raise ValueError(
        "Provided path '{path}' does not match any of the following patterns:\n" +
        '\n'.join("'{}': {}".format(pattern, desc) for pattern, desc in repo.config.path_patterns.items())
    )


# The accepted path patterns should be provided as a dictionary mapping regex
# patterns to descriptions of that pattern.
path_patterns = {
    '.*': "Any path is valid."
}


# A dictionary of aliases which point to knowledge posts. This allows you to alias posts
# which may be useful to forward old links to new locations, or to give certain posts
# precedence. It also allows the post path to violate the normal naming rules of posts.
# The only condition is that they cannot mask an existing post url, in which case the
# alias is silently ignored.
aliases = {}


# Postprocessors to apply when importing KnowledgePost objects into the repository.
# Note that KnowledgePost objects by default run 'extract_images' and 'format_checks'.
# Order is important. Should be a list of tuples, of form:
# ('name of postprocessor', {'init_kwarg': 'value'})
postprocessors = {}


# Usernames of users to keep informed of changes to the knowledge data repo
editors = []


# Function to check whether provided username is a valid username, and if not, mutate it
# such that it is. Should raise an exception if that is not possible, and otherwise
# return the parsed username. A default implementation is provided using
# `username_pattern`, which can be provided more readily in a YAML configuration
# file.
def username_parse(repo, username):
    if not re.match(repo.config.username_pattern, username):
        raise ValueError(
            "Username '{}' does not follow the required pattern: '{}'"
            .format(repo.config.username_pattern)
        )
    return username


# A regex pattern to which valid usernames must adhere
username_pattern = '.*'


# Function to convert a username to a person's proper name.  A default
# implementation is provided using `username_to_name_pattern`, which can be
# provided more readily in a YAML configuration file.
def username_to_name(repo, username):
    m = re.match(repo.config.username_to_name_pattern[0], username)
    return repo.config.username_to_name_pattern[1].format(**m.groupdict())


# A tuple/list of strings, the first being a regex with named groups, and the
# second being a format string with the group names available.
username_to_name_pattern = ('(?P<username>.*)', '{username}')


# Function to convert a username to a person's email. A default implementation
# is provided using `username_to_email_pattern`, which can be provided more
# readily in a YAML configuration file.
def username_to_email(repo, username):
    m = re.match(repo.config.username_to_email_pattern[0], username)
    return repo.config.username_to_email_pattern[1].format(**m.groupdict())


# A tuple/list of strings, the first being a regex with named groups, and the
# second being a format string with the group names available.
username_to_email_pattern = ('(?P<username>.*)', '{username}@example.com')


# Function to generate the web uri for a knowledge post at path `path`. If
# `None`, should return the web uri for the entire repository. Return `None` if
# a web uri does not exist. A default implementation is provided using
# `web_uri_base`, which can be provided more readily in a YAML configuration
# file.
def web_uri(repo, path=None):
    if repo.config.web_uri_base:
        if path:
            return '/'.join([repo.config.web_uri_base, 'post', path])
        return repo.config.web_uri_base
    return None


# The base url of the server hosting this repository.
web_uri_base = None


# If administrators of this knowledge repository want to suggest a specific
# knowledge_repo version requirement when interacting with the repository using
# the `knowledge_repo` script, they may do so here. Users can always work around
# this restriction by using the `--dev` flag to the `knowledge_repo` script. If
# the value supplied is a string starting with '!', it is taken to refer to a
# git tag or commit hash on the upstream Knowledge Repo repository, and the
# `knowledge_repo` script will clone the required  Knowledge Repo version and
# chain commands to it. Otherwise, it is interpreted as a pip-like version
# description (e.g. '==x.y.z', '>0.1.2<=0.8.0', etc), and the currently running
# version of the `knowledge_repo` library is checked at runtime.
required_tooling_version = None


# WARNING: ADVANCED!
# Function that is called on a Flask web app instance before it is launched
# This is useful if you need to add a route for your local deployment, or other
# equally invasive action. Not recommended unless you know exactly what you are doing.
# It must return a KnowledgeFlask app instance.
def prepare_app(repo, app):
    return app
