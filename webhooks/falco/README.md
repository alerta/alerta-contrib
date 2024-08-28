Falco Webhook
==============

Receive [falco](https://falco.org/) alerts via `falcosidekick` webhook.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Falco webhook version support
-------------------------------

[TBD]

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=webhooks/falco

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

`falcosidekick` custom outputs are used here.

Specifically, the `webhook` output. Read more [here](https://github.com/falcosecurity/falcosidekick/blob/master/docs/outputs/webhook.md).

First, an Alerta Api Key has to be set. It can be created in the Alerta's UI, under "Api Keys" menu.

Then, note a custom field is being used to identify environments. This is set in the installation with `customfields="environment:Development"`. Set the right environment for your Falco deployment here.

Finally, if you are using Helm to install Falco, the webhook can be set like this:

``` shell
helm install falco -n falco --set driver.kind=modern_ebpf --set tty=true falcosecurity/falco \
--set falcosidekick.enabled=true \
--set falcosidekick.config.webhook.address="<alerta-url-protocol-here>://<alerta-url-here>/api/webhooks/falco"  \
--set falcosidekick.config.webhook.minimumpriority=notice \
--set falcosidekick.config.webhook.customHeaders="X-Api-Key: <alerta-api-key-here>" \
--set falcosidekick.config.webhook.mutualtls=false \
--set falcosidekick.config.webhook.checkcert=false \
--set falcosidekick.config.customfields="environment:Development"
```

FalcoSidekick payload example
-----------------------------

This is an example of a payload sent by `falcosidekick`:

``` json
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
```
