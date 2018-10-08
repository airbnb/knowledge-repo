from .common import KnowledgeDeployer


class FlaskDeployer(KnowledgeDeployer):

    _registry_keys = ['flask']

    def run(self, **kwargs):
        self.app.start_indexing()
        return self.app.run(
            debug=self.app.config['DEBUG'],
            host=self.host,
            port=self.port,
            threaded=self.app.check_thread_support(),
            **kwargs
        )
