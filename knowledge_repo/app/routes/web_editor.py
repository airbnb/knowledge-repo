from builtins import range
from builtins import str
import json
import logging
import sys
import os
from collections import defaultdict
from datetime import datetime
from flask import request, render_template, Blueprint, current_app, url_for, send_from_directory, g
from sqlalchemy import or_
from werkzeug import secure_filename

from knowledge_repo.post import KnowledgePost
from ..proxies import db_session, current_repo
from ..models import Post, PostAuthorAssoc, Tag, Comment, User, PageView
from ..utils.emails import send_review_email, send_reviewer_request_email
from ..utils.image import pdf_page_to_png, is_pdf, is_allowed_image_format


if sys.version_info.major > 2:
    from urllib.parse import unquote as urlunquote
else:
    from urllib import unquote as urlunquote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


blueprint = Blueprint('web_editor', __name__,
                      template_folder='../templates', static_folder='../static')

# TODO: These functions have not been fully married to the KnowledgePost API
# Currently, backended by Post objects but partially implemented on KnowledgePost API


@blueprint.route('/ajax_tags_typeahead', methods=['GET'])
def generate_tags_typeahead():
    tag_objs = (db_session.query(Tag).all())
    tags_typeahead = [str(tag_obj.name) for tag_obj in tag_objs]
    return json.dumps(tags_typeahead)


@blueprint.route('/ajax_users_typeahead', methods=['GET'])
def generate_users_typeahead():
    user_objs = (db_session.query(User).all())
    users_typeahead = [str(user_obj.username) for user_obj in user_objs]
    return json.dumps(users_typeahead)


@blueprint.route('/ajax_projects_typeahead', methods=['GET'])
def generate_projects_typeahead():
    posts = db_session.query(Post).all()
    projects = []
    for p in posts:
        if p.project:
            projects.append(p.project)
        elif p.path:
            projects.append(from_path_get_project(p.path))
    return json.dumps(list(set(projects)))


def from_path_get_project(path):
    """
    To maintain an organization of webposts beyond a top-level
    grouping, we keep track of a "project" for each post
    :param: path of the post
    :type path: string
    """
    folder_list = path.split("/")
    # All posts are under the "projects/" folder
    # We assume the next folder is the project
    if len(folder_list) >= 2:
        return folder_list[1]
    return ""


@blueprint.route('/webposts', methods=['GET'])
@PageView.logged
def gitless_drafts():
    """ Render the gitless posts that a user has created in table form
        Editors can see all the posts created via Gitless_Editing
    """
    query = (db_session.query(Post))
    if current_app.config.get('WEB_EDITOR_PREFIXES', None):
        query = query.filter(or_(*[Post.path.like(p + '%') for p in current_app.config['WEB_EDITOR_PREFIXES']]))

    if g.user.username not in current_repo.config.editors:
        query = (query.outerjoin(PostAuthorAssoc, PostAuthorAssoc.post_id == Post.id)
                      .filter(PostAuthorAssoc.user_id == g.user.id))

    webposts = query.all()

    return render_template("web_posts.html", posts=webposts)


@blueprint.route('/posteditor', methods=['GET', 'POST'])
@PageView.logged
def post_editor():
    """ Render the web post editor, either with the default settings
        or if the post already exists, with what has been saved
    """
    post_id = request.args.get('post_id', None)

    headers = defaultdict(lambda: None)
    status = current_repo.PostStatus.DRAFT
    markdown = None
    comments = None
    thumbnail = ''
    if post_id and post_id != 'None':
        webpost = (db_session.query(Post)
                             .filter(Post.id == post_id)
                             .first())
        webpost_path = webpost.path
        thumbnail = webpost.thumbnail
        kp = current_repo.post(webpost_path)
        status = current_repo.post_status(webpost_path)
        headers = kp.headers
        markdown = kp.read(images=False, headers=False)
        comments = (db_session.query(Comment)
                              .filter(Comment.post_id == post_id)
                              .filter(Comment.type == "review")
                              .all())

    can_approve = 0
    authors_str = ''
    if 'authors' in headers:
        authors_str = ', '.join(headers['authors'])
        if g.user.username not in authors_str:
            can_approve = 1

    tags_str = ''
    if 'tags' in headers:
        tags_str = ', '.join(headers['tags'])

    # get created at and updated at, or default to now
    created_at = (headers['created_at'] or datetime.now()).strftime('%Y-%m-%d')
    updated_at = (headers['updated_at'] or datetime.now()).strftime('%Y-%m-%d')

    return render_template('post_editor.html',
                           title=headers['title'],
                           project=headers.get('project', ''),
                           created_at=created_at,
                           updated_at=updated_at,
                           author=authors_str,
                           tags=tags_str,
                           tldr=headers['tldr'],
                           markdown=markdown,
                           post_id=post_id,
                           status=status.value,
                           comments=comments,
                           feed_image=thumbnail,
                           can_approve=can_approve,
                           username=g.user.username)


