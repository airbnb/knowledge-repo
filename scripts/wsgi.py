from knowledge_repo.app.deploy import KnowledgeDeployer, get_app_builder

boilerplate_KR = dict({'dum':'../knowledge_repo/kr'})
config_file = "../knowledge_repo/app/config_defaults.py"
workers = 2
port = 7000
timeout = 10



if __name__=="__init__":
    app_builder = get_app_builder(boilerplate_KR,
                                  debug=False,
                                  config=config_file)

    server = KnowledgeDeployer.using(args.engine)(
        app_builder,
        host='0.0.0.0',
        port=port,
        workers=workers,
        timeout=timeout
    )
    server.run()

