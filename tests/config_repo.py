# Configuration for this knowledge data repository.

# Paths relative to repository root in which to look for posts
search_paths = ['.']


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

# Contrib plugins used in the app, ex ['web_editor']
plugins = []


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


# WARNING: ADVANCED!
# Function that is called on a Flask web app instance before it is launched
# This is useful if you need to add a route for your local deployment, or other
# equally invasive action. Not recommended unless you know exactly what you are doing.
# It must return a KnowledgeFlask app instance.
def prepare_app(app):
    server_config_defaults = {'DEFAULT_GROUP': 'knowledge_contributors',
                              'AUTH_USERNAME_REQUEST_HEADER': 'user_header'}
    for k in server_config_defaults:
        app.config[k] = server_config_defaults[k]
    app.repository.config.editors.append('knowledge_default')
    return app
