
import json
import unittest

from alerta.app import create_app, custom_webhooks

import alerta_sentry


class SentryWebhookTestCase(unittest.TestCase):

    def setUp(self):

        test_config = {
            'TESTING': True,
            'AUTH_REQUIRED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

    def test_sentry_webhook(self):

        custom_webhooks.webhooks['sentry'] = alerta_sentry.SentryWebhook()

        payload = r"""
            {
              "project": "alerta5",
              "project_name": "alerta5",
              "culprit": "raven.scripts.runner in main",
              "project_slug": "alerta5",
              "url": "https://sentry.io/alertaio/alerta5/issues/541485531/",
              "logger": null,
              "level": "error",
              "message": "This is an example Python exception",
              "id": "541485531",
              "event": {
                "received": 1525248430,
                "sentry.interfaces.User": {
                  "username": "sentry",
                  "id": "1",
                  "ip_address": "127.0.0.1",
                  "name": "Sentry",
                  "email": "sentry@example.com"
                },
                "sentry.interfaces.Message": {
                  "message": "This is an example Python exception"
                },
                "errors": [],
                "extra": {
                  "emptyList": [],
                  "unauthorized": false,
                  "emptyMap": {},
                  "url": "http://example.org/foo/bar/",
                  "results": [
                    1,
                    2,
                    3,
                    4,
                    5
                  ],
                  "length": 10837790,
                  "session": {
                    "foo": "bar"
                  }
                },
                "event_id": "0476467adf8f499ea795a48fcc4bf290",
                "fingerprint": [
                  "{{ default }}"
                ],
                "modules": {
                  "my.package": "1.0.0"
                },
                "id": 19293981000,
                "sentry.interfaces.Http": {
                  "cookies": [
                    [
                      "foo",
                      "bar"
                    ],
                    [
                      "biz",
                      "baz"
                    ]
                  ],
                  "url": "http://example.com/foo",
                  "headers": [
                    [
                      "Content-Type",
                      "application/json"
                    ],
                    [
                      "Referer",
                      "http://example.com"
                    ],
                    [
                      "User-Agent",
                      "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"
                    ]
                  ],
                  "env": {
                    "ENV": "prod"
                  },
                  "query_string": "foo=bar",
                  "data": {
                    "hello": "world"
                  },
                  "method": "GET",
                  "inferred_content_type": "application/json"
                },
                "sentry.interfaces.Template": {
                  "abs_path": "/srv/example/templates/debug_toolbar/base.html",
                  "pre_context": [
                    "{% endif %}\n",
                    "<script src=\"{% static 'debug_toolbar/js/toolbar.js' %}\"></script>\n",
                    "<div id=\"djDebug\" hidden=\"hidden\" dir=\"ltr\"\n"
                  ],
                  "post_context": [
                    "     {{ toolbar.config.ROOT_TAG_EXTRA_ATTRS|safe }}>\n",
                    "\t<div hidden=\"hidden\" id=\"djDebugToolbar\">\n",
                    "\t\t<ul id=\"djDebugPanelList\">\n"
                  ],
                  "filename": "debug_toolbar/base.html",
                  "lineno": 14,
                  "context_line": "     data-store-id=\"{{ toolbar.store_id }}\" data-render-panel-url=\"{% url 'djdt:render_panel' %}\"\n"
                },
                "version": "5",
                "_ref_version": 2,
                "_ref": 153768,
                "type": "default",
                "sentry.interfaces.Stacktrace": {
                  "frames": [
                    {
                      "function": "build_msg",
                      "abs_path": "/home/ubuntu/.virtualenvs/getsentry/src/raven/raven/base.py",
                      "pre_context": [
                        "                frames = stack",
                        "",
                        "            data.update({",
                        "                'sentry.interfaces.Stacktrace': {",
                        "                    'frames': get_stack_info(frames,"
                      ],
                      "vars": {
                        "'frames'": "<generator object iter_stack_frames at 0x107bcc3c0>",
                        "'culprit'": null,
                        "'event_type'": "'raven.events.Message'",
                        "'handler'": "<raven.events.Message object at 0x107bd0890>",
                        "'date'": "datetime.datetime(2013, 8, 13, 3, 8, 24, 880386)",
                        "'extra'": {
                          "'go_deeper'": [
                            [
                              {
                                "'bar'": [
                                  "'baz'"
                                ],
                                "'foo'": "'bar'"
                              }
                            ]
                          ],
                          "'user'": "'dcramer'",
                          "'loadavg'": [
                            0.37255859375,
                            0.5341796875,
                            0.62939453125
                          ]
                        },
                        "'v'": {
                          "'message'": "u'This is a test message generated using ``raven test``'",
                          "'params'": []
                        },
                        "'stack'": true,
                        "'event_id'": "'54a322436e1b47b88e239b78998ae742'",
                        "'tags'": null,
                        "'time_spent'": null,
                        "'self'": "<raven.base.Client object at 0x107bb8210>",
                        "'data'": {
                          "'sentry.interfaces.Message'": {
                            "'message'": "u'This is a test message generated using ``raven test``'",
                            "'params'": []
                          },
                          "'message'": "u'This is a test message generated using ``raven test``'"
                        },
                        "'result'": {
                          "'sentry.interfaces.Message'": {
                            "'message'": "u'This is a test message generated using ``raven test``'",
                            "'params'": []
                          },
                          "'message'": "u'This is a test message generated using ``raven test``'"
                        },
                        "'kwargs'": {
                          "'message'": "'This is a test message generated using ``raven test``'",
                          "'level'": 20
                        },
                        "'k'": "'sentry.interfaces.Message'",
                        "'public_key'": null
                      },
                      "post_context": [
                        "                },",
                        "            })",
                        "",
                        "        if 'sentry.interfaces.Stacktrace' in data:",
                        "            if self.include_paths:"
                      ],
                      "filename": "raven/base.py",
                      "module": "raven.base",
                      "in_app": false,
                      "context_line": "                        transformer=self.transform)",
                      "lineno": 303
                    },
                    {
                      "function": "capture",
                      "abs_path": "/home/ubuntu/.virtualenvs/getsentry/src/raven/raven/base.py",
                      "pre_context": [
                        "        if not self.is_enabled():",
                        "            return",
                        "",
                        "        data = self.build_msg(",
                        "            event_type, data, date, time_spent, extra, stack, tags=tags,"
                      ],
                      "vars": {
                        "'event_type'": "'raven.events.Message'",
                        "'date'": null,
                        "'extra'": {
                          "'go_deeper'": [
                            [
                              {
                                "'bar'": [
                                  "'baz'"
                                ],
                                "'foo'": "'bar'"
                              }
                            ]
                          ],
                          "'user'": "'dcramer'",
                          "'loadavg'": [
                            0.37255859375,
                            0.5341796875,
                            0.62939453125
                          ]
                        },
                        "'stack'": true,
                        "'tags'": null,
                        "'time_spent'": null,
                        "'self'": "<raven.base.Client object at 0x107bb8210>",
                        "'data'": null,
                        "'kwargs'": {
                          "'message'": "'This is a test message generated using ``raven test``'",
                          "'level'": 20
                        }
                      },
                      "post_context": [
                        "",
                        "        self.send(**data)",
                        "",
                        "        return (data.get('event_id'),)",
                        ""
                      ],
                      "filename": "raven/base.py",
                      "module": "raven.base",
                      "in_app": false,
                      "context_line": "            **kwargs)",
                      "lineno": 459
                    },
                    {
                      "function": "captureMessage",
                      "abs_path": "/home/ubuntu/.virtualenvs/getsentry/src/raven/raven/base.py",
                      "pre_context": [
                        "        \"\"\"",
                        "        Creates an event from ``message``.",
                        "",
                        "        >>> client.captureMessage('My event just happened!')",
                        "        \"\"\""
                      ],
                      "vars": {
                        "'message'": "'This is a test message generated using ``raven test``'",
                        "'kwargs'": {
                          "'extra'": {
                            "'go_deeper'": [
                              [
                                {
                                  "'bar'": [
                                    "'baz'"
                                  ],
                                  "'foo'": "'bar'"
                                }
                              ]
                            ],
                            "'user'": "'dcramer'",
                            "'loadavg'": [
                              0.37255859375,
                              0.5341796875,
                              0.62939453125
                            ]
                          },
                          "'tags'": null,
                          "'data'": null,
                          "'level'": 20,
                          "'stack'": true
                        },
                        "'self'": "<raven.base.Client object at 0x107bb8210>"
                      },
                      "post_context": [
                        "",
                        "    def captureException(self, exc_info=None, **kwargs):",
                        "        \"\"\"",
                        "        Creates an event from an exception.",
                        ""
                      ],
                      "filename": "raven/base.py",
                      "module": "raven.base",
                      "in_app": false,
                      "context_line": "        return self.capture('raven.events.Message', message=message, **kwargs)",
                      "lineno": 577
                    },
                    {
                      "function": "send_test_message",
                      "abs_path": "/home/ubuntu/.virtualenvs/getsentry/src/raven/raven/scripts/runner.py",
                      "pre_context": [
                        "        level=logging.INFO,",
                        "        stack=True,",
                        "        tags=options.get('tags', {}),",
                        "        extra={",
                        "            'user': get_uid(),"
                      ],
                      "vars": {
                        "'client'": "<raven.base.Client object at 0x107bb8210>",
                        "'options'": {
                          "'tags'": null,
                          "'data'": null
                        },
                        "'data'": null,
                        "'k'": "'secret_key'"
                      },
                      "post_context": [
                        "        },",
                        "    ))",
                        "",
                        "    if client.state.did_fail():",
                        "        print('error!')"
                      ],
                      "filename": "raven/scripts/runner.py",
                      "module": "raven.scripts.runner",
                      "in_app": false,
                      "context_line": "            'loadavg': get_loadavg(),",
                      "lineno": 77
                    },
                    {
                      "function": "main",
                      "abs_path": "/home/ubuntu/.virtualenvs/getsentry/src/raven/raven/scripts/runner.py",
                      "pre_context": [
                        "    print(\"Using DSN configuration:\")",
                        "    print(\" \", dsn)",
                        "    print()",
                        "",
                        "    client = Client(dsn, include_paths=['raven'])"
                      ],
                      "vars": {
                        "'root'": "<logging.Logger object at 0x107ba5b10>",
                        "'parser'": "<optparse.OptionParser instance at 0x107ba3368>",
                        "'dsn'": "'https://ebc35f33e151401f9deac549978bda11:f3403f81e12e4c24942d505f086b2cad@sentry.io/1'",
                        "'opts'": "<Values at 0x107ba3b00: {'data': None, 'tags': None}>",
                        "'client'": "<raven.base.Client object at 0x107bb8210>",
                        "'args'": [
                          "'test'",
                          "'https://ebc35f33e151401f9deac549978bda11:f3403f81e12e4c24942d505f086b2cad@sentry.io/1'"
                        ]
                      },
                      "module": "raven.scripts.runner",
                      "filename": "raven/scripts/runner.py",
                      "lineno": 112,
                      "in_app": false,
                      "context_line": "    send_test_message(client, opts.__dict__)"
                    }
                  ]
                },
                "tags": [
                  [
                    "browser",
                    "Chrome 28.0"
                  ],
                  [
                    "device",
                    "Other"
                  ],
                  [
                    "level",
                    "error"
                  ],
                  [
                    "os",
                    "Windows 8"
                  ],
                  [
                    "sentry:user",
                    "id:1"
                  ],
                  [
                    "url",
                    "http://example.com/foo"
                  ]
                ],
                "metadata": {
                  "title": "This is an example Python exception"
                }
              }
            }
        """

        response = self.client.post('/webhooks/sentry', data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['alert']['resource'], 'raven.scripts.runner in main')
        self.assertEqual(data['alert']['event'], '0476467adf8f499ea795a48fcc4bf290')
        self.assertEqual(data['alert']['value'], 'error')
        self.assertEqual(data['alert']['text'], 'This is an example Python exception https://sentry.io/alertaio/alerta5/issues/541485531/')
        self.assertEqual(sorted(data['alert']['tags']), ['browser=Chrome 28.0', 'device=Other', 'level=error', 'os=Windows 8', 'sentry:user=id:1', 'url=http://example.com/foo'])
        self.assertEqual(data['alert']['attributes']['modules'], ['my.package==1.0.0'])
