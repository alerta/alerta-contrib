Google Cloud Pub/Sub Plugin
===========================

Send alerts to Google Cloud Pub/Sub.

For help, join [![Gitter chat]](https://gitter.im/alerta/chat)

Installation
------------

You need to install following python packages:

    $ sudo pip install --upgrade google-cloud
    $ sudo pip install --upgrade oauth2client

Follow this to configure [![authentication]](https://googlecloudplatform.github.io/google-cloud-python/stable/pubsub-usage.html#authentication-configuration)

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/pubsub

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `pubsub` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

```python
PLUGINS = ['pubsub']
```

if you want to use google service account for pubsub. You need to set it in `alertad.conf`:

```python
SERVICE_ACCOUNT_FILE='path to service account json file'
```
References
----------

  * What is Google Cloud Pub/Sub? https://cloud.google.com/pubsub/docs/overview

License
-------

Copyright (c) 2017 Arindam Choudhury. Available under the MIT License.
