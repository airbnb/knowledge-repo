import os
import subprocess
import logging
import shutil

from .common import KnowledgeDeployer

logger = logging.getLogger()


class uWSGIDeployer(KnowledgeDeployer):

    _registry_keys = ['uwsgi']

    COMMAND = u"uwsgi {protocol} --plugin python --wsgi-file {{path}} --callable app --master --processes {{processes}} --threads {{threads}}"

    def run(self):
        if not self.app.check_thread_support():
            raise RuntimeError("Database configuration is not suitable for deployment (not thread-safe).")

        tmp_dir = self.write_temp_files()

        options = {
            'socket': u'{}:{}'.format(self.host, self.port),
            'processes': self.workers,
            'threads': 2,
            'timeout': self.timeout,
            'path': os.path.join(tmp_dir, 'server.py'),
            'cert': self.app.config['SSL_CERT']['cert'],
            'key': self.app.config['SSL_CERT']['key']
        }

        if self.app.config['DEPLOY_HTTPS']:
            self.COMMAND = self.COMMAND.format(protocol="--https {socket},{cert},{key}")
        else:
            self.COMMAND = self.COMMAND.format(protocol="--http {socket}")

        try:
            cmd = u"cd {};".format(tmp_dir) + self.COMMAND.format(**options)
            logger.info("Starting server with command: %s", u" ".join(cmd))
            subprocess.check_output(cmd, shell=True)
        finally:
            shutil.rmtree(tmp_dir)
