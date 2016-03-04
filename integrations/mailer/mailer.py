#!/usr/bin/env python

import datetime
import logging
import os
import re
import smtplib
import socket
import sys
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jinja2

from alerta.alert import AlertDocument
from alerta.api import ApiClient
from alerta.heartbeat import Heartbeat
from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin

DNS_RESOLVER_AVAILABLE = False

try:
    import dns.resolver
    DNS_RESOLVER_AVAILABLE = True
except:
    sys.stdout.write('Python dns.resolver unavailable. The skip_mta option will be forced to False')  # nopep8

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


logging.basicConfig()
LOG = logging.getLogger(__name__)
root = logging.getLogger()

DEFAULT_OPTIONS = {
    'config_file':   '~/.alerta.conf',
    'profile':       None,
    'endpoint':      'http://localhost:8080',
    'key':           '',
    'amqp_url':      'redis://localhost:6379/',
    'amqp_topic':    'notify',
    'smtp_host':     'smtp.gmail.com',
    'smtp_port':     587,
    'smtp_password': '',  # application-specific password if gmail used
    'smtp_starttls': True,  # use the STARTTLS SMTP extension
    'mail_from':     '',  # alerta@example.com
    'mail_to':       [],  # devops@example.com, support@example.com
    'mail_localhost': None,  # fqdn to use in the HELO/EHLO command
    'mail_template':  os.path.dirname(__file__) + os.sep + 'email.tmpl',
    'mail_template_html': os.path.dirname(__file__) + os.sep + 'email.html.tmpl',  # nopep8
    'mail_subject':  ('[{{ alert.status|capitalize }}] {{ alert.environment }}: '
                      '{{ alert.severity|capitalize }} {{ alert.event }} on '
                      '{{ alert.service|join(\',\') }} {{ alert.resource }}'),
    'dashboard_url': 'http://try.alerta.io',
    'debug':         False,
    'skip_mta':      False,
    'email_type':    'text'  # options are: text, html
}

OPTIONS = {}

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
                name='',
                exchange=exchange,
                routing_key='',
                channel=self.channel,
                exclusive=True
            )
        ]

        return [
            Consumer(queues=queues, accept=['json'],
                     callbacks=[self.on_message])
        ]

    def on_message(self, body, message):

        try:
            alert = AlertDocument.parse_alert(body)
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
            alert.severity not in ['critical', 'major'] and
            alert.previous_severity not in ['critical', 'major']
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
        self._template_dir = os.path.dirname(
            os.path.realpath(OPTIONS['mail_template']))
        self._template_name = os.path.basename(OPTIONS['mail_template'])
        self._subject_template = jinja2.Template(OPTIONS['mail_subject'])
        self._template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self._template_dir),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True
        )
        if OPTIONS['mail_template_html']:
            self._template_name_html = os.path.basename(
                OPTIONS['mail_template_html'])

        super(MailSender, self).__init__()

    def run(self):

        api = ApiClient(endpoint=OPTIONS['endpoint'], key=OPTIONS['key'])
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
                tag = OPTIONS['smtp_host'] or 'alerta-mailer'
                api.send(Heartbeat(tags=[tag]))
                keep_alive = 0
            keep_alive += 1
            time.sleep(2)

    def send_email(self, alert):
        """Attempt to send an email for the provided alert, compiling
        the subject and text template and using all the other smtp settings
        that were specified in the configuration file
        """
        contacts = list(OPTIONS['mail_to'])
        LOG.debug('Initial contact list: %s' % (contacts))
        if 'group_rules' in OPTIONS and len(OPTIONS['group_rules']) > 0:
            LOG.debug('Checking %d group rules' % len(OPTIONS['group_rules']))
            for rules in OPTIONS['group_rules']:
                LOG.debug('Matching regex %s to %s (%s)' % (rules['regex'],
                         rules['field'], eval(rules['field'])))
                if re.match(rules['regex'], eval(rules['field'])):
                    LOG.debug('Regex matched')
                    # Add up any new contacts
                    new_contacts = [x.strip() for x in rules['contacts'].split(',')
                                    if x.strip() not in contacts]
                    if len(new_contacts) > 0:
                        LOG.debug('Extending contact to include %s' % (new_contacts))
                        contacts.extend(new_contacts)
                else:
                    LOG.debug('regex did not match')

        template_vars = {
            'alert': alert,
            'mail_to': contacts,
            'dashboard_url': OPTIONS['dashboard_url'],
            'program': os.path.basename(sys.argv[0]),
            'hostname': os.uname()[1],
            'now': datetime.datetime.utcnow()
        }

        subject = self._subject_template.render(alert=alert)
        text = self._template_env.get_template(
            self._template_name).render(**template_vars)

        if (
            OPTIONS['email_type'] == 'html' and
            self._template_name_html
        ):
            html = self._template_env.get_template(
                self._template_name_html).render(**template_vars)
        else:
            html = None

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = OPTIONS['mail_from']
        msg['To'] = ", ".join(contacts)
        msg.preamble = subject

        # by default we are going to assume that the email is going to be text
        msg_text = MIMEText(text, 'plain', 'utf-8')
        if html:
            msg_html = MIMEText(html, 'html', 'utf-8')
            msg.attach(msg_html)

        msg.attach(msg_text)

        try:
            self._send_email_message(msg, contacts)
            LOG.debug('%s : Email sent to %s' % (alert.get_id(),
                                                 ','.join(contacts)))
        except (socket.error, socket.herror, socket.gaierror), e:
            LOG.error('Mail server connection error: %s', e)
            return
        except smtplib.SMTPException, e:
            LOG.error('Failed to send mail to %s on %s:%s : %s',
                      ", ".join(contacts),
                      OPTIONS['smtp_host'], OPTIONS['smtp_port'], e)
        except Exception as e:
            LOG.error('Unexpected error while sending email: {}'.format(str(e)))  # nopep8

    def _send_email_message(self, msg, contacts):
        if OPTIONS['skip_mta'] and DNS_RESOLVER_AVAILABLE:
            for dest in contacts:
                try:
                    (_, ehost) = dest.split('@')
                    dns_answers = dns.resolver.query(ehost, 'MX')

                    if len(dns_answers) <= 0:
                        raise Exception('Failed to find mail exchange for {}'.format(dest))  # nopep8

                    mxhost = reduce(lambda x, y: x if x.preference >= y.preference else y, dns_answers).exchange.to_text()  # nopep8
                    msg['To'] = dest
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
            mx = smtplib.SMTP(OPTIONS['smtp_host'],
                              OPTIONS['smtp_port'],
                              local_hostname=OPTIONS['mail_localhost'])
            if OPTIONS['debug']:
                mx.set_debuglevel(True)

            mx.ehlo()

            if OPTIONS['smtp_starttls']:
                mx.starttls()

            if OPTIONS['smtp_password']:
                mx.login(OPTIONS['mail_from'], OPTIONS['smtp_password'])

            mx.sendmail(OPTIONS['mail_from'],
                        contacts,
                        msg.as_string())
            mx.close()


