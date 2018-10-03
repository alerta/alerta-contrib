
import platform
import sys
import time
import urllib.request, urllib.error, urllib.parse
import json
import threading
import queue
import re
import logging

import datetime
import ssl
import socket

from alertaclient.api import Client

from http.server import BaseHTTPRequestHandler as BHRH

HTTP_RESPONSES = dict([(k, v[0]) for k, v in list(BHRH.responses.items())])

# Add missing responses
HTTP_RESPONSES[102] = 'Processing'
HTTP_RESPONSES[207] = 'Multi-Status'
HTTP_RESPONSES[422] = 'Unprocessable Entity'
HTTP_RESPONSES[423] = 'Locked'
HTTP_RESPONSES[424] = 'Failed Dependency'
HTTP_RESPONSES[506] = 'Variant Also Negotiates'
HTTP_RESPONSES[507] = 'Insufficient Storage'
HTTP_RESPONSES[510] = 'Not Extended'

_HTTP_ALERTS = [
    'HttpConnectionError',
    'HttpServerError',
    'HttpClientError',
    'HttpRedirection',
    'HttpContentError',
    'HttpResponseSlow',
    'HttpResponseOK',
    'HttpResponseRegexError',
    'HttpResponseRegexOK'
]

__version__ = '3.3.0'

LOOP_EVERY = 60  # seconds
#TARGET_FILE = 'urlmon.targets'  # FIXME -- or settings.py ???
SERVER_THREADS = 20
SLOW_WARNING_THRESHOLD = 5000  # ms
SLOW_CRITICAL_THRESHOLD = 10000  # ms
MAX_TIMEOUT = 15000  # ms
SSL_DAYS = 30
SSL_DAYS_PANIC = 7

import settings

LOG = logging.getLogger("alerta.urlmon")
logging.basicConfig(format="%(asctime)s - %(name)s: %(levelname)s - %(message)s", level=logging.DEBUG)


