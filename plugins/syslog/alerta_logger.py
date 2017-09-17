
import logging
import os
import sys
from logging.handlers import SysLogHandler

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.logger')

DEFAULT_SYSLOG_FORMAT = '%(name)s[%(process)d]: %(levelname)s - %(message)s'
DEFAULT_SYSLOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_SYSLOG_FACILITY = 'local7'

LOGGER_SYSLOG_FORMAT = os.environ.get('LOGGER_SYSLOG_FORMAT') or app.config.get('SYSLOG_FORMAT', DEFAULT_SYSLOG_FORMAT)
LOGGER_SYSLOG_DATE_FORMAT = os.environ.get('LOGGER_SYSLOG_DATE_FORMAT') or app.config.get('SYSLOG_DATE_FORMAT', DEFAULT_SYSLOG_DATE_FORMAT)
LOGGER_SYSLOG_FACILITY = os.environ.get('LOGGER_SYSLOG_FACILITY') or app.config.get('SYSLOG_FACILITY', DEFAULT_SYSLOG_FACILITY)


class Syslog(PluginBase):

    def __init__(self, name=None):

        self.logger = logging.getLogger(name)

        if sys.platform == "darwin":
            socket = '/var/run/syslog'
        else:
            socket = '/dev/log'
        facility = LOGGER_SYSLOG_FACILITY

        syslog = SysLogHandler(address=socket, facility=facility)
        syslog.setFormatter(logging.Formatter(fmt=LOGGER_SYSLOG_FORMAT, datefmt=LOGGER_SYSLOG_DATE_FORMAT))
        self.logger.addHandler(syslog)

        super(Syslog, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        if alert.severity == 'critical':
            level = logging.CRITICAL
        elif alert.severity in ['major', 'minor']:
            level = logging.ERROR
        elif alert.severity == 'warning':
            level = logging.WARNING
        else:
            level = logging.INFO

        self.logger.log(level=level, msg=alert)

    def status_change(self, alert, status, text):
        pass
