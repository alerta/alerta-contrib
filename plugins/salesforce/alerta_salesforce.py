import fcntl
import hashlib
import logging
import time
from contextlib import contextmanager

from cachetools import TTLCache

from requests import Session
from requests.exceptions import ConnectionError as RequestsConnectionError

from simple_salesforce import Salesforce
from simple_salesforce import exceptions as sf_exceptions

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

from alerta.plugins import PluginBase


STATE_MAP = {
    'OK': '060 Informational',
    'UP': '060 Informational',
    'INFORMATIONAL': '060 Informational',
    'UNKNOWN': '070 Unknown',
    'WARNING': '080 Warning',
    'MINOR': '080 Warning',
    'MAJOR': '090 Critical',
    'CRITICAL': '090 Critical',
    'DOWN': '090 Critical',
    'UNREACHABLE': '090 Critical',
}

CONFIG_FIELD_MAP = {
    'auth_url': 'instance_url',
    'username': 'username',
    'password': 'password',
    'organization_id': 'organizationId',
    'environment_id': 'environment_id',
    'sandbox_enabled': 'domain',
    'feed_enabled': 'feed_enabled',
    'hash_func': 'hash_func',
}


ALLOWED_HASHING = ('md5', 'sha256')
SESSION_FILE = '/tmp/session'

SALESFORCE_CONFIG = 'temp_configuration'

LOG = logging.getLogger('alerta.plugins.salesforce')
LOG.setLevel(logging.DEBUG)

@contextmanager
def flocked(fd):
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    except IOError:
        LOG.info('Session file locked. Waiting 5 seconds...')
        time.sleep(5)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)


