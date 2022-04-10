Falco Webhook
==============

Receive [Falco](https://falco.org) events via webhook directly from Falco or via [Falco Sidekick](https://github.com/falcosecurity/falcosidekick)

Example Input
-------------
A sample input event from falco looks like:
```json
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
```

and a sample alert from k8s could look like:

```json
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
```


The `time`, `rule`, `priority`, `output_fields`, and `output` properties are guaranteed to always exist, the fields inside of `output_fields` are dynamic based on the `rule` triggered.