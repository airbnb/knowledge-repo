# Configuration for this knowledge data repository.


# A function called to see whether a specified path is permitted in the repository
# Only enforced when creating/modifying posts. It should return the path as a standard
# unix path (virtual folders separated by '/' and the final node should end in '.kp').
# It should raise an exception if the provided path is is not permitted in the knowledge
# repository.
def path_parse(path):
    return path


# A dictionary of aliases which point to knowledge posts. This allows you to alias posts
# which may be useful to forward old links to new locations, or to give certain posts
# precedence. It also allows the post path to violate the normal naming rules of posts.
# The only condition is that they cannot mask an existing post url, in which case the
# alias is silently ignored.
aliases = {}


# Postprocessors to apply when importing KnowledgePost objects into the repository.
# Note that KnowledgePost objects by default run 'extract_images' and 'format_checks'.
# Order is important.
postprocessors = []


# Usernames of users to keep informed of changes to the knowledge data repo
editors = []


# Function to check whether provided username is a valid username, and if not, mutate it
# such that it is. Should raise an exception if that is not possible, and otherwise
# return the parsed username.
def username_parse(username):
    return username


# Function to convert a username to a person's proper name
def username_to_name(username):
    return username


# Function to convert a username to a person's email
def username_to_email(username):
    return '{}@example.com'.format(username)


# Function to generate the web uri for a knowledge post at
# path `path`. If `None`, should return the web uri for
# the entire repository. Return `None` if a web uri does
# not exist.
def web_uri(path=None):
    return None


# WARNING: ADVANCED!
# Function that is called on a Flask web app instance before it is launched
# This is useful if you need to add a route for your local deployment, or other
# equally invasive action. Not recommended unless you know exactly what you are doing.
# It must return a KnowledgeFlask app instance.
def prepare_app(app):
    return app
