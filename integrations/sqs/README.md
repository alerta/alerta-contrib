Amazon SQS Integration
======================

Subscribe to SQS queue of alerts.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/sqs

Configuration
-------------

```python
AWS_ACCESS_KEY_ID = ''  # default="not set"
AWS_SECRET_ACCESS_KEY = ''  # default="not set"
```

**Default Configuration**

```python
AWS_REGION = 'eu-west-1"'  # default="eu-west-1"
AWS_SQS_QUEUE = 'alerts'
```

Troubleshooting
---------------

TBC

References
----------

  * Amazon Web Services SQS: https://aws.amazon.com/sqs/getting-started/

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.
