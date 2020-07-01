Statuscake Webhook
==============

Receive [Statuscake](https://www.statuscake.com) alerts via webhook callbacks.

For help, join [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=webhooks/statuscake

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

The custom webhook will be auto-detected and added to the list of available API endpoints.

Add the Alerta API webhook URL in the Statuscake contact group webhook section

![StatusCake Contact Group](./images/statuscake-webhook.png)


References
----------

  * StatusCake Webhook: https://www.statuscake.com/kb/knowledge-base/how-to-use-the-web-hook-url/

License
-------

Copyright (c) 2020 Matthieu Serrepuy. Available under the MIT License.