@blueprint.route('/submit', methods=['GET', 'POST'])
@PageView.logged
def submit_for_review():
    """ Change the status of a gitless post
        And if there are reviewers assigned, email them
    """
    post_id = request.args.get('post_id', None)
    data = request.get_json()
    post = (db_session.query(Post)
                      .filter(Post.id == post_id)
                      .first())
    post.status = current_repo.PostStatus.SUBMITTED
    db_session.commit()

    path = post.path
    current_repo.submit(path)

    # email the reviewers
    if not data['post_reviewers']:
        return
    reviewers = data['post_reviewers'].split(",")
    if reviewers:
        for r in reviewers:
            send_reviewer_request_email(post_id=post_id, reviewer=r)
    return ""


@blueprint.route('/publish_post', methods=['GET', 'POST'])
@PageView.logged
def publish_post():
    """ Publish the gitless post by changing the status """
    post_id = request.args.get('post_id', None)
    post = (db_session.query(Post)
                      .filter(Post.id == post_id)
                      .first())
    if not post:
        error_msg = "Unable to retrieve post with id = {}!".format(str(post_id))
        json_str = json.dumps({'msg': error_msg, 'success': False})
        return json_str

    post.status = current_repo.PostStatus.PUBLISHED
    db_session.commit()

    path = post.path
    current_repo.publish(path)
    return ""


@blueprint.route('/unpublish_post', methods=['GET', 'POST'])
@PageView.logged
def unpublish_post():
    """ Unpublish the post, going back to the in_review status """
    post_id = request.args.get('post_id', None)
    post = (db_session.query(Post)
                      .filter(Post.id == post_id)
                      .first())
    post.status = current_repo.PostStatus.UNPUBLISHED
    db_session.commit()

    path = post.path
    current_repo.unpublish(path)
    return ""


@blueprint.route('/author_publish', methods=['POST'])
@PageView.logged
def change_author_publish():
    """ Allow the author to publish their own webpost if the
        editor allows them to
    """
    post_id = request.args.get('post_id', None)
    post = (db_session.query(Post)
                      .filter(Post.id == post_id)
                      .first())
    post.status = current_repo.PostStatus.UNPUBLISHED
    db_session.commit()

    path = post.path
    current_repo.accept(path)
    return ""


@blueprint.route('/save_post', methods=['GET', 'POST'])
@PageView.logged
def save_post():
    """ Save the gitless post """
    post_id = request.args.get('post_id', None)
    data = request.get_json()
    post = (db_session.query(Post)
            .filter(Post.id == post_id)
            .first())
    new_post = False
    if not post:
        new_post = True
        path = "{}/{}.kp".format(data['project'],
                                 data['title'].encode('utf8').lower().replace(' ', '_'))
        if current_app.config.get('WEB_EDITOR_PREFIXES', None):
            # TODO: Include dropdown on webeditor to have user specify repo
            path = "{}/{}".format(current_app.config['WEB_EDITOR_PREFIXES'][0], path)

        post = (db_session.query(Post)
                          .filter(Post.path == path)
                          .first())
        if post:
            error_msg = "Post with project {} and title {} already exists!".format(data['project'], data['title'])

            json_str = json.dumps({'msg': error_msg, 'success': False})
            return json_str
        else:
            post = Post()
            post.path = path
    else:
        path = post.path

    # create the knowledge post
    kp = KnowledgePost(path=path)

    headers = {}
    headers['created_at'] = datetime.strptime(data['created_at'], '%Y-%m-%d')
    headers['updated_at'] = datetime.strptime(data['updated_at'], '%Y-%m-%d')
    headers['title'] = str(data['title'])
    headers['path'] = str(post.path)
    headers['project'] = str(data['project'])
    # TODO: thumbnail header not working currently, as feed image set with kp
    # method not based on header
    headers['thumbnail'] = str(data['feed_image'])
    headers['authors'] = [str(auth).strip() for auth in data['author']]
    headers['tldr'] = str(data['tldr'])
    headers['tags'] = [str(tag).strip() for tag in data['tags']]
    kp.write(urlunquote(str(data['markdown'])), headers=headers)

    # add to repo
    current_repo.add(kp, update=True)  # THIS IS DANGEROUS
    db_session.commit()

    # add to index
    post.update_metadata_from_kp(kp)
    if new_post:
        db_session.add(post)
    db_session.commit()

    return json.dumps({'post_id': str(post.id)})


