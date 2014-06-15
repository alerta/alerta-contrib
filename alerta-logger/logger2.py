
import json
import requests
import logging
import settings

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from alerta.alert import AlertDocument


LOG = logging.getLogger(__name__)

from kombu.log import get_logger
logger = get_logger(__name__)


class Worker(ConsumerMixin):

    def __init__(self, connection):

        logger.info('init')

        self.connection = connection
        self.exchange = Exchange(settings.AMQP_TOPIC, type='fanout', channel=self.connection.channel(), durable=True)
        self.queue = Queue('', exchange=self.exchange, routing_key='', channel=self.connection.channel(), exclusive=True)

    def get_consumers(self, Consumer, channel):

        logger.info(self.exchange)
        logger.info(self.queue)

        return [
            Consumer(queues=[self.queue], accept=['pickle', 'json'], callbacks=[self.on_message])
        ]

    def on_message(self, body, message):

        print("Received: %s" % body)
        try:
            logAlert = AlertDocument.parse_alert(body)
        except ValueError:
            return

        if logAlert:
            source_host, _, source_path = logAlert.resource.partition(':')
            document = {
                '@message': logAlert.text,
                '@source': logAlert.resource,
                '@source_host': source_host,
                '@source_path': source_path,
                '@tags': logAlert.tags,
                '@timestamp': logAlert.get_date('last_receive_time'),
                '@type': logAlert.event_type,
                '@fields': logAlert.get_body()
            }
            print('Index payload %s' % document)

            index_url = settings.ES_URL + "/%s/%s" % (logAlert.last_receive_time.strftime(settings.ES_INDEX), logAlert.event_type)
            print('Index URL: %s' % index_url)

            try:
                response = urllib2.urlopen(index_url, json.dumps(document)).read()
            except Exception, e:
                LOG.error('%s : Alert indexing to %s failed - %s', logAlert.last_receive_id, index_url, e)
                return

            try:
                es_id = json.loads(response)['_id']
                LOG.info('%s : Alert indexed at %s/%s', logAlert.last_receive_id, index_url, es_id)
            except Exception, e:
                LOG.error('%s : Could not parse elasticsearch reponse: %s', e)

        message.ack()

if __name__ == '__main__':
    from kombu.utils.debug import setup_logging
    # setup root logger
    setup_logging(loglevel='DEBUG', loggers=[''])
    with Connection(settings.AMQP_URL) as conn:
        try:
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
            print 'Exiting...'