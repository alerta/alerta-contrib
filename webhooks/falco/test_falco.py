import json
import unittest

import alerta_falco
from alerta.app import create_app, custom_webhooks


class FalcoWebhookTestCase(unittest.TestCase):

    def setUp(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()
        custom_webhooks.webhooks['falco'] = alerta_falco.FalcoWebhook(
        )

        self.headers = {
            'Content-Type': 'application/json'
        }

        self.alert_id = 'f0c55228-c61d-462a-9aeb-f6048d37fdf6'

    def test_falcowebhook(self):

        payload_cmd = r"""
        {
           "uuid": "06f73663-b1d4-42e4-b236-eacbd2b96998",
           "output": "20:39:17.500016161: Notice A shell was spawned in a container with an attached terminal (evt_type=execve user=root user_uid=0 user_loginuid=-1 process=sh proc_exepath=/bin/busybox parent=containerd-shim command=sh -c uptime terminal=34816 exe_flags=EXE_WRITABLE container_id=9273d0110c4e container_image=<NA> container_image_tag=<NA> container_name=<NA> k8s_ns=<NA> k8s_pod_name=<NA>)",
           "priority": "Notice",
           "rule": "Terminal shell in container",
           "time": "2024-07-16T20:39:17.500016161Z",
           "output_fields": {
             "container.id": "9273d0110c4e",
             "container.image.repository": "None",
             "container.image.tag": "None",
             "container.name": "None",
             "evt.arg.flags": "EXE_WRITABLE",
             "evt.time": 1721162357500016161,
             "evt.type": "execve",
             "k8s.ns.name": "None",
             "k8s.pod.name": "None",
             "proc.cmdline": "sh -c uptime",
             "proc.exepath": "/bin/busybox",
             "proc.name": "sh",
             "proc.pname": "containerd-shim",
             "proc.tty": 34816,
             "user": "jdelacamara",
             "user.loginuid": -1,
             "user.name": "root",
             "user.uid": 0,
             "environment": "Development"
           },
           "source": "syscall",
           "tags": [
             "T1059",
             "container",
             "maturity_stable",
             "mitre_execution",
             "shell"
           ],
           "hostname": "nixos"
         }
        """

        # Missing fields
        payload_invalidcmd = r"""
        {
           "uuid": "06f73663-b1d4-42e4-b236-eacbd2b96998",
           "time": "2024-07-16T20:39:17.500016161Z",
           "output_fields": {
             "container.id": "9273d0110c4e",
             "container.image.repository": "None",
             "container.image.tag": "None",
             "container.name": "None",
             "evt.arg.flags": "EXE_WRITABLE",
             "evt.time": 1721162357500016161,
             "evt.type": "execve",
             "k8s.ns.name": "None",
             "k8s.pod.name": "None",
             "proc.cmdline": "sh -c uptime",
             "proc.exepath": "/bin/busybox",
             "proc.name": "sh",
             "proc.pname": "containerd-shim",
             "proc.tty": 34816,
             "user": "jdelacamara",
             "user.loginuid": -1,
             "user.name": "root",
             "user.uid": 0,
             "environment": "Development"
           },
           "source": "syscall",
           "tags": [
             "T1059",
             "container",
             "maturity_stable",
             "mitre_execution",
             "shell"
           ],
           "hostname": "nixos"
         }
        """

        # ack with missing fields
        response = self.client.post('/webhooks/falco', data=payload_invalidcmd, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data.decode('utf-8'))

        # ack
        response = self.client.post('/webhooks/falco', data=payload_cmd, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
