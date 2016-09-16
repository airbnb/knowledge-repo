import subprocess

__all__ = ['__author__', '__author_email__', '__version__', '__git_uri__']

__author__ = "Nikki Ray (maintainer), Robert Chang, Dan Frank,  Chetan Sharma,  Matthew Wardrop"
__author_email__ = "nikki.ray@airbnb.com, robert.chang@airbnb.com, dan.frank@airbnb.com, chetan.sharma@airbnb.com, matthew.wardrop@airbnb.com"
__version__ = "0.5"
try:
    __version__ += '_' + subprocess.check_output(['git', 'rev-parse', 'HEAD'], shell=False).decode('utf-8').replace('\n', '')
except:
    pass
__git_uri__ = "git@github.com:airbnb/knowledge-repo.git"
