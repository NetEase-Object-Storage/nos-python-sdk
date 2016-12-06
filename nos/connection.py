# -*- coding:utf8 -*-

import certifi
import urllib3
from urllib3.exceptions import ReadTimeoutError
from .exceptions import (ConnectionError, ConnectionTimeout,
                         ServiceException, HTTP_EXCEPTIONS)
from .compat import ET

__all__ = ["Urllib3HttpConnection"]


class Urllib3HttpConnection(object):
    def __init__(self, num_pools=16, enable_ssl=False, **kwargs):
        if enable_ssl:
            self.pool = urllib3.PoolManager(num_pools=num_pools,
                                            cert_reqs='CERT_REQUIRED',
                                            ca_certs=certifi.where())
        else:
            self.pool = urllib3.PoolManager(num_pools=num_pools)

    def perform_request(self, method, url, body=None, headers={}, timeout=None,
                        preload_content=False):
        try:
            kw = {'preload_content': preload_content}
            if timeout:
                kw['timeout'] = timeout

            # in python2 we need to make sure the url and method are not
            # unicode. Otherwise the body will be decoded into unicode too and
            # that will fail.
            if not isinstance(url, str):
                url = url.encode('utf-8')
            if not isinstance(method, str):
                method = method.encode('utf-8')

            response = self.pool.urlopen(method, url, body=body, retries=False,
                                         headers=headers, **kw)
        except ReadTimeoutError as e:
            raise ConnectionTimeout(str(e), e)
        except Exception as e:
            raise ConnectionError(str(e), e)

        if not (200 <= response.status < 300):
            self._raise_error(response)
        return response.status, response.getheaders(), response

    def _raise_error(self, response):
        """ Locate appropriate exception and raise it. """
        status_code = response.status
        error_type = response.reason
        request_id = response.getheader('x-nos-request-id', '')
        raw_data = response.read()
        error_code = ''
        message = ''
        try:
            resp_info = ET.fromstring(raw_data)
            error_code = resp_info.findtext('Code', '')
            message = resp_info.findtext('Message', '')
        except:
            # we don't care what went wrong
            pass

        raise HTTP_EXCEPTIONS.get(status_code, ServiceException)(
            status_code, error_type, error_code, request_id, message
        )
