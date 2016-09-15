
import os
import sys
import logging

from logging.handlers import SysLogHandler

from alertaclient.app import app
from alertaclient.plugins import PluginBase

LOGGER_SYSLOG_FORMAT = os.environ.get('LOGGER_SYSLOG_FORMAT') or app.config.get('SYSLOG_FORMAT','%(name)s[%(process)d]: %(levelname)s - %(message)s')
LOGGER_SYSLOG_DATE_FORMAT = os.environ.get('LOGGER_SYSLOG_DATE_FORMAT') or app.config.get('SYSLOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
LOGGER_SYSLOG_FACILITY = os.environ.get('LOGGER_SYSLOG_FACILITY') or app.config.get('SYSLOG_FACILITY', 'local7')

class Syslog(PluginBase):

    def __init__(self, name=None):

        self.logger = logging.getLogger('alerta')

        if sys.platform == "darwin":
            socket = '/var/run/syslog'
        else:
            socket = '/dev/log'
        facility = LOGGER_SYSLOG_FACILITY

        syslog = SysLogHandler(address=socket, facility=facility)
        formatter = logging.Formatter(fmt=LOGGER_SYSLOG_FORMAT, datefmt=LOGGER_SYSLOG_DATE_FORMAT)
        syslog.setFormatter(formatter)
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