@blueprint.route('/delete_post', methods=['GET'])
@PageView.logged
def delete_post():
    """ Delete a post """
    post_id = request.args.get('post_id', None)
    item = (db_session.query(Post)
                      .filter(Post.id == post_id)
                      .first())
    db_session.delete(item)
    db_session.commit()
    return ""


@blueprint.route('/file_upload', methods=['POST', 'GET'])
@PageView.logged
def file_upload():
    """ Uploads images dropped on the web editor's markdown box to static/images
        and notifies editors by email
    """
    upload_folder = 'images'
    title = request.form['title']
    files = request.files
    uploadedFiles = []

    if files:
        for img_file in files.values():
            filename = secure_filename(title + "_" + img_file.filename).lower()
            dst_folder = os.path.join(current_app.static_folder, upload_folder)

            if is_allowed_image_format(img_file):
                try:
                    img_file.save(os.path.join(dst_folder, filename))
                    send_from_directory(dst_folder, filename)
                    uploadedFiles += [url_for("static", filename=os.path.join(upload_folder, filename))]
                except Exception as e:
                    error_msg = "ERROR during image upload: {}".format(str(e))
                    logger.error(error_msg)
                    return json.dumps({'error_msg': error_msg, 'success': False})

            elif is_pdf(filename):
                from PyPDF2 import PdfFileReader
                try:
                    src_pdf = PdfFileReader(img_file)
                    filename = os.path.splitext(filename)[0]
                    num_pages = src_pdf.getNumPages()
                    for page_num in range(num_pages):
                        page_png = pdf_page_to_png(src_pdf, page_num)
                        page_name = "{filename}_{page_num}.jpg".format(**locals())
                        page_png.save(filename=os.path.join(dst_folder, page_name))
                        uploadedFiles += [url_for("static", filename=os.path.join(upload_folder, page_name))]
                except Exception as e:
                    error_msg = "ERROR during pdf upload: {}".format(str(e))
                    logger.error(error_msg)
                    return json.dumps({'error_msg': error_msg, 'success': False})

    return json.dumps({'links': uploadedFiles, 'success': True})


@blueprint.route('/review', methods=['POST'])
@PageView.logged
def review_comment():
    """ Saves the comments underneath a Gitless Post to a table
        and sends an email that the post has been reviewed to the
        author of the post
    """
    post_id = request.args.get('post_id', None)
    commenter, commenter_id = g.user.username, g.user.id
    data = request.get_json()   # just the comment text
    comment = Comment()
    comment.text = data['text']
    comment.user_id = commenter_id
    comment.post_id = post_id
    comment.type = "review"
    db_session.add(comment)
    db_session.commit()

    send_review_email(post_id=post_id, commenter=commenter,
                      comment_text=comment.text)
    return ""


@blueprint.route('/delete_review', methods=['GET', 'POST'])
@PageView.logged
def delete_review():
    """ Delete a comment that was made underneath a gitless contribution post """
    try:
        comment_id = int(request.args.get('comment_id', ''))
        items = db_session.query(Comment).filter(
            Comment.id == comment_id).all()
        for item in items:
            db_session.delete(item)
        db_session.commit()
    except:
        logging.warning("ERROR processing request")
        pass
    return ""
