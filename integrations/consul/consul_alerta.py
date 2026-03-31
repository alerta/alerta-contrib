#!/usr/bin/env python

"""Forward Consul health-check alerts to the Alerta API."""

import json
import logging
import os
import sys
import time

import consul
from alertaclient.api import Client

LOG = logging.getLogger('consul-alerta')
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s - %(message)s', level=logging.INFO)

CONSUL_HOST = os.environ.get('CONSUL_HOST', '127.0.0.1')
CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))

SEVERITY_MAP = {
    'critical': 'critical',
    'warning': 'warning',
    'passing': 'ok',
}

DEFAULTS = {
    'alerta/max_retries': 3,
    'alerta/sleep': 2,
    'alerta/timeout': 900,
    'alerta/origin': 'consul',
    'alerta/alerttype': 'ConsulAlert',
}


def get_consul_client():
    return consul.Consul(
        host=CONSUL_HOST,
        port=CONSUL_PORT,
        token=None,
        scheme='http',
        consistency='default',
        dc=None,
        verify=True,
    )


def kv_get(client, key, default=None, required=False):
    """Read a value from the Consul KV store.

    Returns *default* when the key is missing (unless *required*, in which case
    the process exits with an error).
    """
    try:
        value = client.kv.get(key)[1]['Value']
        if isinstance(value, bytes):
            value = value.decode()
        return value
    except Exception:
        if required:
            LOG.error('Required Consul KV key %r is not set — exiting', key)
            sys.exit(1)
        LOG.info('Key %r not found, using default: %s', key, default)
        return default


def load_config(client):
    url = kv_get(client, 'alerta/apiurl', required=True)
    key = kv_get(client, 'alerta/apikey', required=True)
    cfg = {k.split('/')[-1]: type(v)(kv_get(client, k, default=v))
           for k, v in DEFAULTS.items()}
    return url, key, cfg


def resolve_environment(client, node):
    env = kv_get(client, f'alerta/env/{node}')
    if env:
        return env
    return kv_get(client, 'alerta/defaultenv', default='Production')


def send_alert(api, client, check, cfg):
    environment = resolve_environment(client, check['Node'])

    for attempt in range(1, cfg['max_retries'] + 1):
        try:
            response = api.send_alert(
                resource=check['Node'],
                event=check['CheckId'],
                value=check['Status'],
                correlate=list(SEVERITY_MAP.keys()),
                environment=environment,
                service=[check['CheckId']],
                severity=SEVERITY_MAP[check['Status']],
                text=check['Output'],
                timeout=cfg['timeout'],
                origin=cfg['origin'],
                type=cfg['alerttype'],
            )
            LOG.info('Alert accepted: %s', response)
            return
        except Exception as exc:
            LOG.warning('Attempt %d/%d failed: %s',
                        attempt, cfg['max_retries'], exc)
            time.sleep(cfg['sleep'])

    LOG.error('All %d attempts exhausted — API unreachable',
              cfg['max_retries'])


def main():
    checks = json.load(sys.stdin)
    LOG.info('Received %d check(s) from Consul', len(checks))

    kv_client = get_consul_client()
    url, key, cfg = load_config(kv_client)
    api = Client(endpoint=url, key=key)

    for check in checks:
        send_alert(api, kv_client, check, cfg)


if __name__ == '__main__':
    main()
