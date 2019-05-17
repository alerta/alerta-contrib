import os
import json
import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger()


class DebugTracing(PluginBase):
    """
    Test plugin for debug and tracing.
    """

    def pre_receive(self, alert, **kwargs):

        LOG.info('Debug plugin - pre_receive() start.')

        DEBUG = self.get_config('DEBUG', default=False, type=bool, **kwargs)
        LOG.info('DEBUG=%s' % DEBUG)

        BOOL_VAR = self.get_config('BOOL_VAR', default=False, type=bool, **kwargs)
        INT_VAR = self.get_config('INT_VAR', default=0, type=int, **kwargs)
        FLOAT_VAR = self.get_config('FLOAT_VAR', default=0.1, type=float, **kwargs)
        LIST_VAR = self.get_config('LIST_VAR', default=['default', 'list'], type=list, **kwargs)
        STR_VAR = self.get_config('STR_VAR', default='default-string', type=str, **kwargs)
        DICT_VAR = self.get_config('DICT_VAR', default={'default': 'dict'}, type=json.loads, **kwargs)

        LOG.debug('BOOL_VAR=%s' % BOOL_VAR)
        LOG.debug('INT_VAR=%s' % INT_VAR)
        LOG.debug('FLOAT_VAR=%s' % FLOAT_VAR)
        LOG.debug('LIST_VAR=%s' % LIST_VAR)
        LOG.debug('STR_VAR=%s' % STR_VAR)
        LOG.debug('DICT_VAR=%s' % DICT_VAR)

        LOG.debug('-' * 40)
        LOG.debug(os.environ)
        LOG.debug('-' * 40)

        LOG.debug('-' * 40)
        LOG.debug(kwargs['config'])
        LOG.debug('-' * 40)

        LOG.info('Debug plugin - pre_receive() end.')

        return alert

    def post_receive(self, alert, **kwargs):

        LOG.info('Debug plugin - post_receive() start.')
        LOG.info('Debug plugin - post_receive() end.')

        return

    def status_change(self, alert, status, text, **kwargs):

        LOG.info('Debug plugin - status_change() start.')
        LOG.info('Debug plugin - status_change() end.')

        return

    def take_action(self, alert, action, text, **kwargs):

        LOG.info('Debug plugin - take_action() start.')
        LOG.info('Debug plugin - take_action() end.')

        raise NotImplementedError
