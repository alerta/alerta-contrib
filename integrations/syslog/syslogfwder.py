
import os
import sys
import platform
import socket
import select
import re
import logging

from alertaclient.api import Client


__version__ = '3.5.0'

SYSLOG_TCP_PORT = int(os.environ.get('SYSLOG_TCP_PORT', 514))
SYSLOG_UDP_PORT = int(os.environ.get('SYSLOG_UDP_PORT', 514))


SYSLOG_FACILITY_NAMES = [
    "kern",
    "user",
    "mail",
    "daemon",
    "auth",
    "syslog",
    "lpr",
    "news",
    "uucp",
    "cron",
    "authpriv",
    "ftp",
    "ntp",
    "audit",
    "alert",
    "clock",
    "local0",
    "local1",
    "local2",
    "local3",
    "local4",
    "local5",
    "local6",
    "local7"
]

SYSLOG_SEVERITY_NAMES = [
    "emerg",
    "alert",
    "crit",
    "err",
    "warning",
    "notice",
    "info",
    "debug"
]

SYSLOG_SEVERITY_MAP = {
    "emerg":   "critical",
    "alert":   "critical",
    "crit":    "major",
    "err":     "minor",
    "warning": "warning",
    "notice":  "normal",
    "info":    "informational",
    "debug":   "debug",
}

def priority_to_code(name):
    return SYSLOG_SEVERITY_MAP.get(name, "unknown")


def decode_priority(priority):
    facility = priority >> 3
    level = priority & 7
    return SYSLOG_FACILITY_NAMES[facility], SYSLOG_SEVERITY_NAMES[level]

LOOP_EVERY = 20  # seconds

LOG = logging.getLogger("alerta.syslog")
logging.basicConfig(format="%(asctime)s - %(name)s: %(levelname)s - %(message)s", level=logging.DEBUG)


