from csv import excel_tab
import resource
from alerta.models.alert import Alert
from alerta.webhooks import WebhookBase

'''sample events
{
   "output" : "16:31:56.746609046: Error File below a known binary directory opened for writing (user=root command=touch /bin/hack file=/bin/hack)"
   "priority" : "Error",
   "rule" : "Write below binary dir",
   "time" : "2017-10-09T23:31:56.746609046Z",
   "output_fields" : {
      "user.name" : "root",
      "evt.time" : 1507591916746609046,
      "fd.name" : "/bin/hack",
      "proc.cmdline" : "touch /bin/hack"
   }
}

{
    "output": "17:48:58.590038385: Notice A shell was spawned in a container with an attached terminal (user=root k8s.pod=falco-74htl container=a98c2aa8e670 shell=bash parent=<NA> cmdline=bash  terminal=34816)",
    "priority": "Notice",
    "rule": "Terminal shell in container",
    "time": "2017-12-20T17:48:58.590038385Z",
    "output_fields": {
        "container.id": "a98c2aa8e670",
        "evt.time": 1513792138590038385,
        "k8s.pod.name": "falco-74htl",
        "proc.cmdline": "bash ",
        "proc.name": "bash",
        "proc.pname": null,
        "proc.tty": 34816,
        "user.name": "root"
    }
}
'''

class FalcoWebhook(WebhookBase):
    @staticmethod
    def _get_resource(payload):
        # https://v0-26.falco.org/docs/rules/supported-fields/
        # if there's a hostname in the payload, return that
        hostname = payload.get('hostname', '')
        if hostname:
            return hostname
        # if there's a k8s pod name in the payload, return that
        if payload['output_fields'].get('k8s.pod.name', ''):
            return payload['output_fields']['k8s.pod.name']
        # check if there's a container name
        if payload['output_fields'].get('container.name', ''):
            return payload['output_fields']['container.name']
        # if all else fails, return falco
        return 'falco'

    @staticmethod
    def _get_severity(payload):
        p = payload.get('priority')
        # alerta supports: critical, major, minor, warning
        # falco supports : emergency, alert, critical, error, warning, notice, informational, debug
        # map critical
        if p == 'emergency' or p == 'alert' or p == 'critical':
            return 'critical'
        # map major
        if p == 'error':
            return 'major'
        # map minor
        if p == 'warning' or p == 'notice':
            return 'minor'
        # otherwise warning
        return 'warning'

    @staticmethod
    def _get_tags(payload):
        try:
            tags = ['{}={}'.format(k, v) for k, v in payload['output_fields'].items()]
        except Exception as e:
            return ''
        

    def incoming(self, query_string, payload):
        # https://github.com/alerta/alerta-docs/blob/master/conventions.rst
        return Alert(
            resource=self._get_resource(payload),
            event=payload.get('rule'),
            environment=payload.get('environment', 'unknown'),
            severity=self._get_severity(payload),
            service=payload.get('service', 'falco'),
            group='security',
            value=payload.get('rule', 'unknown'),
            text=payload.get('output'),
            tags=self._get_tags(payload),
            attributes=payload.get('output_fields', {}),
            origin='falco',
            raw_data=str(payload)
        )