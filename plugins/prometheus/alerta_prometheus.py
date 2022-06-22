import datetime
import logging
import os
import requests
import json
from typing import Any

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

from alerta.models.alert import Alert
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.prometheus')

DEFAULT_ALERTMANAGER_API_URL = 'http://localhost:9093'

ALERTMANAGER_API_URL = os.environ.get('ALERTMANAGER_API_URL') or app.config.get('ALERTMANAGER_API_URL', None)
ALERTMANAGER_USERNAME = os.environ.get('ALERTMANAGER_USERNAME') or app.config.get('ALERTMANAGER_USERNAME', None)
ALERTMANAGER_PASSWORD = os.environ.get('ALERTMANAGER_PASSWORD') or app.config.get('ALERTMANAGER_PASSWORD', None)
ALERTMANAGER_SILENCE_DAYS = os.environ.get('ALERTMANAGER_SILENCE_DAYS') or app.config.get('ALERTMANAGER_SILENCE_DAYS', 1)
ALERTMANAGER_SILENCE_FROM_ACK = os.environ.get('ALERTMANAGER_SILENCE_FROM_ACK') or app.config.get('ALERTMANAGER_SILENCE_FROM_ACK', False)
ALERTMANAGER_USE_EXTERNALURL_FOR_SILENCES =  os.environ.get('ALERTMANAGER_USE_EXTERNALURL_FOR_SILENCES') or app.config.get('ALERTMANAGER_USE_EXTERNALURL_FOR_SILENCES',False)


class AlertmanagerSilence(PluginBase):

    def __init__(self, name=None):

        self.auth = (ALERTMANAGER_USERNAME, ALERTMANAGER_PASSWORD) if ALERTMANAGER_USERNAME else None

        super(AlertmanagerSilence, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        '''
        If a silence exists for an open or closed alert we probably want to remove it
        '''
        if status in ('open', 'closed'):

            silenceId = alert.attributes.get('silenceId', None)
            if silenceId:
                LOG.debug('Alertmanager: Remove silence for alertname=%s instance=%s', alert.event, alert.resource)
                base_url = ALERTMANAGER_API_URL or alert.attributes.get('externalUrl', DEFAULT_ALERTMANAGER_API_URL)
                url = base_url + '/api/v1/silence/%s' % silenceId
                try:
                    r = requests.delete(url, auth=self.auth, timeout=2)
                except Exception as e:
                    raise RuntimeError("Alertmanager: ERROR - %s" % e)
                LOG.debug('Alertmanager: %s - %s', r.status_code, r.text)

                try:
                    alert.attributes['silenceId'] = None
                except Exception as e:
                    raise RuntimeError("Alertmanager: ERROR - %s" % e)
                LOG.debug('Alertmanager: Removed silenceId %s from attributes', silenceId)
            if status == 'closed':
                LOG.warning("Status is now closed")

        return alert

    def take_action(self, alert: Alert, action: str, text: str, **kwargs) -> Any:
        '''
        Set silence in alertmanager.
        '''

        if alert.event_type != 'prometheusAlert':
            return alert


        base_url = ALERTMANAGER_API_URL or alert.attributes.get('externalUrl', DEFAULT_ALERTMANAGER_API_URL)
        if action == 'close':
            LOG.warning("Got a close action so trying to close this in alertmanager too")
            url = base_url + '/api/v1/alerts'
            raw_data_string = alert.raw_data
            raw_data = json.loads(raw_data_string)
            # set the endsAt to now so alertmanager will consider it expired or whatever
            raw_data["endsAt"] = (datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).replace(microsecond=0).isoformat() + ".000Z"
            LOG.debug("Raw data type:  {}, Raw data contents: {}".format(type(raw_data),raw_data))
            data = [ raw_data ]
            try:
                r = requests.post(url, json=data, auth=self.auth, timeout=2)
            except Exception as e:
                raise RuntimeError("Alertmanager: ERROR - %s" % e)
            LOG.debug('Alertmanager response was: %s - %s', r.status_code, r.text)

        elif action == 'ack' and ALERTMANAGER_SILENCE_FROM_ACK:

            if not ALERTMANAGER_SILENCE_DAYS:
                silence_seconds = kwargs.get('timeout', alert.timeout)
            else:
                try:
                    silence_days = int(ALERTMANAGER_SILENCE_DAYS)
                except Exception as e:
                    LOG.error(
                        "Alertmanager: Could not parse 'ALERTMANAGER_SILENCE_DAYS': %s", e)
                    raise RuntimeError(
                        "Could not parse 'ALERTMANAGER_SILENCE_DAYS': %s" % e)
                silence_seconds = silence_days * 86400

            LOG.debug('Alertmanager: Add silence for alertname=%s instance=%s timeout=%s',
                      alert.event, alert.resource, str(silence_seconds))
            data = {
                "matchers": [
                    {
                      "name": "alertname",
                      "value": alert.event
                    },
                    {
                      "name": "instance",
                      "value": alert.resource
                    }
                ],
                "startsAt": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + ".000Z",
                "endsAt": (datetime.datetime.utcnow() + datetime.timedelta(seconds=silence_seconds))
                              .replace(microsecond=0).isoformat() + ".000Z",
                "createdBy": "alerta",
                "comment": text if text != '' else "silenced by alerta"
            }

            # if alertmanager is clustered behind a load balancer that mirrors requests we should prefer to create one silence 
            # rather than many 
            if ALERTMANAGER_USE_EXTERNALURL_FOR_SILENCES:
                base_url = alert.attributes.get('externalUrl', DEFAULT_ALERTMANAGER_API_URL) or ALERTMANAGER_API_URL 
            else: 
                base_url = ALERTMANAGER_API_URL or alert.attributes.get('externalUrl', DEFAULT_ALERTMANAGER_API_URL)

            url = base_url + '/api/v1/silences'


            try:
                r = requests.post(url, json=data, auth=self.auth, timeout=2)
            except Exception as e:
                raise RuntimeError("Alertmanager: ERROR - %s" % e)
            LOG.debug('Alertmanager: %s - %s', r.status_code, r.text)

            # example r={"status":"success","data":{"silenceId":8}}
            try:
                data = r.json().get('data', [])
                if data:
                    silenceId = data['silenceId']
                    alert.attributes['silenceId'] = silenceId
                else:
                    silenceId = alert.attributes.get('silenceId', "unknown")
                text = text + ' (silenced in Alertmanager)'
            except Exception as e:
                raise RuntimeError("Alertmanager: ERROR - %s" % e)
            LOG.debug('Alertmanager: Added silenceId %s to attributes', silenceId)

        elif action == 'unack':
            LOG.debug('Alertmanager: Remove silence for alertname=%s instance=%s', alert.event, alert.resource)

            silenceId = alert.attributes.get('silenceId', None)
            if silenceId:
                base_url = ALERTMANAGER_API_URL or alert.attributes.get('externalUrl', DEFAULT_ALERTMANAGER_API_URL)
                url = base_url + '/api/v1/silence/%s' % silenceId
                try:
                    r = requests.delete(url, auth=self.auth, timeout=2)
                except Exception as e:
                    raise RuntimeError("Alertmanager: ERROR - %s" % e)
                LOG.debug('Alertmanager: %s - %s', r.status_code, r.text)

                try:
                    alert.attributes['silenceId'] = None
                except Exception as e:
                    raise RuntimeError("Alertmanager: ERROR - %s" % e)
                LOG.debug('Alertmanager: Removed silenceId %s from attributes', silenceId)

        return alert
