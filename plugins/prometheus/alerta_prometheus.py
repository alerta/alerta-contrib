
import os
import datetime
import requests
import logging

from alerta.app import app
from alerta.app import db
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.prometheus')

ALERTMANAGER_API_URL = os.environ.get('ALERTMANAGER_API_URL') or app.config.get('ALERTMANAGER_API_URL', 'http://localhost:9093')
ALERTMANAGER_API_KEY = os.environ.get('ALERTMANAGER_API_KEY') or app.config.get('ALERTMANAGER_API_KEY', '')  # not used
ALERTMANAGER_SILENCE_DAYS = os.environ.get('ALERTMANAGER_SILENCE_DAYS') or app.config.get('ALERTMANAGER_SILENCE_DAYS', 1)


class AlertmanagerSilence(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):

        if alert.event_type != 'prometheusAlert':
            return

        if alert.status == status:
            return

        if status == 'ack':
            LOG.debug('Alertmanager: Add silence for alertname=%s instance=%s', alert.event, alert.resource)
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
                "endsAt": (datetime.datetime.utcnow() + datetime.timedelta(days=ALERTMANAGER_SILENCE_DAYS))
                              .replace(microsecond=0).isoformat() + ".000Z",
                "createdBy": "alerta",
                "comment": text if text != '' else "silenced by alerta"
            }

            url = ALERTMANAGER_API_URL + '/api/v1/silences'
            try:
                r = requests.post(url, json=data, timeout=2)
            except Exception as e:
                raise RuntimeError("Alertmanager: ERROR - %s", e)
            LOG.debug('Alertmanager: %s - %s', r.status_code, r.text)

            # example r={"status":"success","data":{"silenceId":8}}
            try:
                silenceId = r.json()['data']['silenceId']
                db.update_attributes(alert.id, {'silenceId': silenceId})
            except Exception as e:
                raise RuntimeError("Alertmanager: ERROR - %s", e)
            LOG.debug('Alertmanager: Added silenceId %s to attributes', silenceId)

        elif status == 'open':
            LOG.debug('Alertmanager: Remove silence for alertname=%s instance=%s', alert.event, alert.resource)

            silenceId = alert.attributes.get('silenceId', None)
            if silenceId:
                url = ALERTMANAGER_API_URL + '/api/v1/silence/%s' % silenceId
                try:
                    r = requests.delete(url, timeout=2)
                except Exception as e:
                    raise RuntimeError("Alertmanager: ERROR - %s", e)
                LOG.debug('Alertmanager: %s - %s', r.status_code, r.text)

                try:
                    db.update_attributes(alert.id, {'silenceId': None})
                except Exception as e:
                    raise RuntimeError("Alertmanager: ERROR - %s", e)
                LOG.debug('Alertmanager: Removed silenceId %s from attributes', silenceId)
