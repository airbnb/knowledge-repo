import os,sys
script_dir = os.path.dirname(__file__)
if os.path.exists(os.path.join(os.path.dirname(script_dir), 'knowledge_repo', '__init__.py')):
    sys.path.insert(0, os.path.join(script_dir, '..'))

from knowledge_repo.app.deploy import KnowledgeDeployer, get_app_builder

boilerplate_KR = dict({'dum':'kr'})
config_file = "config_defaults.py"
workers = 2
port = 80
timeout = 10
dburi = 'mysql://polly:password@aav7gvtlaqdl6d.cr3v4l6m6o84.ap-northeast-2.rds.amazonaws.com:3306/aav7gvtlaqdl6d'
#dburi = 'mysql://ar:ar@localhost/test_kr' 

app_builder = get_app_builder(boilerplate_KR,
                                  db_uri=dburi,
                                  debug=True,
                                  config=config_file)

application = KnowledgeDeployer.using('uwsgi')(
        app_builder,
        host='0.0.0.0',
        port=port,
        workers=workers,
        timeout=timeout
    )


if __name__=="__main__":
    application.run()

