#!/usr/bin/env python

import os
import sys
import time
import threading
import logging
import smtplib
import socket
import datetime
import json
import jinja2

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from alerta.api import ApiClient
from alerta.alert import AlertDocument
from alerta.heartbeat import Heartbeat

LOG = logging.getLogger(__name__)
root = logging.getLogger()

OPTIONS = {
    'config_file':   '~/.alerta.conf',
    'profile':       None,
    'endpoint':      'http://localhost:8080',
    'key':           '',
    'amqp_url':      'redis://localhost:6379/',
    'amqp_topic':    'notify',
    'smtp_host':     'smtp.gmail.com',
    'smtp_port':     587,
    'smtp_password': '',  # application-specific password if gmail used
    'mail_from':     '',  # alerta@example.com
    'mail_to':       [],  # devops@example.com, support@example.com
    'dashboard_url': 'http://try.alerta.io',
    'debug':         False
}

HOLD_TIME = 30  # seconds (hold alert until sending, delete if cleared before end of hold time)

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
                name='',
                exchange=exchange,
                routing_key='',
                channel=self.channel,
                exclusive=True
            )
        ]

        return [
            Consumer(queues=queues, accept=['json'], callbacks=[self.on_message])
        ]

    def on_message(self, body, message):

        try:
            alert = AlertDocument.parse_alert(json.loads(body))
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

        if alert.severity not in ['critical', 'major'] and alert.previous_severity not in ['critical', 'major']:
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
        super(MailSender, self).__init__()

    def run(self):

        api = ApiClient()
        keep_alive = 0

        while not self.should_stop:
            for alertid in on_hold.keys():
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
                api.send(Heartbeat(tags=[OPTIONS['smtp_host']]))
                keep_alive = 0
            keep_alive += 1
            time.sleep(2)

    def send_email(self, alert):

        # email subject
        subject = '[%s] %s: %s %s on %s %s' % (
            alert.status.capitalize(),
            alert.environment,
            alert.severity.capitalize(),
            alert.event,
            ','.join(alert.service),
            alert.resource
        )

        # email body
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True
        )
        context = {
            'alert': alert,
            'mail_to': OPTIONS['mail_to'],
            'dashboard_url': OPTIONS['dashboard_url'],
            'program': os.path.basename(sys.argv[0]),
            'hostname': os.uname()[1],
            'now': datetime.datetime.utcnow()
        }
        template = env.get_template('email.tmpl')
        text = template.render(context)

        msg = MIMEMultipart('related')
        msg['Subject'] = subject
        msg['From'] = OPTIONS['mail_from']
        msg['To'] = ", ".join(OPTIONS['mail_to'])
        msg.preamble = subject

        msg_text = MIMEText(text, 'plain', 'utf-8')
        msg.attach(msg_text)

        try:
            mx = smtplib.SMTP(OPTIONS['smtp_host'], OPTIONS['smtp_port'])
            if OPTIONS['debug']:
                mx.set_debuglevel(True)
            mx.ehlo()
            mx.starttls()
            mx.login(OPTIONS['mail_from'], OPTIONS['smtp_password'])
            mx.sendmail(OPTIONS['mail_from'], OPTIONS['mail_to'], msg.as_string())
            mx.close()
        except (socket.error, socket.herror, socket.gaierror), e:
            LOG.error('Mail server connection error: %s', e)
            return
        except smtplib.SMTPException, e:
            LOG.error('Failed to send mail to %s on %s:%s : %s',
                          ", ".join(OPTIONS['mail_to']), OPTIONS['smtp_host'], OPTIONS['smtp_port'], e)
        except Exception as e:
            print str(e)

        LOG.info('%s : Email sent to %s' % (alert.get_id(), ','.join(OPTIONS['mail_to'])))


def main():

    config_file = os.environ.get('ALERTA_CONF_FILE') or OPTIONS['config_file']

    config = configparser.RawConfigParser(defaults=OPTIONS)
    try:
        config.read(os.path.expanduser(config_file))
    except Exception as e:
        LOG.warning("Problem reading configuration file %s - is this an ini file?", config_file)
        sys.exit(1)

    if config.has_section('alerta-mailer'):
        for opt in OPTIONS:
            OPTIONS[opt] = config.get('alerta-mailer', opt)

    OPTIONS['endpoint'] = os.environ.get('ALERTA_ENDPOINT') or OPTIONS['endpoint']
    OPTIONS['key'] = os.environ.get('ALERTA_API_KEY') or OPTIONS['key']
    OPTIONS['smtp_password'] = os.environ.get('SMTP_PASSWORD') or OPTIONS['smtp_password']
    OPTIONS['debug'] = os.environ.get('DEBUG') or OPTIONS['debug']

    # ensure mail_to is a list of email destinations
    try:
        OPTIONS['mail_to'] = OPTIONS['mail_to'].split(',')
    except AttributeError:
        pass

    try:
        mailer = MailSender()
        mailer.start()
    except (SystemExit, KeyboardInterrupt):
        sys.exit(0)
    except Exception as e:
        print str(e)
        sys.exit(1)

    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='DEBUG' if OPTIONS['debug'] else 'INFO', loggers=[''])

    with Connection(OPTIONS['amqp_url']) as conn:
        try:
            consumer = FanoutConsumer(connection=conn)
            consumer.run()
        except (SystemExit, KeyboardInterrupt):
            mailer.should_stop = True
            mailer.join()
            sys.exit(0)
        except Exception as e:
            print str(e)
            sys.exit(1)

if __name__ == '__main__':
    main()
