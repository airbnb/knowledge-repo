""" Define the routes that deal with tags

This includes:
  - /tag_pages
  - /batch_tags
  - /delete_tag
  - /delete_tag_posts
  - /edit_tag_description
  - /rename_tag
  - /remove_posts_tags
  - /toggle_tag_subscription
  - /tag_list
"""
from flask import current_app, request, render_template, Blueprint, g
from sqlalchemy import and_
import logging
import math

from ..app import db_session
from ..models import PageView, Post, assoc_post_tag, Subscription, Tag
from ..utils.requests import from_request_get_feed_params
from ..utils.emails import send_subscription_email

blueprint = Blueprint('tag', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/batch_tags')
@PageView.logged
def render_batch_tags():
    """ Render the batch_tags page, which lists all the tags.

        From this view, editors can:
            - rename them
            - delete them
            - delete the tag from certain posts
            - add a tag description
    """
    # get the args
    # sort_by will either be "Tag" or "Number of Posts"
    sort_by = request.args.get('sort_by', '')
    sort_asc = request.args.get('sort_asc', '')
    sort_desc = not sort_asc
    feed_params = from_request_get_feed_params(request)

    excluded_tags = current_app.config.get('EXCLUDED_TAGS', [])
    all_tags = db_session.query(Tag).all()
    tags_to_posts = {}
    nonzero_tags = []
    tags_to_description = {}
    for tag in all_tags:
        posts = tag.posts

        if not posts:
            db_session.delete(tag)
            db_session.commit()

        tags_to_posts[tag.id] = [(post.path, post.title) for post in posts if
                                 post.is_published and not post.contains_excluded_tag]
        nonzero_tags.append(tag)
        # so that we can use the tag in the jinja template
        db_session.expunge(tag)

        tags_to_description[tag.id] = tag.description

    if sort_by:
        if sort_by == "Tag":
            def compare(x):
                return x.name.lower()
        elif sort_by == "Number_of_Posts":
            def compare(x):
                return len(tags_to_posts[x.id])
        else:
            def compare(x):
                return x
        nonzero_tags = sorted(nonzero_tags, key=compare, reverse=sort_desc)

    return render_template("batch_tags.html",
                           tags=nonzero_tags,
                           tags_to_posts=tags_to_posts,
                           tags_to_desc=tags_to_description,
                           feed_params=feed_params)


@blueprint.route('/delete_tag_post', methods=['GET', 'POST'])
@PageView.logged
def delete_tags_from_posts():
    """ Delete a tag from all the posts associated with it """
    tag_id = int(request.args.get('tag_id'))

    tag_obj = (db_session.query(Tag)
               .filter(Tag.id == tag_id)
               .first())

    delete_query = assoc_post_tag.delete().where(assoc_post_tag.c.tag_id == tag_id)
    db_session.execute(delete_query)
    db_session.delete(tag_obj)
    db_session.commit()

    return ""


@delete_tags_from_posts.object_extractor
def delete_tags_from_posts():
    tag_obj = Tag.query.filter(Tag.name == request.args.get('tag_name', '')).first()
    return {
        'id': tag_obj.id if tag_obj else None,
        'type': 'tag',
        'action': 'delete'
    }


@blueprint.route('/tag_pages')
@PageView.logged
def render_tag_pages():
    feed_params = from_request_get_feed_params(request)
    start = feed_params['start']
    num_results = feed_params['results']
    tag = request.args.get('tag', '')

    if tag[0] == '#':
        tag = tag[1:]

    if tag in current_app.config.get('EXCLUDED_TAGS', []):
        return render_template('error.html')

    tag_obj = (db_session.query(Tag)
               .filter(Tag.name == tag)
               .first())

    tag_description = tag_obj.description

    # Get subscription status
    subscribed = tag in feed_params["subscriptions"]

    # get all files with given tag
    tag_posts = tag_obj.posts
    posts = [post for post in tag_posts if post.is_published]

    feed_params['posts_count'] = len(posts)
    feed_params['page_count'] = int(math.ceil(1.0 * len(posts) / feed_params['results']))

    posts = posts[start:min(start + num_results, len(posts))]

    post_stats = {post.path: {'all_views': post.view_count,
                              'distinct_views': post.view_user_count,
                              'total_likes': post.vote_count,
                              'total_comments': post.comment_count} for post in posts}

    author_to_count = {}
    for post in posts:
        authors = post.authors
        for author in authors:
            name = author.format_name
            if name in author_to_count:
                author_to_count[name] += 1
            else:
                author_to_count[name] = 1

    # get author with the max count
    max_count = 1
    max_author = ''
    for (author, count) in author_to_count.items():
        if count >= max_count:
            max_author = author
            max_count = count

    return render_template("tag_pages.html",
                           feed_params=feed_params,
                           full_tag=tag,
                           top_header=tag,
                           tag_description=tag_description,
                           tag_pocs=max_author,
                           posts=posts,
                           subscribed=subscribed,
                           post_stats=post_stats)


@render_tag_pages.object_extractor
def render_tag_pages():
    tag_obj = Tag.query.filter(Tag.name == request.args.get('tag', '')).first()
    return {
        'id': tag_obj.id if tag_obj is not None else None,
        'type': 'tag',
        'action': 'view'
    }


@blueprint.route('/edit_tag_description', methods=['POST'])
@PageView.logged
def edit_tag_desc():
    """ Edit the description of a tag. This is used in the tag_page """
    data = request.get_json()
    tag_id = int(data['tagId'])
    new_tag_desc = data['tagDesc']
    if new_tag_desc:
        tag = (db_session.query(Tag)
               .filter(Tag.id == tag_id)
               .first())
        tag._description = new_tag_desc
        db_session.commit()
    return ""


@edit_tag_desc.object_extractor
def edit_tag_desc():
    tag_obj = Tag.query.filter(Tag.id == request.get_json()['tagId']).first()
    return {
        'id': tag_obj.id if tag_obj is not None else None,
        'type': 'tag',
        'action': 'edit'
    }


@blueprint.route('/toggle_tag_subscription', methods=['GET', 'POST'])
@PageView.logged
def toggle_tag_subscription():
    """ Subscribe/Unsubscribe a user from a tag """
    try:
        # retrieve relevant tag and user args from request
        tag_name = request.args.get('tag_name', '')

        if tag_name in current_app.config.get('EXCLUDED_TAGS', []):
            logging.warning("Trying to subscribe to an excluded tag")
            return ""

        subscribe_action = request.args.get('subscribe_action', '')
        if subscribe_action not in ['unsubscribe', 'subscribe']:
            logging.warning("ERROR processing request")
            return ""

        # get the tag object so we can get the id
        tag_obj = (db_session.query(Tag)
                   .filter(and_(Tag.name == tag_name))
                   .first())
        # retrieve the current subscription object for a user and tag if exists
        subscription = None
        if tag_obj:
            subscription = db_session.query(Subscription).filter(
                and_(Subscription.object_type == 'tag',
                     Subscription.user_id == g.user.id,
                     Subscription.object_id == tag_obj.id)).first()
        if subscription and subscribe_action == 'unsubscribe':
            db_session.delete(subscription)
        elif not subscription and subscribe_action == 'subscribe':
            # otherwise, create new subscription
            subscription = Subscription(user_id=g.user.id, object_type='tag',
                                        object_id=tag_obj.id)
            db_session.add(subscription)
        else:
            logging.warning("ERROR processing request")
            return ""
        db_session.commit()
        return ""
    except:
        logging.warning("ERROR processing request")
        return ""


@toggle_tag_subscription.object_extractor
def toggle_tag_subscription():
    tag_obj = Tag(name=request.args.get('tag_name', ''))
    subscription = db_session.query(Subscription).filter(
        and_(Subscription.object_type == 'tag',
             Subscription.user_id == g.user.id,
             Subscription.object_id == tag_obj.id)
    ).first()
    return {
        'id': tag_obj.id if tag_obj is not None else None,
        'type': 'tag',
        'action': 'unsubscribe' if subscription else 'subscribe'
    }


@blueprint.route('/rename_tag', methods=['POST'])
@PageView.logged
def rename_tags_and_posts():
    """ Rename a tag
        This requires deleteing all the post-tag associations for the old tag
        and re-adding them for the new tag
    """
    data = request.get_json()
    old_tag_id = int(data['oldTagId'])
    new_tag = data['newTag']

    old_tag_obj = (db_session.query(Tag)
                   .filter(Tag.id == old_tag_id)
                   .first())

    new_tag_obj = (db_session.query(Tag)
                   .filter(Tag.name == new_tag)
                   .first())
    if not new_tag_obj:
        new_tag_obj = Tag(name=new_tag)
        db_session.commit()

    # add all the new associations in
    new_tag_post_ids_before = [p.id for p in new_tag_obj.posts]
    for p in old_tag_obj.posts:
        if p.id not in new_tag_post_ids_before:
            new_tag_obj.posts.append(p)
    db_session.commit()

    # delete the tag associations
    old_tag_obj.posts = []
    db_session.delete(old_tag_obj)
    db_session.commit()
    return ""


@rename_tags_and_posts.object_extractor
def rename_tags_and_posts():
    tag_id = int(request.get_json()['oldTagId'])
    return {
        'id': tag_id if tag_id else None,
        'type': 'tag',
        'action': 'rename'
    }


@blueprint.route('/remove_posts_tags', methods=['POST'])
@PageView.logged
def remove_posts_tags():
    """ Delete a tag from certain posts """
    data = request.get_json()
    tag_id = data['tagId']
    posts = data['posts']
    posts = [str(x) for x in posts]

    # for all the posts, query & remove that tag
    for post in posts:
        post_id = (db_session.query(Post).filter(Post.path == post).first()).id
        delete_query = assoc_post_tag.delete().where(
            and_(assoc_post_tag.c.tag_id == tag_id, assoc_post_tag.c.post_id == post_id))
        db_session.execute(delete_query)
    db_session.commit()
    return ""


@remove_posts_tags.object_extractor
def remove_posts_tags():
    return {
        'id': int(request.get_json()['tagId']),
        'type': 'tag',
        'action': 'dissociate'
    }


@blueprint.route('/tag_list', methods=['POST'])
@PageView.logged
def change_tags():
    """ Change the tags associated with a given post.
        This is called when someone clicks on the a knowledge post
        and changes the tag through the web ui
    """
    post_path = request.args.get('post_path', ' ')
    data = request.get_json()
    tags_string = data['tags']

    post = (db_session.query(Post)
            .filter(Post.path == post_path)
            .first())

    old_tags = post.tags
    tag_set = set(old_tags)
    tags_list = tags_string.split(",")
    post.tags = tags_list
    # post tag settr might take subset of tags_list to avoid dupes or whatever else
    new_tags = post.tags

    email_tags = [tag for tag in new_tags if tag not in tag_set]

    db_session.commit()

    for tag in email_tags:
        send_subscription_email(post, tag)

    return " "


@change_tags.object_extractor
def change_tags():
    post_path = request.args.get('post_path', '')
    return {
        'id': Post.query.filter(Post.path == post_path).first().id,
        'type': 'post',
        'action': 'tag'
    }
