import os
import subprocess
import logging
import shutil

from .common import KnowledgeDeployer

logger = logging.getLogger()


class uWSGIDeployer(KnowledgeDeployer):

    _registry_keys = ['uwsgi']

    COMMAND = "uwsgi --http {socket} --plugin python --wsgi-file {path} --callable app --master --processes {processes} --threads {threads} --uid --gid"

    def run(self):
        if not self.app.supports_threads:
            raise RuntimeError("Database configuration is not suitable for deployment (not thread-safe).")

        tmp_dir = self.write_temp_files()

        config = {
            'socket': '{}:{}'.format(self.host, self.port),
            'processes': self.workers,
            'threads': 2,
            'timeout': self.timeout,
            'path': os.path.join(tmp_dir, 'server.py')
        }

        try:
            cmd = "cd {};".format(tmp_dir) + self.COMMAND.format(**config)
            logger.info("Starting server with command:  " + " ".join(cmd))
            subprocess.check_output(cmd, shell=True)
        finally:
            shutil.rmtree(tmp_dir)
