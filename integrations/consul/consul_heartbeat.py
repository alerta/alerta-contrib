#!/usr/bin/env python

"""Send periodic heartbeats from Consul to the Alerta API."""

import logging
import os
import sys
import time

import consul
from alertaclient.api import Client

LOG = logging.getLogger('consul-heartbeat')
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s - %(message)s', level=logging.INFO)

CONSUL_HOST = os.environ.get('CONSUL_HOST', '127.0.0.1')
CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))


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


def kv_get(client, key, required=False):
    """Read a value from the Consul KV store."""
    try:
        value = client.kv.get(key)[1]['Value']
        if isinstance(value, bytes):
            value = value.decode()
        return value
    except Exception:
        if required:
            LOG.error('Required Consul KV key %r is not set — exiting', key)
            sys.exit(1)
        return None


def send_heartbeat(api, origin, timeout, max_retries, retry_sleep):
    for attempt in range(1, max_retries + 1):
        try:
            response = api.heartbeat(origin=origin, timeout=timeout)
            LOG.info('Heartbeat sent: %s', response)
            return
        except Exception as exc:
            LOG.warning('Attempt %d/%d failed: %s', attempt, max_retries, exc)
            time.sleep(retry_sleep)

    LOG.error('All %d attempts exhausted — API unreachable', max_retries)


def main():
    kv_client = get_consul_client()

    url = kv_get(kv_client, 'alerta/apiurl', required=True)
    key = kv_get(kv_client, 'alerta/apikey', required=True)
    max_retries = int(kv_get(kv_client, 'alerta/max_retries') or 3)
    retry_sleep = int(kv_get(kv_client, 'alerta/sleep') or 2)
    timeout = int(kv_get(kv_client, 'alerta/timeout') or 900)
    origin = kv_get(kv_client, 'alerta/origin') or 'consul'

    api = Client(endpoint=url, key=key)
    send_heartbeat(api, origin, timeout, max_retries, retry_sleep)


if __name__ == '__main__':
    main()
