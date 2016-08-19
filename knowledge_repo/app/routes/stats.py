import datetime
import json
from flask import Blueprint, request, render_template, current_app
from sqlalchemy import or_, and_, func

from ..app import db_session
from ..utils.date import next_weekday, get_all_weeks
from ..models import PageView, Post
from ..constants import GitPostStatus, WebPostStatus


blueprint = Blueprint('stats', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/post_stats', methods=['GET'])
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
@PageView.log_pageview
def stats():
    """ Render the stats page, creating graphs for
        pageviews daily, weekly, post creation weekly and
        cumulative posts per week
    """

    all_weeks = get_all_weeks()
    date_count = (db_session.query(PageView.created_at, func.count(PageView.id))
                  .group_by(PageView.created_at)
                  .all())
    created_dict = {}
    for (c, p) in date_count:
        c_trun = datetime.datetime(c.year, c.month, c.day)
        c_trun_s = c_trun.strftime('%Y-%m-%d')
        if c_trun_s in created_dict:
            created_dict[c_trun_s] += p
        else:
            created_dict[c_trun_s] = p

    sorted_page_keys = sorted(created_dict.keys())
    sorted_page_views = [created_dict[k] for k in sorted_page_keys]

    created_ats = {}
    updated_ats = {}

    posts = (db_session.query(Post).filter(Post.is_published).all())

    for f in posts:
        created_at = datetime.datetime.strftime(f.created_at, '%Y-%m-%d')
        updated_at = datetime.datetime.strftime(f.updated_at, '%Y-%m-%d')
        if created_at:
            if created_at in created_ats:
                created_ats[created_at] += 1
            else:
                created_ats[created_at] = 1
        if updated_at:
            if updated_at in updated_ats:
                updated_ats[updated_at] += 1
            else:
                updated_ats[updated_at] = 1

    created_at_dates = created_ats.keys()
    updated_at_dates = updated_ats.keys()
    set_dates = sorted(set(created_at_dates + updated_at_dates))
    saturdays = {saturday: [0, 0, 0] for saturday in all_weeks}
    for d in set_dates:
        closest_saturday = next_weekday(d, 5)
        if closest_saturday in saturdays:
            [created, updated, pageviews] = saturdays[closest_saturday]
            # TODO: This does not appear to make sense to me (Matthew)
            v0, v1 = 0, 0
            if d in created_ats:
                v0 = created_ats[d]
                if d in updated_ats:
                    v1 = updated_ats[d]
            else:
                if d in updated_ats:
                    v1 = updated_ats[d]
            saturdays[closest_saturday] = [v0 + created, v1 + updated, 0]

    for day in created_dict:
        c_saturday = next_weekday(day, 5)
        saturdays[c_saturday][2] += created_dict[day]

    sorted_keys = sorted(saturdays.keys())
    sorted_values = [saturdays[v] for v in sorted_keys]

    # make cumulative sum
    cum_sums = [[0, 0, 0] for i in sorted_values]
    for i in range(len(sorted_values) - 1):
        cum_sums[i + 1][0] = cum_sums[i][0] + sorted_values[i + 1][0]
        cum_sums[i + 1][1] = cum_sums[i][1] + sorted_values[i + 1][1]
        cum_sums[i + 1][2] = cum_sums[i][2] + sorted_values[i + 1][2]

    return render_template('stats.html',
                           pageview_dates=sorted_page_keys,
                           pageview_views=sorted_page_views,
                           posts_dates=sorted_keys,
                           posts_values=sorted_values,
                           posts_values_cum=cum_sums)