class WorkerThread(threading.Thread):

    def __init__(self, queue, api):

        threading.Thread.__init__(self)
        LOG.debug('Initialising %s...', self.getName())

        self.queue = queue   # internal queue
        self.api = api       # send alerts api

    def run(self):

        while True:
            LOG.debug('Waiting on input queue...')
            try:
                check, queue_time = self.queue.get()
            except TypeError:
                LOG.info('%s is shutting down.', self.getName())
                break

            if time.time() - queue_time > LOOP_EVERY:
                LOG.warning('URL request for %s to %s expired after %d seconds.', check['resource'], check['url'],
                            int(time.time() - queue_time))
                self.queue.task_done()
                continue

            resource = check['resource']
            LOG.info('%s polling %s...', self.getName(), resource)
            status, reason, body, rtt = self.urlmon(check)

            status_regex = check.get('status_regex', None)
            search_string = check.get('search', None)
            rule = check.get('rule', None)
            warn_thold = check.get('warning', SLOW_WARNING_THRESHOLD)
            crit_thold = check.get('critical', SLOW_CRITICAL_THRESHOLD)
            checker_api = check.get('api_endpoint', None)
            checker_apikey = check.get('api_key', None)
            check_ssl = check.get('check_ssl')
            if (checker_api and checker_apikey):
                local_api = Client(endpoint=checker_api, key=checker_apikey)
            else:
                local_api = self.api

            try:
                description = HTTP_RESPONSES[status]
            except KeyError:
                description = 'undefined'

            if not status:
                event = 'HttpConnectionError'
                severity = 'major'
                value = reason
                text = 'Error during connection or data transfer (timeout=%d).' % MAX_TIMEOUT

            elif status_regex:
                if re.search(status_regex, str(status)):
                    event = 'HttpResponseRegexOK'
                    severity = 'normal'
                    value = '%s (%d)' % (description, status)
                    text = 'HTTP server responded with status code %d that matched "%s" in %dms' % (status, status_regex, rtt)
                else:
                    event = 'HttpResponseRegexError'
                    severity = 'major'
                    value = '%s (%d)' % (description, status)
                    text = 'HTTP server responded with status code %d that failed to match "%s"' % (status, status_regex)

            elif 100 <= status <= 199:
                event = 'HttpInformational'
                severity = 'normal'
                value = '%s (%d)' % (description, status)
                text = 'HTTP server responded with status code %d in %dms' % (status, rtt)

            elif 200 <= status <= 299:
                event = 'HttpResponseOK'
                severity = 'normal'
                value = '%s (%d)' % (description, status)
                text = 'HTTP server responded with status code %d in %dms' % (status, rtt)

            elif 300 <= status <= 399:
                event = 'HttpRedirection'
                severity = 'minor'
                value = '%s (%d)' % (description, status)
                text = 'HTTP server responded with status code %d in %dms' % (status, rtt)

            elif 400 <= status <= 499:
                event = 'HttpClientError'
                severity = 'minor'
                value = '%s (%d)' % (description, status)
                text = 'HTTP server responded with status code %d in %dms' % (status, rtt)

            elif 500 <= status <= 599:
                event = 'HttpServerError'
                severity = 'major'
                value = '%s (%d)' % (description, status)
                text = 'HTTP server responded with status code %d in %dms' % (status, rtt)

            else:
                event = 'HttpUnknownError'
                severity = 'warning'
                value = 'UNKNOWN'
                text = 'HTTP request resulted in an unhandled error.'

            if event in ['HttpResponseOK', 'HttpResponseRegexOK']:
                if rtt > crit_thold:
                    event = 'HttpResponseSlow'
                    severity = 'critical'
                    value = '%dms' % rtt
                    text = 'Website available but exceeding critical RT thresholds of %dms' % crit_thold
                elif rtt > warn_thold:
                    event = 'HttpResponseSlow'
                    severity = 'warning'
                    value = '%dms' % rtt
                    text = 'Website available but exceeding warning RT thresholds of %dms' % warn_thold
                if search_string and body:
                    LOG.debug('Searching for %s', search_string)
                    found = False
                    for line in body.split('\n'):
                        m = re.search(search_string, line)
                        if m:
                            found = True
                            LOG.debug("Regex: Found %s in %s", search_string, line)
                            break
                    if not found:
                        event = 'HttpContentError'
                        severity = 'minor'
                        value = 'Search failed'
                        text = 'Website available but pattern "%s" not found' % search_string
                elif rule and body:
                    LOG.debug('Evaluating rule %s', rule)
                    headers = check.get('headers', {})
                    if 'Content-type' in headers and headers['Content-type'] == 'application/json':
                        try:
                            body = json.loads(body)
                        except ValueError as e:
                            LOG.error('Could not evaluate rule %s: %s', rule, e)
                    try:
                        eval(rule)  # NOTE: assumes request body in variable called 'body'
                    except (SyntaxError, NameError, ZeroDivisionError) as e:
                        LOG.error('Could not evaluate rule %s: %s', rule, e)
                    except Exception as e:
                        LOG.error('Could not evaluate rule %s: %s', rule, e)
                    else:
                        if not eval(rule):
                            event = 'HttpContentError'
                            severity = 'minor'
                            value = 'Rule failed'
                            text = 'Website available but rule evaluation failed (%s)' % rule

            LOG.debug("URL: %s, Status: %s (%s), Round-Trip Time: %dms -> %s",
                      check['url'], description, status, rtt, event)

            resource = check['resource']
            correlate = _HTTP_ALERTS
            group = 'Web'
            environment = check['environment']
            service = check['service']
            text = text
            tags = check.get('tags', list())
            threshold_info = "%s : RT > %d RT > %d x %s" % (check['url'], warn_thold, crit_thold, check.get('count', 1))

            try:
                local_api.send_alert(
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
                    tags=tags,
                    attributes={
                        'thresholdInfo': threshold_info
                    }
                )
            except Exception as e:
                LOG.warning('Failed to send alert: %s', e)

            if check_ssl:
                ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
                context = ssl.create_default_context()
                conn = context.wrap_socket(
                    socket.socket(socket.AF_INET),
                    server_hostname=check['url'],
                )
                conn.settimeout(3.0)
                conn.connect((check['url'], 443))
                ssl_info = conn.getpeercert()
                days_left = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt) - datetime.datetime.utcnow()
                if days_left < datetime.timedelta(days=0):
                    text = 'HTTPS cert for %s expired' % check['resource']
                    severity = 'critical'
                    send = True
                elif days_left < SSL_DAYS_PANIC:
                    text = 'HTTPS cert for %s will expire at %d' % (check['resource'], days_left)
                    severity = 'major'
                    send = True
                elif days_left < SSL_DAYS_PANIC:
                    text = 'HTTPS cert for %s will expire at %d' % (check['resource'], days_left)
                    severity = 'minor'
                    send = True
                if send:
                    try:
                        local_api.send_alert(
                            resource=resource,
                            event=event,
                            correlate=correlate,
                            group=group,
                            value='0',
                            severity=severity,
                            environment=environment,
                            service=service,
                            text=text,
                            event_type='serviceAlert',
                            tags=tags,
                            attributes={
                                'thresholdInfo': threshold_info
                            }
                        )
                    except Exception as e:
                        LOG.warning('Failed to send ssl alert: %s', e)

            self.queue.task_done()
            LOG.info('%s check complete.', self.getName())

        self.queue.task_done()

    @staticmethod
    def urlmon(check):

        url = check['url']
        post = check.get('post', None)
        count = check.get('count', 1)
        headers = check.get('headers', {})
        username = check.get('username', None)
        password = check.get('password', None)
        realm = check.get('realm', None)
        uri = check.get('uri', None)
        proxy = check.get('proxy', False)

        status = 0
        reason = None
        body = None
        rtt = 0

        while True:

            count -= 1
            start = time.time()

            if username and password:
                auth_handler = urllib.request.HTTPBasicAuthHandler()
                auth_handler.add_password(realm=realm,
                                          uri=uri,
                                          user=username,
                                          passwd=password)
                if proxy:
                    opener = urllib.request.build_opener(auth_handler, urllib.request.ProxyHandler(proxy))
                else:
                    opener = urllib.request.build_opener(auth_handler)
            else:
                if proxy:
                    opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy))
                else:
                    opener = urllib.request.build_opener()
            urllib.request.install_opener(opener)

            if 'User-agent' not in headers:
                headers['User-agent'] = 'alert-urlmon/%s Python-urllib/%s' % (__version__, urllib.__version__)

            try:
                if post:
                    req = urllib.request.Request(url, json.dumps(post), headers=headers)
                else:
                    req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, None, MAX_TIMEOUT)
            except ValueError as e:
                LOG.error('Request failed: %s', e)
            except urllib.error.URLError as e:
                if hasattr(e, 'reason'):
                    reason = str(e.reason)
                    status = None
                elif hasattr(e, 'code'):
                    reason = None
                    status = e.code
            except Exception as e:
                LOG.warning('Unexpected error: %s', e)
            else:
                status = response.getcode()
                body = response.read()

            rtt = int((time.time() - start) * 1000)  # round-trip time

            if status:  # return result if any HTTP/S response is received
                break

            if not count:
                break
            time.sleep(10)

        return status, reason, body, rtt


