import os,sys
script_dir = os.path.dirname(__file__)
if os.path.exists(os.path.join(os.path.dirname(script_dir), 'knowledge_repo', '__init__.py')):
    sys.path.insert(0, os.path.join(script_dir, '..'))

from knowledge_repo.app.deploy import KnowledgeDeployer, get_app_builder

boilerplate_KR = dict({'dum':'../knowledge_repo/kr'})
config_file = "../knowledge_repo/app/config_defaults.py"
workers = 2
port = 80
timeout = 10

app_builder = get_app_builder(boilerplate_KR,
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

