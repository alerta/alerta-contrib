
import logging
import os
import socket

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase


LOG = logging.getLogger('alerta.plugins.logstash')

DEFAULT_LOGSTASH_HOST = 'localhost'
DEFAULT_LOGSTASH_PORT = 6379

LOGSTASH_HOST = os.environ.get('LOGSTASH_HOST') or app.config.get('LOGSTASH_HOST', DEFAULT_LOGSTASH_HOST)
LOGSTASH_PORT = os.environ.get('LOGSTASH_PORT') or app.config.get('LOGSTASH_PORT', DEFAULT_LOGSTASH_PORT)


class LogStashOutput(PluginBase):

    def __init__(self, name=None):
        self.sock = None
        super(LogStashOutput, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((LOGSTASH_HOST, LOGSTASH_PORT))
        except Exception as e:
            raise RuntimeError("Logstash TCP connection error: %s" % str(e))

        try:
            self.sock.send("%s\r\n" % alert)
        except Exception as e:
            LOG.exception(e)
            raise RuntimeError("logstash exception")

        self.sock.close()

    def status_change(self, alert, status, text):
        return
