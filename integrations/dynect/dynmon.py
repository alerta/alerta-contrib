
import sys
import time
import json
import logging
import ConfigParser

# https://github.com/dyninc/Dynect-API-Python-Library
from dynect.DynectDNS import DynectRest

from alerta.api import ApiClient
from alerta.alert import Alert
from alerta.heartbeat import Heartbeat

__version__ = '3.3.0'

DEBUG = False
CONF_FILE = '/etc/alerta.conf'
LOOP_EVERY = 30  # seconds

LOG = logging.getLogger("alerta.dynect")
logging.basicConfig(format="%(asctime)s - %(name)s: %(levelname)s - %(message)s", level=logging.DEBUG)


class DynectDaemon(object):

    def __init__(self):

        self.api = ApiClient()  # Set using ALERTA_ENDPOINT and ALERTA_API_KEY environment variables
        self.info = {}
        self.last_info = {}
        self.shuttingdown = False

        config = ConfigParser.RawConfigParser()
        config.read(CONF_FILE)

        try:
            self.customer = config.get('alerta-dynect', 'customer')
            self.username = config.get('alerta-dynect', 'username')
            self.password = config.get('alerta-dynect', 'password')
        except Exception:
            LOG.error('Failed to read Dynect credentials from %s', CONF_FILE)
            sys.exit(1)

    def run(self):

        while not self.shuttingdown:
            try:
                try:
                    self.queryDynect()
                except Exception:
                    pass
                else:
                    self.alertDynect()
                    self.last_info = self.info

                    LOG.debug('Send heartbeat...')
                    heartbeat = Heartbeat(tags=[__version__])
                    try:
                        self.api.send(heartbeat)
                    except Exception, e:
                        LOG.warning('Failed to send heartbeat: %s', e)

                LOG.debug('Waiting for next check run...')
                time.sleep(LOOP_EVERY)
            except (KeyboardInterrupt, SystemExit):
                self.shuttingdown = True

    def alertDynect(self):

        for resource in self.info:

            if resource not in self.last_info:
                continue

            if resource.startswith('gslb-'):

                # gslb status       = ok | unk | trouble | failover

                text = 'GSLB status is %s.' % self.info[resource]['status']

                if self.info[resource]['status'] == 'ok':
                    event = 'GslbOK'
                    severity = 'normal'
                else:
                    event = 'GslbNotOK'
                    severity = 'critical'
                correlate = ['GslbOK', 'GslbNotOK']

            elif resource.startswith('pool-'):

                # pool status       = up | unk | down
                # pool serve_mode   = obey | always | remove | no
                # pool weight	(1-15)

                if 'down' in self.info[resource]['status']:
                    event = 'PoolDown'
                    severity = 'major'
                    text = 'Pool is down'
                elif 'obey' not in self.info[resource]['status']:
                    event = 'PoolServe'
                    severity = 'major'
                    text = 'Pool with an incorrect serve mode'
                elif self.check_weight(self.info[resource]['gslb'], resource) is False:
                    event = 'PoolWeightError'
                    severity = 'minor'
                    text = 'Pool with an incorrect weight'
                else:
                    event = 'PoolUp'
                    severity = 'normal'
                    text = 'Pool status is normal'
                correlate = ['PoolUp', 'PoolDown', 'PoolServe', 'PoolWeightError']

            else:
                LOG.warning('Unknown resource type: %s', resource)
                continue

            # Defaults
            group = 'GSLB'
            value = self.info[resource]['status']
            environment = 'PROD'
            service = ['Network']
            tags = list()
            timeout = None
            raw_data = self.info[resource]['rawData']

            dynectAlert = Alert(
                resource=resource,
                event=event,
                correlate=correlate,
                group=group,
                value=value,
                severity=severity,
                environment=environment,
                service=service,
                text=text,
                event_type='serviceAlert',
                tags=tags,
                timeout=timeout,
                raw_data=raw_data,
            )

            try:
                self.api.send(dynectAlert)
            except Exception, e:
                LOG.warning('Failed to send alert: %s', e)

    def check_weight(self, parent, resource):
        
        weight = self.info[resource]['status'].split(':')[2]
        for pool in [resource for resource in self.info if resource.startswith('pool') and self.info[resource]['gslb'] == parent]:
            if self.info[pool]['status'].split(':')[1] == 'no':
                LOG.warning('Skipping %s because not serving for pool %s', pool, self.info[pool]['status'])
                continue

            LOG.debug('pool %s weight %s <=> %s', pool, self.info[pool]['status'].split(':')[2], weight)
            if self.info[pool]['status'].split(':')[2] != weight:
                return False
        return True

    def queryDynect(self):

        LOG.info('Query DynECT to get the state of GSLBs')
        try:
            rest_iface = DynectRest()
            rest_iface.verbose = DEBUG

            # login
            credentials = {
                'customer_name': self.customer,
                'user_name': self.username,
                'password': self.password,
            }
            LOG.debug('credentials = %s', credentials)
            response = rest_iface.execute('/Session/', 'POST', credentials)

            if response['status'] != 'success':
                LOG.error('Failed to create API session: %s', response['msgs'][0]['INFO'])
                raise RuntimeWarning

            # Discover all the Zones in DynECT
            response = rest_iface.execute('/Zone/', 'GET')
            LOG.debug('/Zone/ => %s', json.dumps(response, indent=4))
            zone_resources = response['data']

            # Discover all the LoadBalancers
            for resource in zone_resources:
                zone = resource.split('/')[3]  # eg. /REST/Zone/guardiannews.com/
                response = rest_iface.execute('/LoadBalance/' + zone + '/', 'GET')
                LOG.debug('/LoadBalance/%s/ => %s', zone, json.dumps(response, indent=4))
                gslb = response['data']

                # Discover LoadBalancer pool information.
                for lb in gslb:
                    fqdn = lb.split('/')[4]  # eg. /REST/LoadBalance/guardiannews.com/id.guardiannews.com/
                    response = rest_iface.execute('/LoadBalance/' + zone + '/' + fqdn + '/', 'GET')
                    LOG.debug('/LoadBalance/%s/%s/ => %s', zone, fqdn, json.dumps(response, indent=4))
                    status = response['data']['status']
                    monitor = response['data']['monitor']
                    self.info['gslb-' + fqdn] = {'status': status, 'gslb': fqdn, 'rawData': monitor}

                    for pool in response['data']['pool']:
                        name = '%s-%s' % (fqdn, pool['label'].replace(' ', '-'))
                        status = '%s:%s:%s' % (pool['status'], pool['serve_mode'], pool['weight'])
                        self.info['pool-' + name] = {'status': status, 'gslb': fqdn, 'rawData': pool}

            LOG.info('Finished object discovery query.')
            LOG.debug('GSLBs and Pools: %s', json.dumps(self.info, indent=4))

            # logout
            rest_iface.execute('/Session/', 'DELETE')

        except Exception, e:
            LOG.error('Failed to discover GSLBs: %s', e)


def main():

    LOG = logging.getLogger("alerta.dynect")

    try:
        DynectDaemon().run()
    except (SystemExit, KeyboardInterrupt):
        LOG.info("Exiting alerta Dynect.")
        sys.exit(0)
    except Exception as e:
        LOG.error(e, exc_info=1)
        sys.exit(1)

if __name__ == '__main__':
    main()