def parse_group_rules(config):
    notifications = [x for x in config.sections()
                     if 'notification' == x.split(':')[0]]
    rules = []

    for notification in notifications:
        regex = config.get(notification, 'regex')
        contacts = config.get(notification, 'contacts')
        field = config.get(notification, 'field')
        rules.append({'regex': regex, 'contacts': contacts, 'field': field})

    return rules


def main():
    global OPTIONS

    CONFIG_SECTION = 'alerta-mailer'
    config_file = os.environ.get('ALERTA_CONF_FILE') or DEFAULT_OPTIONS['config_file']  # nopep8

    # Convert default booleans to its string type, otherwise config.getboolean fails  # nopep8
    defopts = {k: str(v) if type(v) is bool else v for k, v in DEFAULT_OPTIONS.iteritems()}  # nopep8
    config = configparser.RawConfigParser(defaults=defopts)

    if os.path.exists("{}.d".format(config_file)):
        config_path = "{}.d".format(config_file)
        config_list = []
        for files in os.walk(config_path):
            for filename in files[2]:
                config_list.append("{}/{}".format(config_path, filename))

        config_list.append(os.path.expanduser(config_file))
        config_file = config_list

    try:
        config.read(config_file)
    except Exception as e:
        LOG.warning("Problem reading configuration file %s - is this an ini file?", config_file)  # nopep8
        sys.exit(1)

    if config.has_section(CONFIG_SECTION):
        from types import NoneType
        config_getters = {
            NoneType: config.get,
            str: config.get,
            int: config.getint,
            float: config.getfloat,
            bool: config.getboolean,
            list: lambda s, o: [e.strip() for e in config.get(s, o).split(',')]
        }
        for opt in DEFAULT_OPTIONS:
            # Convert the options to the expected type
            OPTIONS[opt] = config_getters[type(DEFAULT_OPTIONS[opt])](CONFIG_SECTION, opt)  # nopep8
    else:
        sys.stderr.write('Alerta configuration section not found in configuration file\n')  # nopep8
        OPTIONS = defopts.copy()

    OPTIONS['endpoint'] = os.environ.get('ALERTA_ENDPOINT') or OPTIONS['endpoint']  # nopep8
    OPTIONS['key'] = os.environ.get('ALERTA_API_KEY') or OPTIONS['key']
    OPTIONS['smtp_password'] = os.environ.get('SMTP_PASSWORD') or OPTIONS['smtp_password']  # nopep8
    if os.environ.get('DEBUG'):
        OPTIONS['debug'] = True

    OPTIONS['group_rules'] = parse_group_rules(config)

    try:
        mailer = MailSender()
        mailer.start()
    except (SystemExit, KeyboardInterrupt):
        sys.exit(0)
    except Exception as e:
        print str(e)
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
            print str(e)
            sys.exit(1)

if __name__ == '__main__':
    main()
