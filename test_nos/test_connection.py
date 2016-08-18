# -*- coding:utf8 -*-

from mock import Mock, patch
import urllib3
from urllib3.exceptions import ReadTimeoutError
from nos.exceptions import ConnectionTimeout, ConnectionError, BadRequestError
from nos.connection import Urllib3HttpConnection

from .test_cases import TestCase


class TestUrllib3Connection(TestCase):
    def _get_mock_connection(self, connection_params={},
                             status_code=200, response_body='{}'):
        con = Urllib3HttpConnection(**connection_params)

        def _dummy_send(*args, **kwargs):
            dummy_response = Mock()
            dummy_response.headers = {}
            dummy_response.getheaders = Mock(return_value={})
            dummy_response.status = status_code
            dummy_response.read = Mock(return_value=response_body)
            dummy_response.request = args[0]
            dummy_response.cookies = {}
            _dummy_send.call_args = (args, kwargs)
            return dummy_response
        con.pool.urlopen = _dummy_send
        return con

    @patch('urllib3.PoolManager')
    def test_default_num_pools(self, mock_pool_manager):
        Urllib3HttpConnection()
        mock_pool_manager.assert_called_once_with(num_pools=16)

    @patch('urllib3.PoolManager')
    def test_num_pools(self, mock_pool_manager):
        Urllib3HttpConnection(num_pools=1)
        mock_pool_manager.assert_called_once_with(num_pools=1)

    def test_pool(self):
        con = Urllib3HttpConnection()
        self.assertIsInstance(con.pool, urllib3.poolmanager.PoolManager)

    def test_read_timeout_error(self):
        con = Urllib3HttpConnection()
        con.pool.urlopen = Mock(side_effect=ReadTimeoutError('', '', ''))
        self.assertRaises(ConnectionTimeout, con.perform_request,
                          u'GET', u'/', timeout=10)

    def test_other_error(self):
        con = Urllib3HttpConnection()
        con.pool.urlopen = Mock(side_effect=KeyError())
        self.assertRaises(ConnectionError, con.perform_request,
                          u'GET', u'/', timeout=10)

    def test_perform_request_default(self):
        con = self._get_mock_connection(status_code=200, response_body='ok!')
        status, headers, response = con.perform_request('GET', '/')
        self.assertEquals(200, status)
        self.assertEquals({}, headers)
        self.assertEquals('ok!', response.read())

    @patch('nos.connection.Urllib3HttpConnection._raise_error')
    def test_request_error(self, mock_raise_error):
        con = self._get_mock_connection(status_code=400)
        con.perform_request('GET', '/')
        mock_raise_error.assert_called_once()

    def test_raise_error_with_no_data(self):
        response = Mock()
        response.status = 400
        response.reason = 'Bad Request'
        response.getheader = Mock(return_value='')
        response.read = Mock(return_value='')

        con = Urllib3HttpConnection()
        self.assertRaises(BadRequestError, con._raise_error, response)

    def test_raise_error(self):
        response = Mock()
        response.status = 400
        response.reason = 'Bad Request'
        response.getheader = Mock(return_value='')
        response.read = Mock(return_value='''
<Error>
    <Code>InvalidArgument</Code>
    <Message>值“uploadId=23r54i252358235-3253222”非法，必须为整数</Message>
    <Resource></Resource>
    <RequestId>c081a3ec0aa000000154d125d733840f</RequestId>
</Error>
''')
        con = Urllib3HttpConnection()
        self.assertRaises(BadRequestError, con._raise_error, response)
