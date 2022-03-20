from .common import KnowledgeDeployer
import logging
import os
import shutil
import subprocess

logger = logging.getLogger()


class uWSGIDeployer(KnowledgeDeployer):

    _registry_keys = ['uwsgi']

    COMMAND = (
        'uwsgi {protocol} --plugin python --wsgi-file {{path}} --callable app '
        '--master --processes {{processes}} --threads {{threads}}'
    )

    def run(self):
        if not self.app.check_thread_support():
            raise RuntimeError('Database configuration is not suitable '
                               'for deployment (not thread-safe).')

        tmp_dir = self.write_temp_files()

        options = {
            'socket': f'{self.host}:{self.port}',
            'processes': self.workers,
            'threads': 2,
            'timeout': self.timeout,
            'path': os.path.join(tmp_dir, 'server.py'),
            'cert': self.app.config['SSL_CERT']['cert'],
            'key': self.app.config['SSL_CERT']['key']
        }

        if self.app.config['DEPLOY_HTTPS']:
            protocol = '--https {socket},{cert},{key}'
        else:
            protocol = '--http {socket}'
        self.COMMAND = self.COMMAND.format(protocol=protocol)

        try:
            cmd = f'cd {tmp_dir};' + self.COMMAND.format(**options)
            logger.info('Starting server with command: %s', ' '.join(cmd))
            subprocess.check_output(cmd, shell=True)
        finally:
            shutil.rmtree(tmp_dir)
