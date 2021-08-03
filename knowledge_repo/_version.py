import os
import subprocess

__all__ = ['__author__', '__author_email__', '__version__', '__git_uri__', '__dependencies__', '__optional_dependencies__']

__author__ = "Erik Ritter (maintainer), Serena Jiang, John Bodley, Bill Ulammandakh, Naoya Kanai, Robert Chang, Dan Frank,  Chetan Sharma,  Matthew Wardrop"
__author_email__ = "erik.ritter@airbnb.com, serena.jiang@airbnb.com, john.bodley@airbnb.com, bill.ulammandakh@airbnb.com, naoya.kanai@airbnb.com, robert.chang@airbnb.com, dan.frank@airbnb.com, chetan.sharma@airbnb.com, mpwardrop@gmail.com"
__version__ = "0.9.0"
try:
    with open(os.devnull, 'w') as devnull:
        __version__ += '_' + subprocess.check_output(['git', 'rev-parse', 'HEAD'], shell=False, stderr=devnull).decode('utf-8').replace('\n', '')
except:
    pass
__git_uri__ = "https://github.com/airbnb/knowledge-repo.git"

# These are the core dependencies, and should include all packages needed for accessing repositories
# and running a non-server-side instance of the flask application. Optional dependencies for converters/etc
# should be defined elsewhere.
__dependencies__ = [
    # Knowledge Repository Dependencies
    'pyyaml',  # Yaml parser and utilities
    'markdown',  # Markdown conversion utilities
    'pygments',  # Code highlighting support in markdown
    'gitpython',  # Git abstraction
    'tabulate',  # Rendering information prettily in knowledge_repo script
    'cooked_input',  # Used for interactive input from user in CLI tooling
    'requests',  # Used for downloading images

    # Flask App Dependencies
    'flask',  # Main flask framework
    'flask_login',  # User management framework
    'flask_principal',  # Permissions management framework
    'flask_mail',  # Mail client and utilities
    'Flask-Migrate',  # Database migration utilities
    'sqlalchemy',  # Database abstractions
    'jinja2>=2.7',  # Templating engine
    'werkzeug>=1.0',  # Development webserver
    'gunicorn',  # Deployed webserver
    'inflection',  # String transformation library
    'pillow',  # Image thumbnailing
    'weasyprint',  # Post PDF download option
]

__optional_dependencies__ = {
    # ipynb notebook conversion suport
    'ipynb': [
        'nbformat',
        'nbconvert[execute]<6.0.0',
        'traitlets'
    ],

    # PDF to image conversion used by app
    'pdf': [
        'PyPDF2',  # image for parsing PDFs to images
        'wand',  # imagemagick integration for image uploading
    ],

    # Optional OAuth library for external authentication support
    'oauth': [
        'requests_oauthlib'
    ],

    # Optional ldap library for ldap authentication
    'ldap': [
        'ldap3'
    ],

    # Testing dependencies
    'dev': [
        'pycodestyle',  # PEP8 conformance
        'nose',  # Testing framework
        'beautifulsoup4',  # HTML/XML parser
        'coverage'  # Documentation coverage tester
    ]
}
__optional_dependencies__['all'] = [dep for deps in __optional_dependencies__.values() for dep in deps]
