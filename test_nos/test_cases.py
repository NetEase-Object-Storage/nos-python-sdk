# -*- coding:utf8 -*-

from mock import Mock
from collections import defaultdict
try:
    # python 2.6
    from unittest2 import TestCase, SkipTest
except ImportError:
    from unittest import TestCase, SkipTest

from nos import Client


class DummyTransport(object):
    def __init__(self, responses=None, **kwargs):
        self.responses = responses
        self.call_count = 0
        self.calls = defaultdict(list)

    def perform_request(self, method, bucket='', key='', params={}, body=None,
                        headers={}, timeout=None):
        resp = Mock()
        resp.read = Mock(return_value='<a></a>')
        h = {
            'Last-Modified': 'Fri, 10 Feb 2012 21:34:55 GMT',
            'Content-Length':1,
            'Content-Range': '0-50'
        }
        resp = 200, h, resp
        if self.responses:
            resp = self.responses[self.call_count]
        self.call_count += 1
        self.calls[(method, bucket, key)].append((params, body, headers, timeout))
        return resp


class ClinetTestCase(TestCase):
    def setUp(self):
        super(ClinetTestCase, self).setUp()
        self.client = Client(transport_class=DummyTransport)

    def assert_call_count_equals(self, count):
        self.assertEquals(count, self.client.transport.call_count)

    def assert_url_called(self, method, bucket, key, count=1):
        self.assertIn((method, bucket, key), self.client.transport.calls)
        calls = self.client.transport.calls[(method, bucket, key)]
        self.assertEquals(count, len(calls))
        return calls


class TestClinetTestCase(ClinetTestCase):
    def test_our_transport_used(self):
        self.assertIsInstance(self.client.transport, DummyTransport)

    def test_start_with_0_call(self):
        self.assert_call_count_equals(0)

    def test_each_call_is_recorded(self):
        self.client.transport.perform_request('GET')
        self.client.transport.perform_request(
            'DELETE', 'test', 'object', params={},
            body='body', headers={}, timeout=None
        )
        self.assert_call_count_equals(2)
        self.assertEquals([({}, 'body', {}, None)], self.assert_url_called(
            'DELETE', 'test', 'object', 1
        ))