class UrlmonDaemon(object):

    def __init__(self):

        self.shuttingdown = False

    def run(self):

        self.running = True

        self.queue = queue.Queue()
        self.api = Client(endpoint=settings.ENDPOINT, key=settings.API_KEY)

        # Start worker threads
        LOG.debug('Starting %s worker threads...', SERVER_THREADS)
        for i in range(SERVER_THREADS):
            w = WorkerThread(self.queue, self.api)
            try:
                w.start()
            except Exception as e:
                LOG.error('Worker thread #%s did not start: %s', i, e)
                continue
            LOG.info('Started worker thread: %s', w.getName())

        while not self.shuttingdown:
            try:
                for check in settings.checks:
                    self.queue.put((check, time.time()))

                LOG.debug('Send heartbeat...')
                try:
                    origin = '{}/{}'.format('urlmon', platform.uname()[1])
                    self.api.heartbeat(origin, tags=[__version__])
                except Exception as e:
                    LOG.warning('Failed to send heartbeat: %s', e)

                time.sleep(LOOP_EVERY)
                LOG.info('URL check queue length is %d', self.queue.qsize())

            except (KeyboardInterrupt, SystemExit):
                self.shuttingdown = True

        LOG.info('Shutdown request received...')
        self.running = False

        for i in range(SERVER_THREADS):
            self.queue.put(None)
        w.join()


def main():

    LOG = logging.getLogger("alerta.urlmon")

    try:
        UrlmonDaemon().run()
    except Exception as e:
        LOG.error(e, exc_info=1)
        sys.exit(1)
    except KeyboardInterrupt as e:
        LOG.warning("Exiting alerta urlmon.")
        sys.exit(1)

if __name__ == '__main__':
    main()
