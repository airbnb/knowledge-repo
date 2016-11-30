import json
import logging
import sys
import os
from builtins import str
from datetime import datetime
from flask import request, render_template, Blueprint, current_app, url_for, send_from_directory, g
from sqlalchemy import or_
from werkzeug import secure_filename

from knowledge_repo.post import KnowledgePost
from ..proxies import db_session, current_repo
from ..models import Post, PostAuthorAssoc, Tag, Comment, User, PageView
from ..utils.emails import send_review_email, send_reviewer_request_email
from ..utils.image import pdf_page_to_png, is_pdf, is_allowed_image_format

from ..index import update_index

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
    return json.dumps([t[0] for t in db_session.query(Tag.name).all()])


@blueprint.route('/ajax_users_typeahead', methods=['GET'])
def generate_users_typeahead():
    return json.dumps([u[0] for u in db_session.query(User.username).all()])


@blueprint.route('/ajax_paths_typeahead', methods=['GET'])
def generate_projects_typeahead():
    # return path stubs for all repositories
    stubs = ['/'.join(p.split('/')[:-1]) for p in current_repo.dir()]
    return json.dumps(list(set(stubs)))


@blueprint.route('/webposts', methods=['GET'])
@PageView.logged
def gitless_drafts():
    """ Render the gitless posts that a user has created in table form
        Editors can see all the posts created via Gitless_Editing
    """
    prefixes = current_app.config.get('WEB_EDITOR_PREFIXES', [])
    if prefixes == []:
        raise Exception("Web editing is not configured")

    query = (db_session.query(Post))
    if prefixes is not None:
        query = query.filter(or_(*[Post.path.like(p + '%') for p in prefixes]))

    if g.user.username not in current_repo.config.editors:
        query = (query.outerjoin(PostAuthorAssoc, PostAuthorAssoc.post_id == Post.id)
                      .filter(PostAuthorAssoc.user_id == g.user.id))

    return render_template("web_posts.html", posts=query.all())


@blueprint.route('/posteditor', methods=['GET', 'POST'])
@PageView.logged
def post_editor():
    """ Render the web post editor, either with the default values
        or if the post already exists, with what has been saved """
    path = request.args.get('path', None)
    # set defaults
    data = {'title': None,
            'status': current_repo.PostStatus.DRAFT.value,
            'markdown': None,
            'thumbnail': '',
            'can_approve': 0,
            'username': g.user.username,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'authors': [g.user.username],
            'comments': []}

    if path is not None and path in current_repo:
        kp = current_repo.post(path)
        data.update(kp.headers)

        data['status'] = kp.status.value
        data['path'] = path
        data['markdown'] = kp.read(images=False, headers=False)

        # retrieve reviews
        post = db_session.query(Post).filter(Post.path == path).first()
        if post:  # post may have not been indexed yet
            data['comments'] = (db_session.query(Comment)
                                          .filter(Comment.post_id == post.id)
                                          .filter(Comment.type == "review")
                                          .all())

    if g.user.username not in data['authors'] or g.user.username in current_repo.config.editors:
        data['can_approve'] = 1

    data['created_at'] = data['created_at'].strftime('%Y-%m-%d')
    data['updated_at'] = data['updated_at'].strftime('%Y-%m-%d')
    data['authors'] = json.dumps(data.get('authors'))
    data['tags'] = json.dumps(data.get('tags', []))

    if 'proxy' in data or request.args.get('proxy', False):
        return render_template('post_editor_proxy.html', **data)
    return render_template('post_editor_markdown.html',
                           **data)


