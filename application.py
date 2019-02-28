import os,sys


script_dir = os.path.dirname(__file__)
if os.path.exists(os.path.join(os.path.dirname(script_dir), 'knowledge_repo', '__init__.py')):
    sys.path.insert(0, os.path.join(script_dir, '.'))

import knowledge_repo  
from knowledge_repo.repositories.gitrepository import GitKnowledgeRepository  # nopep8
from knowledge_repo.app.deploy import KnowledgeDeployer, get_app_builder

KR_REPO_DB_URI = os.environ['KR_REPO_DB_URI']
KR_REPO_DB_USER = os.environ['KR_REPO_DB_USER']
KR_REPO_DB_PWD = os.environ['KR_REPO_DB_PWD']
KR_REPO_DB_PORT = os.environ['KR_REPO_DB_PORT']
KR_APP_DB_URI = os.environ['KR_APP_DB_URI']

config_file = "app_config.py"
workers = 2
port = 5000
timeout = 1000

repo_db_conn = u'mysql+mysqlconnector://%s:%s@%s:%s/knowledgerepo'%(KR_REPO_DB_USER,KR_REPO_DB_PWD,KR_REPO_DB_URI,KR_REPO_DB_PORT)

boilerplate_KR = dict({"webpost":"%s:webposts"%repo_db_conn,"webpost2":"%s:webposts2"%repo_db_conn})
app_builder = get_app_builder(boilerplate_KR,
                                  db_uri=KR_APP_DB_URI,
                                  debug=True,
                                  config=config_file)

application = KnowledgeDeployer.using('flask')(
        app_builder,
        host='0.0.0.0',
        port=port,
        workers=workers,
        timeout=timeout).app


if __name__=="__main__":
    application.run()

