import json
import logging
import os
import socket

from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0


LOG = logging.getLogger('alerta.plugins.logstash')

DEFAULT_LOGSTASH_HOST = 'localhost'
DEFAULT_LOGSTASH_PORT = 6379

LOGSTASH_HOST = os.environ.get('LOGSTASH_HOST') or app.config.get(
    'LOGSTASH_HOST', DEFAULT_LOGSTASH_HOST)
LOGSTASH_PORT = os.environ.get('LOGSTASH_PORT') or app.config.get(
    'LOGSTASH_PORT', DEFAULT_LOGSTASH_PORT)


class LogStashOutput(PluginBase):

    def __init__(self, name=None):
        self.sock = None
        super().__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        try:
            logstash_port = int(LOGSTASH_PORT)
        except Exception as e:
            LOG.error("Alerta_logstash: Could not parse 'LOGSTASH_PORT': %s", e)
            raise RuntimeError("Could not parse 'LOGSTASH_PORT': %s" % e)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((LOGSTASH_HOST, logstash_port))
        except Exception as e:
            raise RuntimeError('Logstash TCP connection error: %s' % str(e))

        try:
            self.sock.send(b'%s\r\n' % json.dumps(
                alert.get_body(history=False)).encode('utf-8'))
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError('logstash exception')

        self.sock.close()

    def status_change(self, alert, status, text):
        return
