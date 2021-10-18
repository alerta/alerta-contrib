#!/usr/bin/env python

import json
import logging
import os
import re
import signal
import smtplib
import socket
import sys
import threading
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import reduce

import jinja2
import six
import sqlalchemy
from alertaclient.api import Client
from alertaclient.models.alert import Alert
from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin

__version__ = '5.2.0'

DNS_RESOLVER_AVAILABLE = False

try:
    import dns.resolver

    DNS_RESOLVER_AVAILABLE = True
except:
    sys.stdout.write('Python dns.resolver unavailable. The skip_mta option will be forced to False\n')  # nopep8

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)
root = logging.getLogger()

OPTIONS = {
    'config_file': '~/.alerta.conf',
    'profile': None,
    'endpoint': 'http://localhost:8080',
    'key': '',
    'amqp_url': 'redis://localhost:6379/',
    'amqp_topic': 'notify',
    'amqp_queue_name': '',  # Name of the AMQP queue. Default is no name (default queue destination).
    'amqp_queue_exclusive': True,  # Exclusive queues may only be consumed by the current connection.
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_username': '',  # application-specific username if it differs from the specified 'mail_from' user
    'smtp_password': '',  # application-specific password if gmail used
    'smtp_starttls': True,  # use the STARTTLS SMTP extension
    'smtp_use_ssl': False,  # whether or not SSL is being used for the SMTP connection
    'ssl_key_file': None,  # a PEM formatted private key file for the SSL connection
    'ssl_cert_file': None,  # a certificate chain file for the SSL connection
    'mail_from': '',  # alerta@example.com
    'mail_to': [],  # devops@example.com, support@example.com
    'mail_localhost': None,  # fqdn to use in the HELO/EHLO command
    'mail_template': os.path.dirname(__file__) + os.sep + 'email.tmpl',
    'mail_template_html': os.path.dirname(__file__) + os.sep + 'email.html.tmpl',  # nopep8
    'mail_subject': ('[{{ alert.status|capitalize }}] {{ alert.environment }}: '
                     '{{ alert.severity|capitalize }} {{ alert.event }} on '
                     '{{ alert.service|join(\',\') }} {{ alert.resource }}'),
    'dashboard_url': 'http://try.alerta.io',
    'debug': False,
    'skip_mta': False,
    'email_type': 'text',  # options are: text, html
    'severities': []
}

if os.environ.get('DEBUG'):
    OPTIONS['debug'] = True

# seconds (hold alert until sending, delete if cleared before end of hold time)
HOLD_TIME = 30

on_hold = dict()


class FanoutConsumer(ConsumerMixin):

    def __init__(self, connection):

        self.connection = connection
        self.channel = self.connection.channel()

    def get_consumers(self, Consumer, channel):
        exchange = Exchange(
            name=OPTIONS['amqp_topic'],
            type='fanout',
            channel=self.channel,
            durable=True
        )

        queues = [
            Queue(
                name=OPTIONS['amqp_queue_name'],
                exchange=exchange,
                routing_key='',
                channel=self.channel,
                exclusive=OPTIONS['amqp_queue_exclusive']
            )
        ]

        return [
            Consumer(queues=queues, accept=['json'],
                     callbacks=[self.on_message])
        ]

    def on_message(self, body, message):
        sevs = list(OPTIONS['severities'])
        if not sevs:
            sevs = ['critical', 'major']

        try:
            alert = Alert.parse(body)
            alertid = alert.get_id()
        except Exception as e:
            LOG.warn(e)
            return

        if alert.repeat:
            message.ack()
            return

        if alert.status not in ['open', 'closed']:
            message.ack()
            return

        if (
                alert.severity not in sevs and
                alert.previous_severity not in sevs
        ):
            message.ack()
            return

        if alertid in on_hold:
            if alert.severity in ['normal', 'ok', 'cleared']:
                try:
                    del on_hold[alertid]
                except KeyError:
                    pass
                message.ack()
            else:
                on_hold[alertid] = (alert, time.time() + HOLD_TIME)
                message.ack()
        else:
            on_hold[alertid] = (alert, time.time() + HOLD_TIME)
            message.ack()


