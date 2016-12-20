import datetime
import json
import collections
from flask import Blueprint, request, render_template
from sqlalchemy import func

from ..app import db_session
from ..models import PageView, Post
from ..utils.requests import from_request_get_feed_params

blueprint = Blueprint('stats', __name__,
                      template_folder='../templates', static_folder='../static')


def _round_date(d):
    """Round date to the previous Monday"""
    return d - datetime.timedelta(d.weekday())


@blueprint.route('/post_stats', methods=['GET'])
@PageView.logged
def post_stats():
    """ Return the total views, distinct views, total likes and total comments
        for a given post """
    post_id = request.args.get('post_id', '')
    post = (db_session.query(Post)
                      .filter(Post.path == post_id)
                      .first())
    if not post:
        return json.dumps({})
    return json.dumps({'all_views': post.view_count,
                       'distinct_views': post.view_user_count,
                       'total_likes': post.vote_count,
                       'total_comments': post.comment_count})


@blueprint.route('/stats', methods=['GET'])
@PageView.logged
def stats():
    """ Render the stats page, creating graphs for
        pageviews daily, weekly, post creation weekly and
        cumulative posts per week
    """
    feed_params = from_request_get_feed_params(request)

    # count daily and weekly pageviews
    datetime_pageviews = (db_session.query(PageView.created_at, func.count(PageView.id))
                                    .group_by(PageView.created_at)
                                    .all())

    daily_pageviews = {}
    weekly_pageviews = {}
    for k, v in datetime_pageviews:
        d = k.date()
        wk = _round_date(d)
        daily_pageviews[d] = daily_pageviews.get(d, 0) + v
        weekly_pageviews[wk] = weekly_pageviews.get(wk, 0) + v

    # count post creation (created and updated)
    posts = (db_session.query(Post)
                       .filter(Post.is_published).all())

    created_at_counts = collections.Counter([_round_date(post.created_at.date()) for post in posts])
    updated_at_counts = collections.Counter([_round_date(post.updated_at.date()) for post in posts])

    all_week_keys = set(created_at_counts.keys()).union(updated_at_counts.keys())
    weekly_posts_created_and_updated = dict((k, [created_at_counts.get(k, 0), updated_at_counts.get(k, 0)])
                                            for k in all_week_keys)

    # cumulative weekly post created
    weekly_cumulative_posts = {}
    cum_created_val = 0
    for week in sorted(all_week_keys):
        cum_created_val += created_at_counts.get(week, 0)
        weekly_cumulative_posts[week] = cum_created_val

    return render_template('stats.html',
                           feed_params=feed_params,
                           daily_pageviews=daily_pageviews,
                           weekly_posts_created_and_updated=weekly_posts_created_and_updated,
                           weekly_cumulative_posts=weekly_cumulative_posts,
                           weekly_pageviews=weekly_pageviews)
