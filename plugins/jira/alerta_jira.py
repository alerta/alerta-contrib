import http.client
import json
import logging
import os
from base64 import b64encode

from alerta.plugins import PluginBase

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

# set plugin logger
LOG = logging.getLogger('alerta.plugins.jira')

# retrieve plugin configurations
JIRA_URL = app.config.get('JIRA_URL') or os.environ.get('JIRA_URL')
JIRA_PROJECT = app.config.get('JIRA_PROJECT') or os.environ.get('JIRA_PROJECT')
JIRA_USER = app.config.get('JIRA_USER') or os.environ.get('JIRA_USER')
JIRA_PASS = app.config.get('JIRA_PASS') or os.environ.get('JIRA_PASS')


class JiraCreate(PluginBase):

    def _sendjira(self, host, event, value, chart, text, severity):
        LOG.info('JIRA: Create task ...')
        userpass = '{}:{}'.format(JIRA_USER, JIRA_PASS)
        userAndPass = b64encode(bytes(userpass, 'utf-8')).decode('ascii')
        LOG.debug('JIRA_URL: {}'.format(JIRA_URL))
        conn = http.client.HTTPSConnection('%s' % (JIRA_URL))

        payload_dict = {
            'fields': {
                'project':
                {
                    'key': '%s' % (JIRA_PROJECT)
                },
                'summary': 'Server {}: alert {} in chart {} - Severity: {}'.format(host.upper(), event.upper(), chart.upper(), severity.upper()),
                'description': 'The chart {} INFO: {}. \nVALUE: {}.'.format(chart, text, value),
                'issuetype': {
                    'name': 'Bug'
                },
            }
        }
        payload = json.dumps(payload_dict, indent=4)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic %s' % userAndPass
        }

        conn.request('POST', '/rest/api/2/issue/', payload, headers)
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)
        return data['key']

    # reject or modify an alert before it hits the database
    def pre_receive(self, alert):
        return alert

    # after alert saved in database, forward alert to external systems
    def post_receive(self, alert):
        try:
            # if the alert is critical and don't duplicate, create task in Jira
            if alert.status not in ['ack', 'closed', 'shelved'] and alert.duplicate_count == 0:
                LOG.info('Jira: Received an alert')
                LOG.debug('Jira: ALERT       {}'.format(alert))
                LOG.debug('Jira: ID          {}'.format(alert.id))
                LOG.debug('Jira: RESOURCE    {}'.format(alert.resource))
                LOG.debug('Jira: EVENT       {}'.format(alert.event))
                LOG.debug('Jira: SEVERITY    {}'.format(alert.severity))
                LOG.debug('Jira: TEXT        {}'.format(alert.text))

                # get basic info from alert
                host = alert.resource.split(':')[0]
                LOG.debug('JIRA: HOST        {}'.format(host))
                chart = '.'.join(alert.event.split('.')[:-1])
                LOG.debug('JIRA: CHART       {}'.format(chart))
                event = alert.event.split('.')[-1]
                LOG.debug('JIRA: EVENT       {}'.format(event))

                # call the _sendjira and modify de text (discription)
                task = self._sendjira(
                    host, event, alert.value, chart, alert.text, alert.severity)
                task_url = 'https://' + JIRA_URL + '/browse/' + task
                href = '<a href="{}" target="_blank">{}</a>'.format(
                    task_url, task)
                alert.attributes = {'Jira Task': href}
                return alert

        except Exception as e:
            LOG.error('Jira: Failed to create task: %s', e)
            return

    # triggered by external status changes, used by integrations
    def status_change(self, alert, status, text):
        return
