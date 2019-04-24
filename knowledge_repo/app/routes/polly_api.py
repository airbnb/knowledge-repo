"""
APIs for polly and their routes
Includes:
    - /api/uploadkr
    - /api/uploadpost
    - /api/uploadpage

"""

import os
import json
from builtins import str
from collections import namedtuple
from flask import request, render_template, redirect, Blueprint, current_app, make_response,jsonify,url_for
from flask_login import login_required
from sqlalchemy import case, desc
from sqlalchemy.exc import IntegrityError
from werkzeug import secure_filename
from .. import permissions
from ..proxies import db_session, current_repo
from ..utils.posts import get_posts
from ..models import Post, Tag, User, PageView
from ..utils.requests import from_request_get_feed_params
from ..utils.render import render_post_tldr
from ..utils.s3_talk import download_dir,download_from_s3  
from ..index import update_index, update_index_for_post
blueprint = Blueprint('api', __name__, template_folder='../templates', static_folder='../static')




def publish_post_db(kp,path):
    if not kp.is_valid():
        print("KP was invalid")
        return

    print("Checking the DB for this:",path)
    post = (db_session.query(Post).filter(Post.path==path).first())
    if not post:
        print(u'creating new post from path {}'.format(kp.path))
        post = Post()
        db_session.add(post)
        db_session.commit()
        db_session.flush()  # (matthew) Fix groups logic so this is not necessary
    try:
        post.update_metadata_from_kp(kp)
        print("After update:", post.path)
    except IntegrityError:
        import uuid
        db_session.rollback()
        print("from the caller:",kp.path)
        kp.uuid = str(uuid.uuid4())
        post.update_metadata_from_kp(kp)
        print("After update:", post.path)
    db_session.commit()
    db_session.flush()

        # Record revision
#    for uri, revision in current_repo.revisions.items():
#        IndexMetadata.set('repository_revision', uri, str(revision))

<<<<<<< HEAD
def prep_kr_path(path,dir_name):
    path_parts = path.split('/')
    if path_parts[0] != dir_name:
        path = dir_name + '/' + path
    if not path.endswith('.kp'):
        path = path + '.kp'
    return path

def prep_post_path(path):
    if not path.endswith('.kp'):
        path = path + '.kp'
    return path
=======


>>>>>>> working setup
@blueprint.route('/api/uploadpage')
@PageView.logged
def upload_post_page(): 
    try:
        kr_list = current_app.get_kr_list()
    except ValueError:
        return redirect("https://%s/?next=%s"%(request.host,request.full_path))
    return render_template('upload_page.html',krs = kr_list)

@blueprint.route('/api/uploadpost',methods=['POST'])
def upload_post():
    # Access the file
    #TODO: Put everything in try catch
    tempfile = request.files['file']
    temp_path = os.path.join('/tmp',secure_filename(tempfile.filename))
    tempfile.save(temp_path)
    repo = request.form.get('repo')
    path = repo + '/' + request.form.get('path')
    # Just post the post to the path
    try:
        new_post = current_repo.upload_post(temp_path,path)
    #    update_index_for_post(new_post,path)
<<<<<<< HEAD
        path = prep_post_path(path)
=======
>>>>>>> working setup
        publish_post_db(new_post,path)
    except:
        return render_template("error.html")
    return redirect(url_for('posts.render',path=path+".kp"))

@blueprint.route('/api/uploadkr')
@PageView.logged
def upload_kr():
    """
    API to upload a KR to the server
    args:
        S3-Path 
    """
    import shutil
    global current_repo,current_app
    from ...repositories.meta import MetaKnowledgeRepository
    path = request.args.get('path')
    dir_name,dir_path = download_dir(path)
    error = 200
    try:
        db_path = current_app.config['KR_REPO_DB_PATH'] + ':' + dir_name
        dbobj  = current_repo.migrate_to_dbrepo(dir_path,db_path)
        current_app.append_repo_obj(dir_name,dbobj)
        temp_kr = MetaKnowledgeRepository({dir_name:dbobj})
        for post in temp_kr.posts():
<<<<<<< HEAD
            post_path = prep_kr_path(post.path,dir_name)
            publish_post_db(post,post_path)
            print("Tried pushing:",post_path)
=======
            publish_post_db(post,post.path)
        #current_app.db_update_index(check_timeouts=False,force=True)
>>>>>>> working setup
    except:
    #TODO: do more precise exception handling
        error = 400
    shutil.rmtree(dir_path)
    return jsonify({
                'statusCode': '400' if error==400 else '200',
                'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                            },
                   })

