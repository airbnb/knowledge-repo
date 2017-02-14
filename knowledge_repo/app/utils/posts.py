"""Functions that interact with posts.

Functions include:
    - get_posts
    - get_all_post_stats
"""
import math
from flask import current_app
from sqlalchemy import func, distinct, or_

from ..app import db_session
from ..models import (Comment, PageView, Post,
                      Tag, Vote, User)


def get_query_param_set(params):
    """
    Strip, lowercase, and remove empty params to be used in a query
    """
    param_set = params.strip().lower().split(" ")
    param_set = [p for p in param_set if len(p) > 0]
    return param_set


def get_posts(feed_params):
    """
    Return a list of post objects (either WebEditorPosts or GitPosts)
    by building a query based on the feed_params
    :param feed_params: Parameters in the url request
    :type feed_params: object
    :return: Posts matching feed param specification
    :rtype: Tuple
    """

    # make sure post is published
    query = (db_session.query(Post).filter(Post.is_published))

    # posts returned should not include any posts in the excluded tags
    excluded_tags = current_app.config.get('EXCLUDED_TAGS', [])
    if excluded_tags:
        query = query.filter(~Post.tags.any(Tag.name.in_(excluded_tags)))

    # filter out based on feed param filters
    filters = feed_params['filters']
    if filters and str(filters):
        filter_set = get_query_param_set(filters)
        for elem in filter_set:
            query = query.filter(or_(func.lower(Post.keywords).like('%' + elem + '%'),
                                     func.lower(Post.keywords).like('%' + elem),
                                     func.lower(Post.keywords).like(elem + '%')))

    author_names = feed_params['authors']
    if author_names:
        author_names = [author_name.strip() for author_name in author_names.split(",")]
        query = query.filter(Post.authors.any(User.username.in_(author_names)))

    # sort - TODO clean up
    sort_by = feed_params['sort_by']

    # sort by post property
    post_properties = {
        "updated_at": Post.updated_at,
        "created_at": Post.created_at,
        "title": Post.title,
    }
    join_order_col = {
        "uniqueviews": func.count(distinct(PageView.user_id)),
        "allviews": func.count(PageView.object_id),
        "upvotes": func.count(Vote.object_id),
        "comments": func.count(Comment.post_id)
    }

    order_col = None
    if sort_by in post_properties:
        order_col = post_properties[sort_by]
    elif sort_by in join_order_col:  # sort by joined property
        order_col = join_order_col[sort_by]

        joins = {
            "uniqueviews": (PageView, PageView.object_id),
            "allviews": (PageView, PageView.object_id),
            "upvotes": (Vote, Vote.object_id),
            "comments": (Comment, Comment.post_id)
        }

        (join_table, join_on) = joins[sort_by]

        query = (db_session.query(Post, order_col)
                 .outerjoin(join_table, Post.path == join_on))
        query = query.group_by(Post.path)

    # sort order
    if order_col is not None:
        if feed_params['sort_desc']:
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())

    query = (query.order_by(Post.id.desc()))
    posts = query.all()

    # Check if a grouped by result, and if so, unnest Post object
    if posts and not isinstance(posts[0], Post):
        posts = [post[0] for post in posts]

    # get the right indexes
    feed_params['posts_count'] = len(posts)
    feed_params['page_count'] = int(math.ceil(float(len(posts)) / feed_params['results']))
    posts = posts[feed_params['start']:feed_params[
        'start'] + feed_params['results']]

    # Post.authors is lazy loaded, so we need to make sure it has been loaded before being
    # passed beyond the scope of this database db_session.
    for post in posts:
        post.authors

    post_stats = {post.path: {'all_views': post.view_count,
                              'distinct_views': post.view_user_count,
                              'total_likes': post.vote_count,
                              'total_comments': post.comment_count} for post in posts}

    db_session.expunge_all()

    return posts, post_stats
