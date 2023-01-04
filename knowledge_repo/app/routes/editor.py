from .. import permissions
from ..index import update_index
from ..models import Comment, PageView, Post, PostAuthorAssoc
from ..proxies import current_repo, current_user, db_session
from ..utils.emails import (
    send_review_email,
    send_reviewer_request_email,
)
from ..utils.image import (
    is_allowed_image_format,
    is_pdf,
    pdf_page_to_png,
)
from ..utils.shared import get_blueprint
from datetime import datetime
from flask import (
    current_app,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from knowledge_repo.post import KnowledgePost
from sqlalchemy import or_
from urllib.parse import unquote
from werkzeug.utils import secure_filename
import json
import logging
import os
from knowledge_repo.utils.s3 import get_s3_client, put_object_to_s3
import nbformat
from nbconvert import HTMLExporter
import io
from knowledge_repo.constants import AWS_S3_BUCKET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blueprint = get_blueprint("editor", __name__)
s3_client = get_s3_client("", "", "us-west-2")


def get_warning_msg(msg):
    return json.dumps({"msg": msg, "success": False})


def get_error_msg(msg):
    return json.dumps({"error_msg": msg, "success": False})


# TODO: These functions have not been fully married
# to the KnowledgePost API
# Currently, backended by Post objects but partially
# implemented on KnowledgePost API


# TODO: Deprecate this route in favour of integrating editing
# links into primary index pages and user pages
@blueprint.route("/webposts", methods=["GET"])
@PageView.logged
@permissions.post_edit.require()
def gitless_drafts():
    """Render the gitless posts that a user has created in table form
    Editors can see all the posts created via Gitless_Editing
    """
    prefixes = current_app.config.get("WEB_EDITOR_PREFIXES", [])
    if prefixes == []:
        raise Exception("Web editing is not configured")

    query = db_session.query(Post)
    if prefixes is not None:
        query = query.filter(or_(*[Post.path.like(p + "%") for p in prefixes]))

    if current_user.identifier not in current_repo.config.editors:
        query = query.outerjoin(
            PostAuthorAssoc, PostAuthorAssoc.post_id == Post.id
        ).filter(PostAuthorAssoc.user_id == current_user.id)

    return render_template("web_posts.html", posts=query.all())


@blueprint.route("/edit")
@blueprint.route("/edit/<path:path>", methods=["GET", "POST"])
@PageView.logged
@permissions.post_edit.require()
def editor(path=None):
    """Render the web post editor, either with the default values
    or if the post already exists, with what has been saved"""

    prefixes = current_app.config.get("WEB_EDITOR_PREFIXES", None)

    if prefixes is not None:
        assert path is None or any(
            path.startswith(prefix) for prefix in prefixes
        ), "Editing this post online is not permitted by server configuration."

    # set defaults
    data = {
        "title": None,
        "status": current_repo.PostStatus.DRAFT.value,
        "markdown": request.args.get("markdown"),
        "thumbnail": "",
        "can_approve": 0,
        "username": current_user.identifier,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "authors": [current_user.identifier],
        "comments": [],
        "tldr": request.args.get("tldr"),
    }

    if path is not None and path in current_repo:
        kp = current_repo.post(path)
        data.update(kp.headers)

        data["status"] = kp.status.value
        data["path"] = path
        data["markdown"] = kp.read(images=False, headers=False)

        # retrieve reviews
        post = db_session.query(Post).filter(Post.path == path).first()
        if post:  # post may have not been indexed yet
            data["comments"] = (
                db_session.query(Comment)
                .filter(Comment.post_id == post.id)
                .filter(Comment.type == "review")
                .all()
            )

    if (
        current_user.identifier not in data["authors"] or
        current_user.identifier in current_repo.config.editors
    ):
        data["can_approve"] = 1

    data["created_at"] = data["created_at"]
    data["updated_at"] = data["updated_at"]
    data["authors"] = json.dumps(data.get("authors"))
    data["tags"] = json.dumps(data.get("tags", []))
    logger.info(data)

    if "proxy" in data or request.args.get("proxy", False):
        return render_template("post_editor_proxy.html", **data)
    if "ipynb" in data or request.args.get("ipynb", False):
        data["ipynb"] = True
        return render_template("post_editor_ipynb.html", **data)
    return render_template("post_editor_markdown.html", **data)


@blueprint.route("/ajax/editor/save", methods=["GET", "POST"])
@PageView.logged
@permissions.post_edit.require()
def save_post():
    """Save the post"""

    data = request.get_json()
    path = data["path"]

    prefixes = current_app.config["WEB_EDITOR_PREFIXES"]
    if prefixes == []:
        raise Exception("Web editing is not configured")

    if prefixes is not None:
        if not any([path.startswith(prefix) for prefix in prefixes]):
            return get_warning_msg(f"Your post path must begin with one of {prefixes}")

    # TODO better handling of overwriting
    kp = None
    if path in current_repo:
        kp = current_repo.post(path)
        if (
            current_user.identifier not in kp.headers["authors"] and
            current_user.identifier not in current_repo.config.editors
        ):
            return get_warning_msg(
                f"Post with path {path} already exists and you are not "
                "an author!\nPlease try a different path"
            )

    # create the knowledge post
    kp = kp or KnowledgePost(path=path)

    headers = {}
    headers["created_at"] = datetime.strptime(data["created_at"], "%Y-%m-%d").date()
    headers["updated_at"] = datetime.strptime(data["updated_at"], "%Y-%m-%d").date()
    headers["title"] = data["title"]
    headers["path"] = data["path"]
    # TODO: thumbnail header not working currently, as feed image set
    # with kp method not based on header
    headers["thumbnail"] = data.get("feed_image", "")
    headers["authors"] = [auth.strip() for auth in data["author"]]
    headers["tldr"] = data["tldr"]
    headers["tags"] = [tag.strip() for tag in data.get("tags", [])]
    if "proxy" in data:
        headers["proxy"] = data["proxy"]
    if "ipynb" in data:
        headers["ipynb"] = data["ipynb"]
        if (
            data.get("file_name", None) is not None and
            data.get("file_data", None) is not None
        ):
            response = s3_upload(data["file_name"], data["file_data"])
            if response is None:
                error_msg = "ERROR during upload file to s3"
                logger.error(error_msg)
                return get_error_msg(error_msg)
            else:
                headers["display_link"] = response
        else:
            headers["display_link"] = data["display_link"]

    kp.write(unquote(data["markdown"]), headers=headers)
    # add to repo
    current_repo.add(kp, update=True, message=headers["title"])  # THIS IS DANGEROUS

    update_index()
    return json.dumps({"path": path})


@blueprint.route("/ajax/editor/submit", methods=["GET", "POST"])
@PageView.logged
@permissions.post_edit.require()
def submit_for_review():
    """Submit post and if there are reviewers assigned, email them"""
    path = request.args.get("path", None)
    data = request.get_json()
    current_repo.submit(path)

    # email the reviewers
    reviewers = data.get("post_reviewers", None)
    if reviewers:
        for r in reviewers.split(","):
            send_reviewer_request_email(path=path, reviewer=r)

    update_index()
    return "OK"


@blueprint.route("/ajax/editor/publish", methods=["GET", "POST"])
@PageView.logged
@permissions.post_edit.require()
def publish_post():
    """Publish the post by changing the status"""
    path = request.args.get("path", None)
    if path not in current_repo:
        return get_warning_msg(f"Unable to retrieve post with path = {path}!")
    current_repo.publish(path)

    update_index(check_timeouts=False)
    return "OK"


@blueprint.route("/ajax/editor/unpublish", methods=["GET", "POST"])
@PageView.logged
@permissions.post_edit.require()
def unpublish_post():
    """Unpublish the post"""
    path = request.args.get("path", None)
    if path not in current_repo:
        return get_warning_msg(f"Unable to retrieve post with path = {path}!")
    current_repo.unpublish(path)

    update_index(check_timeouts=False)
    return "OK"


@blueprint.route("/ajax/editor/accept", methods=["GET", "POST"])
@PageView.logged
@permissions.post_edit.require()
def accept():
    """Accept the post"""
    path = request.args.get("path", None)
    if path not in current_repo:
        return get_warning_msg(f"Unable to retrieve post with path = {path}!")
    current_repo.accept(path)
    update_index()
    return "OK"


@blueprint.route("/ajax/editor/delete", methods=["GET", "POST"])
@PageView.logged
@permissions.post_edit.require()
def delete_post():
    """Delete a post"""
    path = request.args.get("path", None)
    if path not in current_repo:
        return get_warning_msg(f"Unable to retrieve post with path = {path}!")
    kp = current_repo.post(path)
    if current_user.identifier not in kp.headers["authors"]:
        return get_warning_msg("You can only delete a post where you are an author!")
    current_repo.remove(path)

    update_index(check_timeouts=False)
    return "OK"


@blueprint.route("/ajax/editor/review", methods=["POST", "DELETE"])
@PageView.logged
@permissions.post_edit.require()
def review_comment():
    """
    Saves a review and sends an email that the post has been reviewed to
    the author of the post or deletes a submitted review
    """

    if request.method == "POST":
        path = request.args.get("path", None)
        post_id = db_session.query(Post).filter(Post.path == path).first().id

        comment = Comment()
        comment.text = request.get_json()["text"]
        comment.user_id = current_user.id
        comment.post_id = post_id
        comment.type = "review"
        db_session.add(comment)
        db_session.commit()

        send_review_email(
            path=path, commenter=current_user.identifier, comment_text=comment.text
        )

    elif request.method == "DELETE":
        comment = Comment.query.get(int(request.args.get("comment_id", "")))
        if comment and current_user.id == comment.user_id:
            db_session.delete(comment)
            db_session.commit()

    return "OK"


def s3_upload(file_name, file_data):
    """Upload file(s) to AWS s3 path and return the display link in the response"""

    if file_name is None or file_data is None or file_data is "":
        return get_warning_msg(f"File name is empty. Please re-upload!")

    response = put_object_to_s3(s3_client, file_data, AWS_S3_BUCKET, file_name)

    # create a html version of this file
    if ".ipynb" in file_name:
        with io.StringIO(file_data) as f:
            nb = nbformat.read(f, as_version=4)

            # export to html
            html_exporter = HTMLExporter()
            (html_data, resources) = html_exporter.from_notebook_node(nb)

            html_file_name = file_name.replace(".ipynb", ".html")
            response = put_object_to_s3(
                s3_client,
                html_data,
                AWS_S3_BUCKET,
                html_file_name,
                "text/html",
            )

            if response:
                display_link = "https://s3.us-west-2.amazonaws.com/{0}/{1}".format(
                    AWS_S3_BUCKET, html_file_name
                )  # todo: make s3 region name be configurable
                return display_link
    return None


# DEPRECATED
@blueprint.route("/file_upload", methods=["POST", "GET"])
@PageView.logged
@permissions.post_edit.require()
def file_upload():
    """
    Uploads images dropped on the web editor's markdown box to
    static/images and notifies editors by email
    """
    upload_folder = "images"
    title = request.form["title"]
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
                    uploadedFiles += [
                        url_for(
                            "static", filename=os.path.join(upload_folder, filename)
                        )
                    ]
                except Exception as e:
                    error_msg = f"ERROR during image upload: {e}"
                    logger.error(error_msg)
                    return get_error_msg(error_msg)

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
                        uploadedFiles += [
                            url_for(
                                "static",
                                filename=os.path.join(upload_folder, page_name),
                            )
                        ]
                except Exception as e:
                    error_msg = f"ERROR during pdf upload: {e}"
                    logger.error(error_msg)
                    return get_error_msg(error_msg)

    return json.dumps({"links": uploadedFiles, "success": True})
