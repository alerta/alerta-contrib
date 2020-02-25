Alerta Contrib
==============

Useful but non-essential additions to the alerta monitoring system.

Integrations are specific to the monitoring tool or service
being integrated whereas plugins are standard extensions that are
triggered before or after alert reception or by an external alert
status change.

Some of the integrations listed below redirect to a dedicated
Github repository.

Integrations
------------

  * [Consul](integrations/consul)
  * [Fail2Ban](integrations/fail2ban)
  * [Kibana](https://github.com/alerta/kibana-alerta)
  * [Mailer](integrations/mailer)
  * [Nagios](https://github.com/alerta/nagios-alerta)
  * [OpsWeekly](integrations/opsweekly)
  * [Pinger](integrations/pinger)
  * [Prometheus](https://github.com/alerta/prometheus-config)
  * [Riemann](https://github.com/alerta/riemann-alerta)
  * [SNMPTrap](integrations/snmptrap)
  * [Sensu](https://github.com/alerta/sensu-alerta)
  * [Amazon SQS](integrations/sqs)
  * [Supervisor](integrations/supervisor)
  * [Syslog](integrations/syslog)
  * [URLmon](integrations/urlmon)
  * [Zabbix](https://github.com/alerta/zabbix-alerta)

Plugins
-------

  * [AlertOps](plugins/alertops)
  * [AMQP](plugins/amqp)
  * [Cachet](plugins/cachet)
  * [Enhance](plugins/enhance)
  * [Forward](plugins/forward)
  * [GeoIP](plugins/geoip)
  * [HipChat](plugins/hipchat)
  * [InfluxDB](plugins/influxdb)
  * [Logstash](plugins/logstash)
  * [Mattermost](plugins/mattermost)
  * [MS Teams](plugins/msteams)
  * [Normalise](plugins/normalise)
  * [OP5](plugins/op5)
  * [OpsGenie](plugins/opsgenie)
  * [PagerDuty](plugins/pagerduty)
  * [Prometheus](plugins/prometheus)
  * [Google Cloud Pub/Sub](plugins/pubsub)
  * [Pushover.net](plugins/pushover)
  * [Rocket.Chat](plugins/rocketchat)
  * [Slack](plugins/slack)
  * [Amazon SNS](plugins/sns)
  * [Syslog](plugins/syslog)
  * [Telegram](plugins/telegram)
  * [Timeout](plugins/timeout)
  * [Twilio SMS](plugins/twilio)
  * [Zabbix](plugins/zabbix)
  * [Forward](plugins/forward)

Webhooks
--------

  * [AWS CloudWatch](https://github.com/alerta/alerta/blob/master/alerta/webhooks/cloudwatch.py)
  * [Azure Monitor](webhooks/azuremonitor)
  * [Fail2Ban](webhooks/fail2ban)
  * [Grafana](https://github.com/alerta/alerta/blob/master/alerta/webhooks/grafana.py)
  * [Graylog](https://github.com/alerta/alerta/blob/master/alerta/webhooks/graylog.py)
  * [Mailgun](webhooks/mailgun)
  * [MS Teams](webhooks/msteams)
  * [New Relic](https://github.com/alerta/alerta/blob/master/alerta/webhooks/newrelic.py)
  * [PagerDuty](https://github.com/alerta/alerta/blob/master/alerta/webhooks/pagerduty.py)
  * [Pingdom](https://github.com/alerta/alerta/blob/master/alerta/webhooks/pingdom.py)
  * [Prometheus Alertmanager](https://github.com/alerta/alerta/blob/master/alerta/webhooks/prometheus.py)
  * [Riemann](https://github.com/alerta/alerta/blob/master/alerta/webhooks/riemann.py)
  * [Sentry](webhooks/sentry)
  * [Server Density](https://github.com/alerta/alerta/blob/master/alerta/webhooks/serverdensity.py)
  * [Slack](https://github.com/alerta/alerta/blob/master/alerta/webhooks/slack.py)
  * [Stackdriver](https://github.com/alerta/alerta/blob/master/alerta/webhooks/stackdriver.py)
  * [Telegram](https://github.com/alerta/alerta/blob/master/alerta/webhooks/telegram.py)

Tests
-----

To run the tests using a local Postgres database run:

    $ pip install -r requirements-dev.txt
    $ createdb test5
    $ ALERTA_SVR_CONF_FILE= DATABASE_URL=postgres:///test5 pytest -v webhooks/*/test*

License
-------

Copyright (c) 2014-2019 Nick Satterly and [AUTHORS](AUTHORS). Available under the MIT License.

