
import os
import sys
import datetime
import logging
import re


from alertaclient.api import ApiClient
from alertaclient.alert import Alert
from alertaclient.heartbeat import Heartbeat

__version__ = '3.3.1'


LOG = logging.getLogger("alerta.snmptrap")
logging.basicConfig(format="%(asctime)s - %(name)s: %(levelname)s - %(message)s", level=logging.DEBUG)


class SnmpTrapHandler(object):

    def __init__(self):

        self.api = None

    def run(self):

        endpoint = os.environ.get('ALERTA_ENDPOINT', 'http://localhost:8080')
        key = os.environ.get('ALERTA_API_KEY', None)

        self.api = ApiClient(endpoint=endpoint, key=key)

        data = sys.stdin.read()
        LOG.info('snmptrapd -> %r', data)
        data = unicode(data, 'utf-8', errors='ignore')
        LOG.debug('unicoded -> %s', data)

        snmptrapAlert = SnmpTrapHandler.parse_snmptrap(data)

        if snmptrapAlert:
            try:
                self.api.send(snmptrapAlert)
            except Exception, e:
                LOG.warning('Failed to send alert: %s', e)

        LOG.debug('Send heartbeat...')
        heartbeat = Heartbeat(tags=[__version__])
        try:
            self.api.send(heartbeat)
        except Exception, e:
            LOG.warning('Failed to send heartbeat: %s', e)

    @staticmethod
    def parse_snmptrap(data):

        pdu_data = data.splitlines()
        varbind_list = pdu_data[:]

        trapvars = dict()
        for line in pdu_data:
            if line.startswith('$'):
                special, value = line.split(None, 1)
                trapvars[special] = value
                varbind_list.pop(0)

        if '$s' in trapvars:
            if trapvars['$s'] == '0':
                trap_version = 'SNMPv1'
            elif trapvars['$s'] == '1':
                trap_version = 'SNMPv2c'
            elif trapvars['$s'] == '2':
                trap_version = 'SNMPv2u'  # not supported
            else:
                trap_version = 'SNMPv3'
            trapvars['$s'] = trap_version
        else:
            LOG.warning('Failed to parse unknown trap type.')
            return

        # Get varbinds
        varbinds = dict()
        idx = 0
        for varbind in '\n'.join(varbind_list).split('~%~'):
            if varbind == '':
                break
            idx += 1
            try:
                oid, value = varbind.split(None, 1)
            except ValueError:
                oid = varbind
                value = ''
            varbinds[oid] = value
            trapvars['$' + str(idx)] = value  # $n
            LOG.debug('$%s %s', str(idx), value)

        trapvars['$q'] = trapvars['$q'].lstrip('.')  # if numeric, remove leading '.'
        trapvars['$#'] = str(idx)

        LOG.debug('varbinds = %s', varbinds)

        correlate = list()

        if trap_version == 'SNMPv1':
            if trapvars['$w'] == '0':
                trapvars['$O'] = 'coldStart'
                correlate = ['coldStart', 'warmStart']
            elif trapvars['$w'] == '1':
                trapvars['$O'] = 'warmStart'
                correlate = ['coldStart', 'warmStart']
            elif trapvars['$w'] == '2':
                trapvars['$O'] = 'linkDown'
                correlate = ['linkUp', 'linkDown']
            elif trapvars['$w'] == '3':
                trapvars['$O'] = 'linkUp'
                correlate = ['linkUp', 'linkDown']
            elif trapvars['$w'] == '4':
                trapvars['$O'] = 'authenticationFailure'
            elif trapvars['$w'] == '5':
                trapvars['$O'] = 'egpNeighborLoss'
            elif trapvars['$w'] == '6':  # enterpriseSpecific(6)
                if trapvars['$q'].isdigit():  # XXX - specific trap number was not decoded
                    trapvars['$O'] = '%s.0.%s' % (trapvars['$N'], trapvars['$q'])
                else:
                    trapvars['$O'] = trapvars['$q']

        elif trap_version == 'SNMPv2c':
            if 'coldStart' in trapvars['$2']:
                trapvars['$w'] = '0'
                trapvars['$W'] = 'Cold Start'
            elif 'warmStart' in trapvars['$2']:
                trapvars['$w'] = '1'
                trapvars['$W'] = 'Warm Start'
            elif 'linkDown' in trapvars['$2']:
                trapvars['$w'] = '2'
                trapvars['$W'] = 'Link Down'
            elif 'linkUp' in trapvars['$2']:
                trapvars['$w'] = '3'
                trapvars['$W'] = 'Link Up'
            elif 'authenticationFailure' in trapvars['$2']:
                trapvars['$w'] = '4'
                trapvars['$W'] = 'Authentication Failure'
            elif 'egpNeighborLoss' in trapvars['$2']:
                trapvars['$w'] = '5'
                trapvars['$W'] = 'EGP Neighbor Loss'
            else:
                trapvars['$w'] = '6'
                trapvars['$W'] = 'Enterprise Specific'
            trapvars['$O'] = trapvars['$2']  # SNMPv2-MIB::snmpTrapOID.0
        LOG.debug('trapvars = %s', trapvars)

        LOG.info('%s-Trap-PDU %s from %s at %s %s', trap_version, trapvars['$O'], trapvars['$B'], trapvars['$x'], trapvars['$X'])

        if trapvars['$B'] != '<UNKNOWN>':
            resource = trapvars['$B']
        elif trapvars['$A'] != '0.0.0.0':
            resource = trapvars['$A']
        else:
            m = re.match(r'UDP: \[(\d+\.\d+\.\d+\.\d+)\]', trapvars['$b'])
            if m:
                resource = m.group(1)
            else:
                resource = '<NONE>'

        snmptrapAlert = Alert(
            resource=resource,
            event=trapvars['$O'],
            correlate=correlate,
            group='SNMP',
            value=trapvars['$w'],
            severity='indeterminate',
            environment='Production',
            service=['Network'],
            text=trapvars['$W'],
            event_type='snmptrapAlert',
            attributes={'trapvars': {k.replace('$','_'):v for k,v in trapvars.iteritems()}},
            tags=[trap_version],
            create_time=datetime.datetime.strptime('%sT%s.000Z' % (trapvars['$x'], trapvars['$X']), '%Y-%m-%dT%H:%M:%S.%fZ'),
            raw_data=data
        )

        if snmptrapAlert.get_type() == 'Heartbeat':
            snmptrapAlert = Heartbeat(origin=snmptrapAlert.origin, tags=[__version__])

        return snmptrapAlert

def main():

    LOG = logging.getLogger("alerta.snmptrap")

    try:
        SnmpTrapHandler().run()
    except (SystemExit, KeyboardInterrupt):
        LOG.info("Exiting alerta SNMP trapper.")
        sys.exit(0)
    except Exception as e:
        LOG.error(e, exc_info=1)
        sys.exit(1)

if __name__ == '__main__':
    main()