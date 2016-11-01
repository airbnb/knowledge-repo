from .common import KnowledgeDeployer


class FlaskDeployer(KnowledgeDeployer):

    _registry_keys = ['flask']

    def run(self, **kwargs):
        app = self.app
        return app.run(
            debug=app.config['DEBUG'],
            host=self.host,
            port=self.port,
            threaded=app.supports_threads,
            **kwargs
        )
