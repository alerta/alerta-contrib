
import sys
import time
import subprocess
import threading
import Queue
import re
import logging
import yaml

from alertaclient.api import ApiClient
from alertaclient.alert import Alert
from alertaclient.heartbeat import Heartbeat

__version__ = '3.2.0'

LOG = logging.getLogger('alerta.pinger')
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

PING_FILE = 'alert-pinger.targets'
PING_MAX_TIMEOUT = 15  # seconds
PING_MAX_RETRIES = 2
PING_SLOW_WARNING = 200  # ms
PING_SLOW_CRITICAL = 500  # ms
SERVER_THREAD_COUNT = 20
LOOP_EVERY = 30

_PING_ALERTS = [
    'PingFailed',
    'PingSlow',
    'PingOK',
    'PingError',
]

PING_OK = 0       # all ping replies received within timeout
PING_FAILED = 1   # some or all ping replies not received or did not respond within timeout
PING_ERROR = 2    # unspecified error with ping


# Initialise Rules
def init_targets():

    targets = list()
    LOG.info('Loading Ping targets...')
    try:
        targets = yaml.load(open(PING_FILE))
    except Exception, e:
        LOG.error('Failed to load Ping targets: %s', e)
    LOG.info('Loaded %d Ping targets OK', len(targets))

    return targets


class WorkerThread(threading.Thread):

    def __init__(self, api, queue):

        threading.Thread.__init__(self)
        LOG.debug('Initialising %s...', self.getName())

        self.last_event = {}
        self.queue = queue   # internal queue
        self.api = api               # message broker

    def run(self):

        while True:
            LOG.debug('Waiting on input queue...')
            item = self.queue.get()

            if not item:
                LOG.info('%s is shutting down.', self.getName())
                break

            environment, service, resource, retries, queue_time = item

            if time.time() - queue_time > LOOP_EVERY:
                LOG.warning('Ping request to %s expired after %d seconds.', resource, int(time.time() - queue_time))
                self.queue.task_done()
                continue

            LOG.info('%s pinging %s...', self.getName(), resource)
            if retries > 1:
                rc, rtt, loss, stdout = self.pinger(resource, count=2, timeout=5)
            else:
                rc, rtt, loss, stdout = self.pinger(resource, count=5, timeout=PING_MAX_TIMEOUT)

            if rc != PING_OK and retries:
                LOG.info('Retrying ping %s %s more times', resource, retries)
                self.queue.put((environment, service, resource, retries - 1, time.time()))
                self.queue.task_done()
                continue

            if rc == PING_OK:
                avg, max = rtt
                if avg > PING_SLOW_CRITICAL:
                    event = 'PingSlow'
                    severity = 'critical'
                    text = 'Node responded to ping in %s ms avg (> %s ms)' % (avg, PING_SLOW_CRITICAL)
                elif avg > PING_SLOW_WARNING:
                    event = 'PingSlow'
                    severity = 'warning'
                    text = 'Node responded to ping in %s ms avg (> %s ms)' % (avg, PING_SLOW_WARNING)
                else:
                    event = 'PingOK'
                    severity = 'normal'
                    text = 'Node responding to ping avg/max %s/%s ms.' % tuple(rtt)
                value = '%s/%s ms' % tuple(rtt)
            elif rc == PING_FAILED:
                event = 'PingFailed'
                severity = 'major'
                text = 'Node did not respond to ping or timed out within %s seconds' % PING_MAX_TIMEOUT
                value = '%s%% packet loss' % loss
            elif rc == PING_ERROR:
                event = 'PingError'
                severity = 'warning'
                text = 'Could not ping node %s.' % resource
                value = stdout
            else:
                LOG.warning('Unknown ping return code: %s', rc)
                continue

            # Defaults
            resource += ':icmp'
            group = 'Ping'
            correlate = _PING_ALERTS
            raw_data = stdout

            pingAlert = Alert(
                resource=resource,
                event=event,
                correlate=correlate,
                group=group,
                value=value,
                severity=severity,
                environment=environment,
                service=service,
                text=text,
                event_type='serviceAlert',
                tags=None,
                raw_data=raw_data,
            )

            try:
                r = self.api.send(pingAlert)
                LOG.debug(r)
            except Exception, e:
                LOG.warning('Failed to send alert: %s', e)

            self.queue.task_done()
            LOG.info('%s ping %s complete.', self.getName(), resource)

        self.queue.task_done()

    @staticmethod
    def pinger(node, count=1, interval=1, timeout=5):

        if timeout <= count * interval:
            timeout = count * interval + 1
        if timeout > PING_MAX_TIMEOUT:
            timeout = PING_MAX_TIMEOUT

        if sys.platform == "darwin":
            cmd = "ping -q -c %s -i %s -t %s %s" % (count, interval, timeout, node)
        else:
            cmd = "ping -q -c %s -i %s -w %s %s" % (count, interval, timeout, node)
        ping = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = ping.communicate()[0].rstrip('\n')
        rc = ping.returncode
        LOG.debug('Ping %s => %s (rc=%d)', cmd, stdout, rc)

        m = re.search('(?P<loss>\d+(\.\d+)?)% packet loss', stdout)
        if m:
            loss = m.group('loss')
        else:
            loss = 'n/a'

        m = re.search('(?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+)/(?P<mdev>\d+\.\d+)\s+ms', stdout)
        if m:
            rtt = (float(m.group('avg')), float(m.group('max')))
        else:
            rtt = (0, 0)

        if rc == 0:
            LOG.info('%s: is alive %s', node, rtt)
        else:
            LOG.info('%s: not responding', node)

        return rc, rtt, loss, stdout


class PingerDaemon(object):

    def __init__(self):

        self.shuttingdown = False

    def run(self):

        self.running = True

        # Create internal queue
        self.queue = Queue.Queue()

        self.api = ApiClient()

        # Initialiase ping targets
        ping_list = init_targets()

        # Start worker threads
        LOG.debug('Starting %s worker threads...', SERVER_THREAD_COUNT)
        for i in range(SERVER_THREAD_COUNT):
            w = WorkerThread(self.api, self.queue)
            try:
                w.start()
            except Exception, e:
                LOG.error('Worker thread #%s did not start: %s', i, e)
                continue
            LOG.info('Started worker thread: %s', w.getName())

        while not self.shuttingdown:
            try:
                for p in ping_list:
                    if 'targets' in p and p['targets']:
                        for target in p['targets']:
                            environment = p['environment']
                            service = p['service']
                            retries = p.get('retries', PING_MAX_RETRIES)
                            self.queue.put((environment, service, target, retries, time.time()))

                LOG.debug('Send heartbeat...')
                heartbeat = Heartbeat(tags=[__version__])
                try:
                    self.api.send(heartbeat)
                except Exception, e:
                    LOG.warning('Failed to send heartbeat: %s', e)

                time.sleep(LOOP_EVERY)
                LOG.info('Ping queue length is %d', self.queue.qsize())

            except (KeyboardInterrupt, SystemExit):
                self.shuttingdown = True

        LOG.info('Shutdown request received...')
        self.running = False

        for i in range(SERVER_THREAD_COUNT):
            self.queue.put(None)
        w.join()


def main():

    pinger = PingerDaemon()
    pinger.run()

if __name__ == '__main__':
    main()