def sf_auth_retry(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except sf_exceptions.SalesforceExpiredSession:
            LOG.warning('Salesforce session expired.')
            self.auth()
        except RequestsConnectionError:
            LOG.error('Salesforce connection error.')
            self.auth()
        return method(self, *args, **kwargs)
    return wrapper


class SfNotifierError(Exception):
    pass

class SFIntegration(PluginBase):
    def pre_receive(self, alert):
        # TODO
        return alert
    
    def post_receive(self, alert):
        self.client.create_case(alert.event, alert.text, alert.serialize)
        return

    def status_change(self, alert):
        # TODO
        return alert

    def take_action(self, alert, action, text):
        # need some logic to determine which is the appropriate environment from the config file to use
        LOG.debug("SFDC take_action function reached")
        try:
            configValues = {
                'AUTH_URL': app.config.get('SFDC_AUTH_URL'),
                'USERNAME': app.config.get('SFDC_USERNAME'),
                'PASSWORD': app.config.get('SFDC_PASSWORD'),
                'ORGANIZATION_ID': app.config.get('SFDC_ORGANIZATION_ID'),
                'ENVIRONMENT_ID': app.config.get('SFDC_ENVIRONMENT_ID'),
                'SANDBOX_ENABLED': app.config.get('SFDC_SANDBOX_ENABLED'),
                'FEED_ENABLED': app.config.get('SFDC_FEED_ENABLED'),
                'HASH_FUNC': app.config.get('SFDC_HASH_FUNC')
            }
            LOG.debug("SFDC values read for environment %s", configValues['ENVIRONMENT_ID'])
        except Exception as e:
            LOG.error(e)
        self.client = SalesforceClient(configValues)
        return alert, action, text

class SalesforceClient(object):
    def __init__(self, config):
        self.metrics = {
            'sf_auth_ok': False,
            'sf_error_count': 0,
            'sf_request_count': 0
        }
        self._registered_alerts = TTLCache(maxsize=2048, ttl=300)

        self.config = self._validate_config(config)
        self.hash_func = self._hash_func(self.config.pop('hash_func'))
        self.feed_enabled = self.config.pop('feed_enabled')

        self.environment = self.config.pop('environment_id')
        self.sf = None
        self.session = Session()
        self.auth(no_retry=True)
        LOG.debug("SFDC client initialized")

    @staticmethod
    def _hash_func(name):
        if name in ALLOWED_HASHING:
            return getattr(hashlib, name)
        msg = ('Invalid hashing function "{}".'
               'Switching to default "sha256".').format(name)
        LOG.warn(msg)
        return hashlib.sha256

    @staticmethod
    def _validate_config(config):
        kwargs = {}

        for param, value in config.items():
            field = CONFIG_FIELD_MAP.get(param.lower())
            if field is None:
                # env_var = 'SFDC_{}'.format(param)
                msg = ('Invalid config: missing "{}" field or "{}" environment'
                       ' variable.').format(field, param)
                LOG.error(msg)
                raise SfNotifierError(msg)

            kwargs[field] = value

            if field == 'domain':
                if value:
                    kwargs[field] = 'test'
                else:
                    del kwargs[field]

        return kwargs

    def _auth(self, config):
        try:
            config.update({'session': self.session})
            self.sf = Salesforce(**config)
        except Exception as ex:
            LOG.error('Salesforce authentication failure: {}.'.format(ex))
            self.metrics['sf_auth_ok'] = False
            return False

        LOG.info('Salesforce authentication successful.')
        self.metrics['sf_auth_ok'] = True
        return True

    def _load_session(self, session_file):
        lines = session_file.readlines()

        if lines == []:
            return
        return lines[0]

    def _refresh_ready(self, saved_session):
        if saved_session is None:
            LOG.info('Current session is None.')
            return True

        if self.sf is None:
            return False

        if self.sf.session_id == saved_session:
            return True
        return False

    def _reuse_session(self, saved_session):
        LOG.info('Reusing session id from file.')
        # limit params to avoid login request
        config = {
            'session_id': saved_session,
            'instance_url': self.config['instance_url']
        }
        return self._auth(config)

    def _acquire_session(self):
        # only one worker at a time can check session_file
        auth_success = False

        LOG.info('Attempting to lock session file.')
        with open(SESSION_FILE, 'r+') as session_file:
            with flocked(session_file):
                LOG.info('Successfully locked session file for refresh.')

                saved_session = self._load_session(session_file)

                if self._refresh_ready(saved_session):
                    LOG.info('Attempting to refresh session.')

                    if self._auth(self.config):
                        auth_success = True
                        session_file.truncate(0)
                        session_file.seek(0)
                        session_file.write(self.sf.session_id)
                        LOG.info('Refreshed session successfully.')
                    else:
                        LOG.error('Failed to refresh session.')
                else:
                    LOG.info('Not refreshing. Reusing session.')
                    auth_success = self._reuse_session(saved_session)

        if auth_success is False:
            LOG.warn('Waiting 30 seconds before next attempt...')
            time.sleep(30)

        return auth_success

    def auth(self, no_retry=False):
        LOG.debug("Attempting to acquire SFDC sesion")
        auth_ok = self._acquire_session()

        if no_retry:
            return

        while auth_ok is False:
            auth_ok = self._acquire_session()

    def _get_alert_id(self, labels):
        alert_id_data = ''
        for key in sorted(labels):
            alert_id_data += labels[key].replace(".", "\\.")
        return self.hash_func(alert_id_data.encode('utf-8')).hexdigest()

    @staticmethod
    def _is_watchdog(labels):
        return labels['alertname'].lower() == 'watchdog'

    @sf_auth_retry
    def _create_case(self, subject, body, labels, alert_id):

        if alert_id in self._registered_alerts:
            LOG.warning('Duplicate case for alert: {}.'.format(alert_id))
            return 1, self._registered_alerts[alert_id]['Id']

        severity = labels.get('severity', 'unknown').upper()
        payload = {
            'Subject': subject,
            'Description': body,
            'IsMosAlert__c': 'true',
            'Alert_Priority__c': STATE_MAP.get(severity, '070 Unknown'),
            'Alert_Host__c': labels.get('host') or labels.get(
                'instance', 'UNKNOWN'
            ),
            'Alert_Service__c': labels.get('service', 'UNKNOWN')[0],
            'Environment2__c': self.environment,
            'Alert_ID__c': alert_id,
        }
        if labels.get('cluster_id') is not None:
            payload['ClusterId__c'] = labels['cluster_id']

        # if self._is_watchdog(labels):
        #     payload['IsWatchDogAlert__c'] = 'true'

        LOG.info('Try to create case: {}.'.format(payload))
        try:
            self.metrics['sf_request_count'] += 1
            case = self.sf.Case.create(payload)
            LOG.info('Created case: {}.'.format(case))
        except sf_exceptions.SalesforceMalformedRequest as ex:
            msg = ex.content[0]['message']
            err_code = ex.content[0]['errorCode']

            if err_code == 'DUPLICATE_VALUE':
                LOG.warning('Duplicate case: {}.'.format(msg))
                case_id = msg.split()[-1]
                self._registered_alerts[alert_id] = {'Id': case_id}
                return 1, case_id

            LOG.error('Cannot create case: {}.'.format(msg))
            self.metrics['sf_error_count'] += 1
            raise

        self._registered_alerts[alert_id] = {'Id': case['id']}
        return 0, case['id']

    @sf_auth_retry
    def _create_feed_item(self, subject, body, case_id):
        feed_item = {'Title': subject, 'ParentId': case_id, 'Body': body}
        LOG.debug('Creating feed item: {}.'.format(feed_item))
        return self.sf.FeedItem.create(feed_item)

    def create_case(self, subject, body, labels):
        LOG.debug("Attempting to create SFDC case")
        # alert_id = self._get_alert_id(labels)
        alert_id = labels.get('id')

        error_code, case_id = self._create_case(subject, body,
                                                labels, alert_id)

        response = {'case_id': case_id, 'alert_id': alert_id}

        if error_code == 1:
            response['status'] = 'duplicate'
        else:
            response['status'] = 'created'
            LOG.debug("SFDC #%s case created", response['case_id'])

        if self.feed_enabled or self._is_watchdog(labels):
            self._create_feed_item(subject, body, case_id)
        return response