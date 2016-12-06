# -*- coding:utf8 -*-

from mock import Mock, patch
from nos.exceptions import (ConnectionTimeout, ConnectionError,
                            ServiceException, FileOpenModeError,
                            BadRequestError)
from nos.transport import Transport
from nos.serializer import JSONSerializer
from nos.connection import Urllib3HttpConnection
from nos.client.utils import MAX_OBJECT_SIZE

from .test_cases import TestCase


class TestTransport(TestCase):
    def test_init_default_args(self):
        transport = Transport()
        self.assertEquals(None, transport.access_key_id)
        self.assertEquals(None, transport.access_key_secret)
        self.assertEquals(2, transport.max_retries)
        self.assertEquals(False, transport.retry_on_timeout)
        self.assertEquals('nos-eastchina1.126.net', transport.end_point)
        self.assertEquals((500, 501, 503, ), transport.retry_on_status)
        self.assertEquals(None, transport.timeout)
        self.assertIsInstance(transport.serializer, JSONSerializer)
        self.assertIsInstance(transport.connection, Urllib3HttpConnection)

    def test_init_args(self):
        access_key_id = '12345'
        access_key_secret = '54321'
        retry_on_timeout = True
        retry_on_status = (500, 502, )
        serializer = JSONSerializer()
        kwargs = {
            'max_retries': 10,
            'end_point': 'nos110.netease.com',
            'timeout': 1
        }
        transport = Transport(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            retry_on_timeout=retry_on_timeout,
            retry_on_status=retry_on_status,
            serializer=serializer,
            **kwargs
        )
        self.assertEquals(access_key_id, transport.access_key_id)
        self.assertEquals(access_key_secret, transport.access_key_secret)
        self.assertEquals(retry_on_timeout, transport.retry_on_timeout)
        self.assertEquals(retry_on_status, transport.retry_on_status)
        self.assertEquals(kwargs['max_retries'], transport.max_retries)
        self.assertEquals(kwargs['end_point'], transport.end_point)
        self.assertEquals(kwargs['timeout'], transport.timeout)
        self.assertEquals(serializer, transport.serializer)
        self.assertIsInstance(transport.connection, Urllib3HttpConnection)

    @patch('nos.transport.RequestMetaData')
    def test_perform_request_default_args(self, mock_meta_data):
        url = 'http://nos.neteast.com'
        headers = {'a': 'b'}
        d = Mock()
        d.get_url.return_value = url
        d.get_headers.return_value = headers
        mock_meta_data.return_value = d

        transport = Transport()
        transport.connection.perform_request = Mock(return_value=(200, {}, ''))
        self.assertEquals((200, {}, ''), transport.perform_request('GET'))
        mock_meta_data.assert_called_once_with(
            access_key_id=transport.access_key_id,
            access_key_secret=transport.access_key_secret,
            method='GET',
            bucket=None,
            key=None,
            end_point='nos-eastchina1.126.net',
            params={},
            body=None,
            headers={},
            enable_ssl=False
        )
        transport.connection.perform_request.assert_called_once_with(
            'GET', url, None, headers, timeout=None
        )

    @patch('nos.transport.RequestMetaData')
    def test_perform_request_with_timeout(self, mock_meta_data):
        url = 'http://nos.neteast.com'
        headers = {'a': 'b'}
        d = Mock()
        d.get_url.return_value = url
        d.get_headers.return_value = headers
        mock_meta_data.return_value = d

        transport = Transport()
        transport.serializer.dumps = Mock(return_value='54321')
        transport.connection.perform_request = Mock(
            side_effect=ConnectionTimeout
        )
        self.assertRaises(ConnectionTimeout, transport.perform_request,
                          'GET', body='12345')
        transport.serializer.dumps.assert_called_once_with('12345')
        transport.connection.perform_request.assert_called_once_with(
            'GET', url, '54321', headers, timeout=None
        )

    @patch('nos.transport.RequestMetaData')
    def test_perform_request_with_connectionerror(self, mock_meta_data):
        url = 'http://nos.neteast.com'
        headers = {'a': 'b'}
        d = Mock()
        d.get_url.return_value = url
        d.get_headers.return_value = headers
        mock_meta_data.return_value = d

        transport = Transport()
        transport.serializer.dumps = Mock(return_value='54321')
        transport.connection.perform_request = Mock(
            side_effect=ConnectionError('', '')
        )
        self.assertRaises(ConnectionError, transport.perform_request,
                          'GET', body='12345')
        transport.serializer.dumps.assert_called_once_with('12345')
        transport.connection.perform_request.assert_called_with(
            'GET', url, '54321', headers, timeout=None
        )

    @patch('nos.transport.RequestMetaData')
    def test_perform_request_with_serviceexception(self, mock_meta_data):
        url = 'http://nos.neteast.com'
        headers = {'a': 'b'}
        d = Mock()
        d.get_url.return_value = url
        d.get_headers.return_value = headers
        mock_meta_data.return_value = d

        transport = Transport()
        transport.serializer.dumps = Mock(return_value='54321')
        transport.connection.perform_request = Mock(
            side_effect=ServiceException(503)
        )
        self.assertRaises(ServiceException, transport.perform_request,
                          'GET', body='12345')
        transport.serializer.dumps.assert_called_once_with('12345')
        transport.connection.perform_request.assert_called_with(
            'GET', url, '54321', headers, timeout=None
        )

    def test_perform_request_with_fileopenmodeerror(self):
        transport = Transport()
        f = open('setup.py', 'r')
        transport.serializer.dumps = Mock(return_value=f)
        self.assertRaises(
            FileOpenModeError, transport.perform_request, 'GET', body=f
        )

    def test_perform_request_with_badrequesterror(self):
        d = '12' * MAX_OBJECT_SIZE
        transport = Transport()
        transport.serializer.dumps = Mock(return_value=d)
        self.assertRaises(
            BadRequestError, transport.perform_request, 'GET', body=d
        )
