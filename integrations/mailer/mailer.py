#!/usr/bin/env python

import datetime
import json
import logging
import os
import platform
import re
import signal
import smtplib
import socket
from functools import reduce

import sys
import threading
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jinja2
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
    sys.stdout.write('Python dns.resolver unavailable. The skip_mta option will be forced to False')  # nopep8

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)
root = logging.getLogger()

DEFAULT_OPTIONS = {
    'config_file':   '~/.alerta.conf',
    'profile':       None,
    'endpoint':      'http://localhost:8080',
    'key':           '',
    'amqp_url':      'redis://localhost:6379/',
    'amqp_topic':    'notify',
    'amqp_queue_name':    '', # Name of the AMQP queue. Default is no name (default queue destination).
    'amqp_queue_exclusive': True, # Exclusive queues may only be consumed by the current connection.
    'smtp_host':     'smtp.gmail.com',
    'smtp_port':     587,
    'smtp_username': '', # application-specific username if it differs from the specified 'mail_from' user
    'smtp_password': '',  # application-specific password if gmail used
    'smtp_starttls': True,  # use the STARTTLS SMTP extension
    'smtp_use_ssl': False,  # whether or not SSL is being used for the SMTP connection
    'ssl_key_file': None, # a PEM formatted private key file for the SSL connection
    'ssl_cert_file': None, # a certificate chain file for the SSL connection
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
        elif isinstance(value, str) or isinstance(value, unicode):  # pylint: disable=undefined-variable
            LOG.debug('Trying to match %s to %s',
                      value, regex)
            return re.search(regex, value) is not None
        LOG.warning('Field type is not supported')
        return False

    def send_email(self, alert):
        """Attempt to send an email for the provided alert, compiling
        the subject and text template and using all the other smtp settings
        that were specified in the configuration file
        """
        contacts = list(OPTIONS['mail_to'])
        LOG.debug('Initial contact list: %s', contacts)
        if 'group_rules' in OPTIONS and len(OPTIONS['group_rules']) > 0:
            LOG.debug('Checking %d group rules' % len(OPTIONS['group_rules']))
            for rule in OPTIONS['group_rules']:
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
                        break
                if is_matching:
                    # Add up any new contacts
                    new_contacts = [x.strip() for x in rule['contacts']
                                    if x.strip() not in contacts]
                    if len(new_contacts) > 0:
                        if not rule.get('exclude', False):
                            LOG.debug('Extending contact to include %s' % (
                                new_contacts))
                            contacts.extend(new_contacts)
                        else:
                            LOG.info('Clearing initial list of contacts and'
                                     ' adding for this rule only')
                            del contacts[:]
                            contacts.extend(new_contacts)
        
        # Don't loose time (and try to send an email) if there is no contact...
        if not contacts:
            return

        template_vars = {
            'alert': alert,
            'mail_to': contacts,
            'dashboard_url': OPTIONS['dashboard_url'],
            'program': os.path.basename(sys.argv[0]),
            'hostname': platform.uname()[1],
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
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = OPTIONS['mail_from']
	if "contacts" in alert.attributes:
	    msg['To'] = alert.attributes['contacts']
	else:
            msg['To'] = ", ".join(contacts)
        msg.preamble = msg['Subject']

        # by default we are going to assume that the email is going to be text
        msg_text = MIMEText(text, 'plain', 'utf-8')
        msg.attach(msg_text)
        if html:
            msg_html = MIMEText(html, 'html', 'utf-8')
            msg.attach(msg_html)

        try:
            self._send_email_message(msg, contacts)
            LOG.debug('%s : Email sent to %s' % (alert.get_id(),
                                                 ','.join(contacts)))
            return (msg, contacts)
        except smtplib.SMTPException as e:
            LOG.error('Failed to send mail to %s on %s:%s : %s',
                      ", ".join(contacts),
                      OPTIONS['smtp_host'], OPTIONS['smtp_port'], e)
            return None
        except (socket.error, socket.herror, socket.gaierror) as e:
            LOG.error('Mail server connection error: %s', e)
            return None
        except Exception as e:
            LOG.error('Unexpected error while sending email: {}'.format(str(e)))  # nopep8
            return None

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


def validate_rules(rules):
    '''
    Validates that rules are correct
    '''
    if not isinstance(rules, list):
        LOG.warning('Invalid rules, must be list')
        return
    valid_rules = []
    for rule in rules:
        if not isinstance(rule, dict):
            LOG.warning('Invalid rule %s, must be dict', rule)
            continue
        valid = True
        # TODO: This could be optimized to use sets instead
        for key in ['name', 'fields', 'contacts']:
            if key not in rule:
                LOG.warning('Invalid rule %s, must have %s', rule, key)
                valid = False
                break
        if valid is False:
            continue
        if not isinstance(rule['fields'], list) or len(rule['fields']) == 0:
            LOG.warning('Rule fields must be a list and not empty')
            continue
        for field in rule['fields']:
            for key in ['regex', 'field']:
                if key not in field:
                    LOG.warning('Invalid rule %s, must have %s on fields',
                                rule, key)
                    valid = False
                    break
        if valid is False:
            continue

        LOG.info('Adding rule %s to list of rules to be evaluated', rule)
        valid_rules.append(rule)
    return valid_rules


def parse_group_rules(config_file):
    rules_dir = "{}/alerta.rules.d".format(os.path.dirname(config_file))
    LOG.debug('Looking for rules files in %s', rules_dir)
    if os.path.exists(rules_dir):
        rules_d = []
        for files in os.walk(rules_dir):
            for filename in files[2]:
                LOG.debug('Parsing %s', filename)
                try:
                    with open(os.path.join(files[0], filename), 'r') as f:
                        rules = validate_rules(json.load(f))
                        if rules is not None:
                            rules_d.extend(rules)
                except:
                    LOG.exception('Could not parse file')
        return rules_d
    return ()

def on_sigterm(x, y):
    raise SystemExit

def main():
    global OPTIONS

    CONFIG_SECTION = 'alerta-mailer'
    config_file = os.environ.get('ALERTA_CONF_FILE') or DEFAULT_OPTIONS['config_file']  # nopep8

    # Convert default booleans to its string type, otherwise config.getboolean fails  # nopep8
    defopts = {k: str(v) if type(v) is bool else v for k, v in DEFAULT_OPTIONS.items()}  # nopep8
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
        # No need to expanduser if we got a list (already done sooner)
        # Morever expanduser does not accept a list.
        if isinstance(config_file, list):
            config.read(config_file)
        else:
            config.read(os.path.expanduser(config_file))
    except Exception as e:
        LOG.warning("Problem reading configuration file %s - is this an ini file?", config_file)  # nopep8
        sys.exit(1)

    if config.has_section(CONFIG_SECTION):
        NoneType = type(None)
        config_getters = {
            NoneType: config.get,
            str: config.get,
            int: config.getint,
            float: config.getfloat,
            bool: config.getboolean,
            list: lambda s, o: [e.strip() for e in config.get(s, o).split(',')] if len(config.get(s, o)) else []
        }
        for opt in DEFAULT_OPTIONS:
            # Convert the options to the expected type
            OPTIONS[opt] = config_getters[type(DEFAULT_OPTIONS[opt])](CONFIG_SECTION, opt)  # nopep8
    else:
        sys.stderr.write('Alerta configuration section not found in configuration file\n')  # nopep8
        OPTIONS = defopts.copy()

    OPTIONS['endpoint'] = os.environ.get('ALERTA_ENDPOINT') or OPTIONS['endpoint']  # nopep8
    OPTIONS['key'] = os.environ.get('ALERTA_API_KEY') or OPTIONS['key']
    OPTIONS['smtp_username'] = os.environ.get('SMTP_USERNAME') or OPTIONS['smtp_username'] or OPTIONS['mail_from']
    OPTIONS['smtp_password'] = os.environ.get('SMTP_PASSWORD') or OPTIONS['smtp_password']  # nopep8

    if os.environ.get('DEBUG'):
        OPTIONS['debug'] = True

    if isinstance(config_file, list):
        group_rules = []
        for file in config_file:
            group_rules.extend(parse_group_rules(file))
    else:
        group_rules = parse_group_rules(config_file)
    if group_rules is not None:
        OPTIONS['group_rules'] = group_rules

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