@blueprint.route('/save_post', methods=['GET', 'POST'])
@PageView.logged
def save_post():
    """ Save the post """

    data = request.get_json()
    path = data['path']

    prefixes = current_app.config['WEB_EDITOR_PREFIXES']
    if prefixes == []:
        raise Exception("Web editing is not configured")

    if prefixes is not None:
        if not any([path.startswith(prefix) for prefix in prefixes]):
            return json.dumps({'msg': ("Your post path must begin with one of {}").format(prefixes),
                               'success': False})

    # TODO better handling of overwriting
    kp = None
    if path in current_repo:
        kp = current_repo.post(path)
        if g.user.username not in kp.headers['authors']:
            return json.dumps({'msg': ("Post with path {} already exists and you are not an author!",
                                       "\nPlease try a different path").format(path),
                               'success': False})

    # create the knowledge post
    kp = kp or KnowledgePost(path=path)

    headers = {}
    headers['created_at'] = datetime.strptime(data['created_at'], '%Y-%m-%d').date()
    headers['updated_at'] = datetime.strptime(data['updated_at'], '%Y-%m-%d').date()
    headers['title'] = data['title']
    headers['path'] = data['path']
    # TODO: thumbnail header not working currently, as feed image set with kp
    # method not based on header
    headers['thumbnail'] = data.get('feed_image', '')
    headers['authors'] = [auth.strip() for auth in data['author']]
    headers['tldr'] = data['tldr']
    headers['tags'] = [tag.strip() for tag in data.get('tags', [])]
    if 'proxy' in data:
        headers['proxy'] = data['proxy']

    kp.write(urlunquote(data['markdown']), headers=headers)
    # add to repo
    current_repo.add(kp, update=True, message=headers['title'])  # THIS IS DANGEROUS

    update_index()
    return json.dumps({'path': path})


@blueprint.route('/submit', methods=['GET', 'POST'])
@PageView.logged
def submit_for_review():
    """ Submit post and if there are reviewers assigned, email them"""
    path = request.args.get('path', None)
    data = request.get_json()
    current_repo.submit(path)

    # email the reviewers
    reviewers = data.get('post_reviewers', None)
    if reviewers:
        for r in reviewers.split(','):
            send_reviewer_request_email(path=path, reviewer=r)

    update_index()
    return 'OK'


@blueprint.route('/publish_post', methods=['GET', 'POST'])
@PageView.logged
def publish_post():
    """ Publish the post by changing the status """
    path = request.args.get('path', None)
    if path not in current_repo:
        return json.dumps({'msg': "Unable to retrieve post with path = {}!".format(path), 'success': False})
    current_repo.publish(path)

    update_index()
    return 'OK'


@blueprint.route('/unpublish_post', methods=['GET', 'POST'])
@PageView.logged
def unpublish_post():
    """ Unpublish the post """
    path = request.args.get('path', None)
    if path not in current_repo:
        return json.dumps({'msg': "Unable to retrieve post with path = {}!".format(path), 'success': False})
    current_repo.unpublish(path)

    update_index()
    return 'OK'


@blueprint.route('/accept_post', methods=['POST'])
@PageView.logged
def accept():
    """ Accept the post """
    path = request.args.get('path', None)
    if path not in current_repo:
        return json.dumps({'msg': "Unable to retrieve post with path = {}!".format(path), 'success': False})
    current_repo.accept(path)
    update_index()
    return 'OK'


@blueprint.route('/delete_post', methods=['GET'])
@PageView.logged
def delete_post():
    """ Delete a post """
    path = request.args.get('path', None)
    if path not in current_repo:
        return json.dumps({'msg': "Unable to retrieve post with path = {}!".format(path), 'success': False})
    kp = current_repo.post(path)
    if g.user.username not in kp.headers['authors']:
        return json.dumps({'msg': "You can only delete a post where you are an author!", 'success': False})
    current_repo.remove(path)

    update_index()
    return 'OK'


@blueprint.route('/review', methods=['POST'])
@PageView.logged
def review_comment():
    """ Saves a review and sends an email that the post has been reviewed to the author of the post """
    path = request.args.get('path', None)
    post_id = db_session.query(Post).filter(Post.path == path).first().id

    comment = Comment()
    comment.text = request.get_json()['text']
    comment.user_id = g.user.id
    comment.post_id = post_id
    comment.type = "review"
    db_session.add(comment)
    db_session.commit()

    send_review_email(path=path,
                      commenter=g.user.username,
                      comment_text=comment.text)


@blueprint.route('/delete_review', methods=['GET', 'POST'])
@PageView.logged
def delete_review():
    """ Delete a review """
    comment = Comment.query.get(int(request.args.get('comment_id', '')))
    if comment and g.user.id == comment.user_id:
        db_session.delete(comment)
        db_session.commit()
    return 'OK'


# DEPRECATED
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
