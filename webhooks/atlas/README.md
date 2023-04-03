MongoDB Atlas Webhook
==============

Receive [MongoDB Atlas](https://www.mongodb.com/atlas/database) alerts via webhook callbacks.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=webhooks/atlas

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

The custom webhook will be auto-detected and added to the list of available API endpoints.

Add the Alerta API webhook URL in the MongoDB Atlas webhook section


References
----------

  * MongoDB Atlas Webhook Integration: https://docs.atlas.mongodb.com/tutorial/third-party-service-integrations/

License
-------

Copyright (c) 2020 Matthieu Serrepuy. Available under the MIT License.