class MailSender(threading.Thread):

    def __init__(self):
        self.should_stop = False
        self._subject_template = jinja2.Template(OPTIONS['mail_subject'])
        super(MailSender, self).__init__()

    def run(self):
        api = Client(endpoint=OPTIONS['endpoint'], key=OPTIONS['key'])
        keep_alive = 0

        while not self.should_stop:
            for alertid in list(on_hold.keys()):
                try:
                    (alert, hold_time) = on_hold[alertid]
                except KeyError:
                    continue
                if time.time() > hold_time:
                    self.send_email(alert)
                    try:
                        del on_hold[alertid]
                    except KeyError:
                        continue

            if keep_alive >= 10:
                try:
                    origin = '{}/{}'.format('alerta-mailer', OPTIONS['smtp_host'])
                    api.heartbeat(origin, tags=[__version__])
                except Exception as e:
                    time.sleep(5)
                    continue
                keep_alive = 0
            keep_alive += 1
            time.sleep(2)

    def _rule_matches(self, regex, value):
        '''Checks if a rule matches the regex to
        its provided value considering its type
        '''
        if isinstance(value, list):
            LOG.debug('%s is a list, at least one item must match %s',
                      value, regex)
            for item in value:
                if re.match(regex, item) is not None:
                    LOG.debug('Regex %s matches item %s', regex, item)
                    return True
            LOG.debug('Regex %s matches nothing', regex)
            return False
        elif isinstance(value, six.string_types):  # pylint: disable=undefined-variable
            LOG.debug('Trying to match %s to %s',
                      value, regex)
            return re.search(regex, value) is not None
        LOG.warning('Field type is not supported')
        return False

    def send_email(self, alert):
        """
        Load the forward rules based on alert.customer
        """
        customer_forward_rules = get_rules_for_customer_id(alert.customer)
        LOG.info(f"Obtained {len(customer_forward_rules)} for customer {alert.customer}")
        for rule in customer_forward_rules:
            LOG.info('Evaluating rule %s', rule['name'])
            is_matching = False
            for field in rule['fields']:
                LOG.debug('Evaluating rule field %s', field)
                value = getattr(alert, field['field'], None)
                if value is None:
                    LOG.warning('Alert has no attribute %s',
                                field['field'])
                    break
                if self._rule_matches(field['regex'], value):
                    is_matching = True
                else:
                    is_matching = False
                    break
            if is_matching:
                contacts = rule["contacts"]
                subject = self._subject_template.render(alert=alert)
                text = alert.text
                msg = MIMEMultipart('alternative')
                msg['Subject'] = Header(subject, 'utf-8').encode()
                msg['From'] = OPTIONS['mail_from']
                msg['To'] = ", ".join(contacts)
                msg.preamble = msg['Subject']
                msg_text = MIMEText(text, 'plain', 'utf-8')
                msg.attach(msg_text)
                try:
                    self._send_email_message(msg, contacts)
                    LOG.debug('%s : Email sent to %s' % (alert.get_id(),
                                                         ','.join(contacts)))
                except smtplib.SMTPException as e:
                    LOG.error('Failed to send mail to %s on %s:%s : %s',
                              ", ".join(contacts),
                              OPTIONS['smtp_host'], OPTIONS['smtp_port'], e)
                except (socket.error, socket.herror, socket.gaierror) as e:
                    LOG.error('Mail server connection error: %s', e)
                except Exception as e:
                    LOG.error('Unexpected error while sending email: {}'.format(str(e)))

    def _send_email_message(self, msg, contacts):
        if OPTIONS['skip_mta'] and DNS_RESOLVER_AVAILABLE:
            for dest in contacts:
                try:
                    (_, ehost) = dest.split('@')
                    dns_answers = dns.resolver.query(ehost, 'MX')

                    if len(dns_answers) <= 0:
                        raise Exception('Failed to find mail exchange for {}'.format(dest))  # nopep8

                    mxhost = reduce(lambda x, y: x if x.preference >= y.preference else y,
                                    dns_answers).exchange.to_text()  # nopep8
                    msg['To'] = dest
                    if OPTIONS['smtp_use_ssl']:
                        mx = smtplib.SMTP_SSL(mxhost,
                                              OPTIONS['smtp_port'],
                                              local_hostname=OPTIONS['mail_localhost'],
                                              keyfile=OPTIONS['ssl_key_file'],
                                              certfile=OPTIONS['ssl_cert_file'])
                    else:
                        mx = smtplib.SMTP(mxhost,
                                          OPTIONS['smtp_port'],
                                          local_hostname=OPTIONS['mail_localhost'])
                    if OPTIONS['debug']:
                        mx.set_debuglevel(True)
                    mx.sendmail(OPTIONS['mail_from'], dest, msg.as_string())
                    mx.close()
                    LOG.debug('Sent notification email to {} (mta={})'.format(dest, mxhost))  # nopep8
                except Exception as e:
                    LOG.error('Failed to send email to address {} (mta={}): {}'.format(dest, mxhost, str(e)))  # nopep8

        else:
            if OPTIONS['smtp_use_ssl']:
                mx = smtplib.SMTP_SSL(OPTIONS['smtp_host'],
                                      OPTIONS['smtp_port'],
                                      local_hostname=OPTIONS['mail_localhost'],
                                      keyfile=OPTIONS['ssl_key_file'],
                                      certfile=OPTIONS['ssl_cert_file'])
            else:
                mx = smtplib.SMTP(OPTIONS['smtp_host'],
                                  OPTIONS['smtp_port'],
                                  local_hostname=OPTIONS['mail_localhost'])
            if OPTIONS['debug']:
                mx.set_debuglevel(True)

            mx.ehlo()

            if OPTIONS['smtp_starttls']:
                mx.starttls()

            if OPTIONS['smtp_password']:
                mx.login(OPTIONS['smtp_username'], OPTIONS['smtp_password'])

            mx.sendmail(OPTIONS['mail_from'],
                        contacts,
                        msg.as_string())
            mx.close()


def get_rules_for_customer_id(customer_id):
    postgres_connection_url = os.environ.get('POSTGRES_CONNECTION_URL')
    engine = sqlalchemy.create_engine(postgres_connection_url)
    r = engine.execute(f"select * from customer_rules where customer_id='{customer_id}'")
    results = r.fetchall()
    engine.dispose()
    rules_d = []
    for result in results:
        rules_d.extend([json.loads(s) for s in result.rules])
    return rules_d


def on_sigterm(x, y):
    raise SystemExit


def main():
    # Registering action for SIGTERM signal handling
    signal.signal(signal.SIGTERM, on_sigterm)

    try:
        mailer = MailSender()
        mailer.start()
    except (SystemExit, KeyboardInterrupt):
        sys.exit(0)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    from kombu.utils.debug import setup_logging
    loginfo = 'DEBUG' if OPTIONS['debug'] else 'INFO'
    setup_logging(loglevel=loginfo, loggers=[''])
    with Connection(OPTIONS['amqp_url']) as conn:
        try:
            consumer = FanoutConsumer(connection=conn)
            consumer.run()
        except (SystemExit, KeyboardInterrupt):
            mailer.should_stop = True
            mailer.join()
            sys.exit(0)
        except Exception as e:
            print(str(e))
            sys.exit(1)


if __name__ == '__main__':
    main()
