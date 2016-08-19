from __builtin__ import object
import string


class WebPostStatus(object):
    """
    Static class with webpost constants to avoid hard-coding
    """
    PRIVATE_WEBPOST = 0
    IN_REVIEW_WEBPOST = 1
    PUBLISHED_WEBPOST = 2


class GitPostStatus(object):
    """
    Static class with gitpost constants to avoid hard-coding
    """
    REVERTED_GITPOST = 0
    PUBLISHED_GITPOST = 1


class TagConstants(object):
    """
    Static class with tag constants to avoid hard-coding
    """
    DEFAULT_TAG_TYPE = "other"
    PRIVATE_TAG = "other/private"


STOPWORDS = [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves',
             u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him',
             u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its',
             u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what',
             u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am',
             u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has',
             u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the',
             u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while',
             u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between',
             u'into', u'through', u'during', u'before', u'after', u'above', u'below',
             u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over',
             u'under', u'again', u'further', u'then', u'once', u'here', u'there',
             u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each',
             u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor',
             u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very',
             u's', u't', u'can', u'will', u'just', u'don', u'should', u'now'] + list(string.punctuation)
