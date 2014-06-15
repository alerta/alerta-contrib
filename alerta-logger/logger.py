
import time
import threading
import json
import urllib2

from alerta.common.api import ApiClient
from alerta.common.amqp import Messaging, FanoutConsumer
from alerta.common.alert import AlertDocument
from alerta.common.heartbeat import Heartbeat
from alerta.common.utils import DateEncoder

import logging

__version__ = '3.1.0'

ES_URL = "http://localhost:9200"


class LoggerMessage(FanoutConsumer, threading.Thread):

    def __init__(self):

        mq = Messaging()
        self.connection = mq.connection

        FanoutConsumer.__init__(self, self.connection)
        threading.Thread.__init__(self)

    def on_message(self, body, message):

        logging.debug("Received: %s", body)
        try:
            logAlert = AlertDocument.parse_alert(body)
        except ValueError:
            return

        if logAlert:
            logging.info('%s : [%s] %s', logAlert.last_receive_id, logAlert.status, logAlert.text)

            source_host, _, source_path = logAlert.resource.partition(':')
            document = {
                '@message': logAlert.text,
                '@source': logAlert.resource,
                '@source_host': source_host,
                '@source_path': source_path,
                '@tags': logAlert.tags,
                '@timestamp': logAlert.last_receive_time,
                '@type': logAlert.event_type,
                '@fields': logAlert.get_body()
            }
            logging.debug('Index payload %s', document)

            index_url = ES_URL + "/%s/%s" % (logAlert.last_receive_time.strftime(CONF.es_index), logAlert.event_type)
            logging.debug('Index URL: %s', index_url)

            try:
                response = urllib2.urlopen(index_url, json.dumps(document, cls=DateEncoder)).read()
            except Exception, e:
                logging.error('%s : Alert indexing to %s failed - %s', logAlert.last_receive_id, index_url, e)
                return

            try:
                es_id = json.loads(response)['_id']
                logging.info('%s : Alert indexed at %s/%s', logAlert.last_receive_id, index_url, es_id)
            except Exception, e:
                logging.error('%s : Could not parse elasticsearch reponse: %s', e)

        message.ack()


class LoggerDaemon(Daemon):

    logger_opts = {
        'es_host': 'localhost',
        'es_port': 9200,
        'es_index': 'alerta-%Y.%m.%d',  # NB. Kibana config must match this index
    }

    def __init__(self, prog, **kwargs):

        config.register_opts(LoggerDaemon.logger_opts)

        Daemon.__init__(self, prog, kwargs)

    def run(self):

        logger = LoggerMessage()
        logger.start()

        self.api = ApiClient()

        try:
            while True:
                LOG.debug('Send heartbeat...')
                heartbeat = Heartbeat(tags=[__version__])
                try:
                    self.api.send(heartbeat)
                except Exception, e:
                    LOG.warning('Failed to send heartbeat: %s', e)
                time.sleep(CONF.loop_every)
        except (KeyboardInterrupt, SystemExit):
            logger.should_stop = True


if __name__ == '__main__':
    config.parse_args(version=__version__)
    logging.setup('alerta')
    logger = LoggerDaemon('alert-logger')
    logger.start()
