import os
import subprocess
from setuptools import setup, find_packages
from distutils.command.build import build

# Extract version info from library
version_info = {}
with open('knowledge_repo/_version.py') as version_file:
    exec(version_file.read(), version_info)


setup(
    name='knowledge_repo',
    description=(
        " A workflow for contributing company knowledge, in the form "
        " of RMarkdowns, iPythons, and Markdowns, rendered and organized"
        " to magnify research impact across teams and time "),
    version=version_info['__version__'].split('_')[0],  # remove git revision if present
    author=version_info['__author__'],
    author_email=version_info['__author_email__'],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,  # See included paths in MANIFEST.in
    scripts=['scripts/knowledge_repo'],
    install_requires=[
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
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    extras_require={
        'all': ['coverage'],
        'dev': ['coverage'],
    }
)
