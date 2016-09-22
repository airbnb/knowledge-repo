import subprocess

__all__ = ['__author__', '__author_email__', '__version__', '__git_uri__', '__dependencies__']

__author__ = "Nikki Ray (maintainer), Robert Chang, Dan Frank,  Chetan Sharma,  Matthew Wardrop"
__author_email__ = "nikki.ray@airbnb.com, robert.chang@airbnb.com, dan.frank@airbnb.com, chetan.sharma@airbnb.com, matthew.wardrop@airbnb.com"
__version__ = "0.5"
try:
    __version__ += '_' + subprocess.check_output(['git', 'rev-parse', 'HEAD'], shell=False).decode('utf-8').replace('\n', '')
except:
    pass
__git_uri__ = "git@github.com:airbnb/knowledge-repo.git"

__dependencies__ = [
    # Knowledge Repository Dependencies
    'markdown',  # Markdown conversion utilities
    'nbconvert',  # Jupyter notebook conversion utilities
    'nbformat',  # Jupyter notebook reference format
    'gitpython',  # Git abstraction
    'pyyaml',  # Yaml parser and utilities
    'tabulate',  # Rendering user information prettily
    'enum34',  # Post status enum object
    'future',  # Python 2/3 support
    # Flask App Dependencies
    'flask',  # Main flask framework
    'flask_mail',  # Mail client and utilities
    'Flask-Migrate',  # Database migration utilities
    'sqlalchemy',  # Database abstractions
    'jinja2>=2.7',  # Templating engine
    'werkzeug',  # Development webserver
    'gunicorn',  # Deployed webserver
    'inflection',  # String transformation library
    'PyPDF2',  # image for parsing PDFs to images
    'wand',  # imagemagick integration for image uploading
    'Pillow',  # image processing for sending images
    # Testing Dependencies
    'nose',  # Testing framework
    'beautifulsoup4'  # HTML/XML parser
]
