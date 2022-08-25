import fcntl
import logging
import time
from contextlib import contextmanager

from requests import Session

from simple_salesforce import Salesforce
from simple_salesforce import exceptions as sf_exceptions

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

from alerta.plugins import PluginBase

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

SESSION_FILE = '/tmp/session'

logger = logging.getLogger(__name__)


@contextmanager
def flocked(fd):
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    except IOError:
        logger.info('Session file locked. Waiting 5 seconds...')
        time.sleep(5)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)


class SfNotifierError(Exception):
    pass


class SalesforceClient(PluginBase):
    def __init__(self, config):
        self.metrics = {
            'sf_auth_ok': False,
        }
        self.config = self._validate_config(config)

        self.environment = self.config.pop('environment_id')
        self.sf = None
        self.session = Session()
        self.auth(no_retry=True)

    @staticmethod
    def _validate_config(config):
        kwargs = {}

        for param, value in config.items():
            field = CONFIG_FIELD_MAP.get(param.lower())
            if field is None:
                env_var = 'SFDC_{}'.format(param)
                msg = ('Invalid config: missing "{}" field or "{}" environment'
                       ' variable.').format(field, env_var)
                logger.error(msg)
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
            logger.error('Salesforce authentication failure: {}.'.format(ex))
            self.metrics['sf_auth_ok'] = False
            return False

        logger.info('Salesforce authentication successful.')
        self.metrics['sf_auth_ok'] = True
        return True

    def _load_session(self, session_file):
        lines = session_file.readlines()

        if lines == []:
            return
        return lines[0]

    def _refresh_ready(self, saved_session):
        if saved_session is None:
            logger.info('Current session is None.')
            return True

        if self.sf is None:
            return False

        if self.sf.session_id == saved_session:
            return True
        return False

    def _reuse_session(self, saved_session):
        logger.info('Reusing session id from file.')
        # limit params to avoid login request
        config = {
            'session_id': saved_session,
            'instance_url': self.config['instance_url']
        }
        return self._auth(config)

    def _acquire_session(self):
        # only one worker at a time can check session_file
        auth_success = False

        logger.info('Attempting to lock session file.')
        with open(SESSION_FILE, 'r+') as session_file:
            with flocked(session_file):
                logger.info('Successfully locked session file for refresh.')

                saved_session = self._load_session(session_file)

                if self._refresh_ready(saved_session):
                    logger.info('Attempting to refresh session.')

                    if self._auth(self.config):
                        auth_success = True
                        session_file.truncate(0)
                        session_file.seek(0)
                        session_file.write(self.sf.session_id)
                        logger.info('Refreshed session successfully.')
                    else:
                        logger.error('Failed to refresh session.')
                else:
                    logger.info('Not refreshing. Reusing session.')
                    auth_success = self._reuse_session(saved_session)

        if auth_success is False:
            logger.warn('Waiting 30 seconds before next attempt...')
            time.sleep(30)

        return auth_success

    def auth(self, no_retry=False):
        auth_ok = self._acquire_session()

        if no_retry:
            return

        while auth_ok is False:
            auth_ok = self._acquire_session()