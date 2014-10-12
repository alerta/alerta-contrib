Alerta Contrib
==============

Useful but non-essential additions to the alerta monitoring system which are grouped together as follows:

  * monitors - alert sources eg. ping script, SNMP traps, Syslog, URL monitor

  * plug-ins - pre-receive and post-receive server hooks

  * listeners - programs that listen for alerts forwarded by the server to AMQP or SQS queues


Example - How to use the AMQP Plug-in with RabbitMQ
---------------------------------------------------

Standard monitors for Syslog, SNMP and ping send alerts to the Alerta sever. Once the database is updated, the AMQP plug-in forwards the alerts to RabbitMQ. Different components listen for these alerts either on a dedicated queue or a shared topic, reformat the alerts and send IRC messages, emails or alerts to Pagerduty based on alert attributes.

```
       Monitors                          Plug-in                    Listeners

      +----------+                                   +-----+       +-----------+   
      |  syslog  +-------+   +------------+-----+    |  R  +-----> | IRC       |   
      +----------+       |   |            |   P |    |  a  |       +-----------+   
                         |   |            | A l |    |  b  |                       
      +----------+       |   |            | M u |    |  b  |       +-----------+   
      |  SNMP    +---------->   ALERTA    | Q g +----+  i  +-----> | Mailer    |   
      +----------+       |   |            | P i |    |  t  |       +-----------+   
                         |   |            |   n |    |  M  |                       
      +----------+       |   |            |     |    |  Q  |       +-----------+   
      | Pinger   +-------+   +-----+---+--+-----+    |     +-----> | Pagerduty |   
      +----------+                 |   |             +-----+       +-----------+   
                                 +-v---+-+                                         
                                 |       |                                         
                                 | Mongo |                                         
                                 |       |                                         
                                 |       |                                         
                                 +-------+                                         
```
