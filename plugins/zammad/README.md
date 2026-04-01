# Zammad Plugin

Create a Zammad ticket for new alerts with severity critical or major.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

## Installation

Clone the GitHub repo and run:

```shell
python setup.py install
```

Or, to install remotely from GitHub run:

```shell
pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/zammad
```

Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

## Configuration

Add `zammad` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file or environment variable. Set plugin-specific variables
either in the server configuration file or as environment variables.

The authentication towards Zammad can be done with username and password or
token authentication. This user or token needs at least the ticket.customer or
ticket.agent permissions. We would recommend to use a dedicated customer account
to follow the principle of least privilege. This customer account needs to be
allowed to use tokens (user_preferences.access_token). The site to create the
access tokens can normal be found at
<https://example.zammad.com/#profile/token_access>.

### Required settings

```python
PLUGINS = ['zammad']
ZAMMAD_URL = https://example.zammad.com #No slash in the end
ZAMMAD_CUSTOMER = <zammad_customer_email>
# username and password authentication
ZAMMAD_USERNAME = <zammad_user>
ZAMMAD_PASSWORD = <zammad_user_password>
# or token authentication
ZAMMAD_TOKEN = <zammad_token>
```

The `DASHBOARD_URL` setting should be configured to link Zammad tickets to
the Alerta alerts:

```python
DASHBOARD_URL = ''  # default="not set"
```

### Optional settings

These setting are optional and further customize the integrations into Zammad.

```python
ZAMMAD_API_URL = '' # default="ZAMMAD_URL + /api/v1/"
ZAMMAD_GROUP = '' # default="Users"
ZAMMAD_ARTICLE_TYPE = '' #default="note"
ZAMMAD_ENVIRONMENT = '' #default="Production"
```

### Example

This show a functional example configuration with the use of Zammad token
authentication.

```python
PLUGINS = ['reject', 'zammad']
ZAMMAD_CUSTOMER = 'alerta@alerta.io'
ZAMMAD_TOKEN = '3tKTy9PsxkwsOshTTm1PqBi2r03QNbD4UmRX2EZ0lH-EVZqGDTdWM2-V_yOnCOSE'
DASHBOARD_URL = 'https://try.alerta.io'
ZAMMAD_ENVIRONMENT = 'Production,Test'
```

## Development && Debug

This section should help to develop and debug the plugins.

To debug you only need to set the [debug mode](https://docs.alerta.io/configuration.html#general-settings)
in Alerta.

```python
DEBUG = True
```

### Python environment

You can setup a python environment with [uv](https://github.com/astral-sh/uv)
all other methods also work.

1. Enter the alerta-contrib project
2. Run `uv init --no-workspace -p 3.12` -p is the python version
3. Install the requirements-dev.txt with `uv pip install -r requirments-dev.txt`
4. Enable the venv with `source .venv/bin/activate`
5. Happy developing (=

### Test alerts

The included bash script send-payload.sh can be used to send Prometheus style
alerts for testing the application. This script need an Alerta Api Key with at
least following scopes:

- write:alerts
- write:heartbeats
- write:webhooks

To run the script:

```shell
export ALERTA_WEBHOOK_URL='https://try.alerta.io/api/webhooks/prometheus?api-key=<api_key>'`
bash send-payload.sh both
```

This will send a firing and resolved Prometheus alert to the Alerta Prometheus
webhook. For more detail take a look at the script.

## Future Plans

Following features are planned for the future:

- Make resolved and create ticket severity configurable
- Alerta customer to Zammad customer mapping
- Customiziable Zammad sender (Customer/Agent)
- Alerta user in ack status change Zammad article
- More status changes handling (open, shelve, close, delete)

Help to implement those features is very welcome.

## License

This plugins was initially created by Jonas Reindl ([@ohdearaugustin](https://github.com/ohdearaugustin))
from [mgit GmbH](https://mgit.at).

Copyright (c) 2024 mgIT GmbH. Available under the MIT License.
