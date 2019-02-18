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
from flask import request, render_template, redirect, Blueprint, current_app, make_response
from flask_login import login_required
from sqlalchemy import case, desc
from werkzeug import secure_filename
from .. import permissions
from ..proxies import db_session, current_repo
from ..utils.posts import get_posts
from ..models import Post, Tag, User, PageView
from ..utils.requests import from_request_get_feed_params
from ..utils.render import render_post_tldr
from ..utils.s3_talk import download_dir,download_from_s3  
blueprint = Blueprint('api', __name__, template_folder='../templates', static_folder='../static')

@blueprint.route('/api/uploadpage')
@PageView.logged
def upload_post_page(): 
    return render_template('upload_page.html')

@blueprint.route('/api/uploadpost',methods=['POST','GET'])
def upload_post():
    tempfile = request.files['file']
    temp_path = os.path.join('/tmp',secure_filename(tempfile.filename))
    tempfile.save(temp_path)
    path = request.form.get('path')
    
    print(request.args.keys())
    current_repo.upload_post(temp_path,path)
    current_app.db_update_index(check_timeouts=False,force=True)
    return redirect('/feed')

@blueprint.route('/api/uploadkr')
@PageView.logged
def upload_kr():
    """
    API to upload a KR to the server
    args:
        S3-Path 
    """
    global current_repo,current_app
    path = request.args.get('path')
    dir_name,dir_path = download_dir(path)
    error = 200
    try:
        db_path = current_app.config['KR_REPO_DB_PATH'] + ':' + dir_name
        dbobj  = current_repo.migrate_to_dbrepo(dir_path,db_path)
        current_repo = current_app.append_repo_obj(dir_name,dbobj)
    except:
        error = 400
    return {
                'statusCode': '400' if error==400 else '200',
                'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                            },
            }


