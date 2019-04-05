# WSGI Application file for Elastic beanstalk to be able to load the KR application layer

import os,sys

# Ensuring that this is the KR script that gets called. Borrowed straight from scripts/knowledgerepo 
script_dir = os.path.dirname(__file__)
if os.path.exists(os.path.join(os.path.dirname(script_dir), 'knowledge_repo', '__init__.py')):
    sys.path.insert(0, os.path.join(script_dir, '.'))

import knowledge_repo  
from knowledge_repo.repositories.gitrepository import GitKnowledgeRepository  # nopep8
from knowledge_repo.app.deploy import KnowledgeDeployer, get_app_builder, get_polly_app_builder


# Pick major URLs/ bucket names etc from environment variables

KR_REPO_DB_URI = os.environ['KR_REPO_DB_URI']
KR_REPO_DB_USER = os.environ['KR_REPO_DB_USER']
KR_REPO_DB_PWD = os.environ['KR_REPO_DB_PWD']
KR_REPO_DB_PORT = os.environ['KR_REPO_DB_PORT']
KR_APP_DB_URI = os.environ['KR_APP_DB_URI']
KR_REPO_DB_NAME = os.environ['KR_REPO_DB_NAME']

config_file = "app_config.py" # also available in the root folder
workers = 2
port = 5000
timeout = 1000

repo_db_conn = u'mysql+mysqlconnector://%s:%s@%s:%s/%s'%(KR_REPO_DB_USER,KR_REPO_DB_PWD,KR_REPO_DB_URI,KR_REPO_DB_PORT,KR_REPO_DB_NAME)

# Pull names of all KRs that have been loaded on this server so far. If the server goes down and wants to come up, it should now load ALL the repositories that were up before it went down. 
# ToDo : this will need augmentation when GIT integration is done to do something similar for all the mounted GIT repos

from sqlalchemy import create_engine
engine = create_engine(repo_db_conn)
kr_names  = engine.table_names()
engine.dispose()


# prepare boilerplate KR object with all the table names in the DB since they represent individual KRs that were uploaded.
boilerplate_KR = {"webpost":"%s:%s"%(repo_db_conn,"webpost")}
for i in kr_names:
    boilerplate_KR[i] = "%s:%s"%(repo_db_conn,i)

# build app using KR's internal functionality
app_builder = get_app_builder(boilerplate_KR,
                                  db_uri=KR_APP_DB_URI,
                                  debug=True,
                                  config=config_file)


# Instantiate a flask application object. This handler is what will be used by EB to run. 
application = KnowledgeDeployer.using('flask')(
        app_builder,
        host='0.0.0.0',
        port=port,
        workers=workers,
        timeout=timeout).app

# This should be deprecated. Will do after testing
if __name__=="__main__":
    application.run()