class SyslogDaemon(object):

    def __init__(self):

        self.api = Client()

        LOG.info('Starting UDP listener...')
        # Set up syslog UDP listener
        try:
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp.bind(('', SYSLOG_UDP_PORT))
        except socket.error as e:
            LOG.error('Syslog UDP error: %s', e)
            sys.exit(2)
        LOG.info('Listening on syslog port %s/udp' % SYSLOG_UDP_PORT)

        LOG.info('Starting TCP listener...')
        # Set up syslog TCP listener
        try:
            self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp.bind(('', SYSLOG_TCP_PORT))
            self.tcp.listen(5)
        except socket.error as e:
            LOG.error('Syslog TCP error: %s', e)
            sys.exit(2)
        LOG.info('Listening on syslog port %s/tcp' % SYSLOG_TCP_PORT)

        self.shuttingdown = False

    def run(self):

        count = 0
        while not self.shuttingdown:
            try:
                LOG.debug('Waiting for syslog messages...')
                ip, op, rdy = select.select([self.udp, self.tcp], [], [], LOOP_EVERY)
                if ip:
                    for i in ip:
                        if i == self.udp:
                            data, addr = self.udp.recvfrom(4096)
                            data = unicode(data, 'utf-8', errors='ignore')
                            LOG.debug('Syslog UDP data received from %s: %s', addr, data)
                        if i == self.tcp:
                            client, addr = self.tcp.accept()
                            data = client.recv(4096)
                            data = unicode(data, 'utf-8', errors='ignore')
                            client.close()
                            LOG.debug('Syslog TCP data received from %s: %s', addr, data)

                        alerts = self.parse_syslog(ip=addr[0], data=data)
                        for alert in alerts:
                            try:
                                self.api.send_alert(**alert)
                            except Exception as e:
                                LOG.warning('Failed to send alert: %s', e)

                    count += 1
                if not ip or count % 5 == 0:
                    LOG.debug('Send heartbeat...')
                    try:
                        origin = '{}/{}'.format('syslog', platform.uname()[1])
                        self.api.heartbeat(origin, tags=[__version__])
                    except Exception as e:
                        LOG.warning('Failed to send heartbeat: %s', e)

            except (KeyboardInterrupt, SystemExit):
                self.shuttingdown = True

        LOG.info('Shutdown request received...')

    def parse_syslog(self, ip, data):

        LOG.debug('Parsing syslog message...')
        syslogAlerts = list()

        event = None
        resource = None

        for msg in data.split('\n'):
            if not msg or 'last message repeated' in msg:
                continue

            if re.match('<\d+>1', msg):
                # Parse RFC 5424 compliant message
                m = re.match(r'<(\d+)>1 (\S+) (\S+) (\S+) (\S+) (\S+) (.*)', msg)
                if m:
                    PRI = int(m.group(1))
                    ISOTIMESTAMP = m.group(2)
                    HOSTNAME = m.group(3)
                    APPNAME = m.group(4)
                    PROCID = m.group(5)
                    MSGID = m.group(6)
                    TAG = '%s[%s] %s' % (APPNAME, PROCID, MSGID)
                    MSG = m.group(7)
                    LOG.info("Parsed RFC 5424 message OK")
                else:
                    LOG.error("Could not parse RFC 5424 syslog message: %s", msg)
                    continue

            elif re.match(r'<(\d{1,3})>\S{3}\s', msg):
                # Parse RFC 3164 compliant message
                m = re.match(r'<(\d{1,3})>\S{3}\s{1,2}\d?\d \d{2}:\d{2}:\d{2} (\S+)( (\S+):)? (.*)', msg)
                if m:
                    PRI = int(m.group(1))
                    HOSTNAME = m.group(2)
                    TAG = m.group(4)
                    MSG = m.group(5)
                    LOG.info("Parsed RFC 3164 message OK")
                else:
                    LOG.error("Could not parse RFC 3164 syslog message: %s", msg)
                    continue

            elif re.match('<\d+>.*%[A-Z0-9_-]+', msg):
                # Parse Cisco Syslog message
                m = re.match('<(\d+)>.*(%([A-Z0-9_-]+)):? (.*)', msg)
                if m:
                    LOG.debug(m.groups())
                    PRI = int(m.group(1))
                    CISCO_SYSLOG = m.group(2)
                    try:
                        CISCO_FACILITY, CISCO_SEVERITY, CISCO_MNEMONIC = m.group(3).split('-')
                    except ValueError as e:
                        LOG.error('Could not parse Cisco syslog - %s: %s', e, m.group(3))
                        CISCO_FACILITY = CISCO_SEVERITY = CISCO_MNEMONIC = 'na'

                    TAG = CISCO_MNEMONIC
                    MSG = m.group(4)

                    event = CISCO_SYSLOG

                    # replace IP address with a hostname, if necessary
                    try:
                        socket.inet_aton(ip)
                        (resource, _, _) = socket.gethostbyaddr(ip)
                    except (socket.error, socket.herror):
                        resource = ip

                    resource = '%s:%s' % (resource, CISCO_FACILITY)
                else:
                    LOG.error("Could not parse Cisco syslog message: %s", msg)
                    continue

            facility, level = decode_priority(PRI)

            # Defaults
            event = event or '%s%s' % (facility.capitalize(), level.capitalize())
            resource = resource or '%s%s' % (HOSTNAME, ':' + TAG if TAG else '')
            severity = priority_to_code(level)
            group = 'Syslog'
            value = level
            text = MSG
            environment = 'Production'
            service = ['Platform']
            tags = ['%s.%s' % (facility, level)]
            correlate = ['%s%s' % (facility.capitalize(), s.capitalize()) for s in SYSLOG_SEVERITY_NAMES]
            raw_data = msg

            syslogAlert = {
                'resource': resource,
                'event': event,
                'environment': environment,
                'severity': severity,
                'correlate':correlate,
                'service': service,
                'group': group,
                'value': value,
                'text': text,
                'tags': tags,
                'event_type': 'syslogAlert',
                'raw_data': raw_data
            }
            syslogAlerts.append(syslogAlert)

        return syslogAlerts


def main():

    LOG = logging.getLogger("alerta.syslog")

    try:
        SyslogDaemon().run()
    except (SystemExit, KeyboardInterrupt):
        LOG.info("Exiting alerta syslog.")
        sys.exit(0)
    except Exception as e:
        LOG.error(e, exc_info=1)
        sys.exit(1)

