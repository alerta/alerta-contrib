Query Webhook
==============

Receive Alerts using only query parameters by webhook. For those apps or use cases when you can't specify a payload or body to the query and just one to send all by query parameters.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=webhooks/query

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

You can specify all the parameters on the query except Attributes for the moment. 
https://[ALERTA-URL]/api/webhooks/query?api-key=[YOUR-API-KEY]&service=TheForce&severity=critical&resource=Alderaan&event=SomethingTerribleHappened&text=AGreatDisturbanceInTheForce&tags=Force,Alderaan,DeathStar&origin=ObiWanKenobi&group=Jedi&timeout=300

References
----------

  * Based on the other Alerta-Contrib plugins.

License
-------

Copyright (c) 2021 Pablo Villaverde. Available under the MIT License.
