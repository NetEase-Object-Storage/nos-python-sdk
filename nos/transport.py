# -*- coding:utf8 -*-

from .connection import Urllib3HttpConnection
from .serializer import JSONSerializer
from .exceptions import (NOSException, ServiceException, ConnectionError,
                         ConnectionTimeout, InvalidObjectName,
                         InvalidBucketName, FileOpenModeError,
                         BadRequestError)
from .client.auth import RequestMetaData
from .client.utils import MAX_OBJECT_SIZE

__all__ = ["Transport"]


class Transport(object):
    """
    Encapsulation of transport-related to logic. Handles instantiation of the
    individual connections as well as creating a connection pool to hold them.

    Main interface is the `perform_request` method.
    """
    def __init__(self, access_key_id=None, access_key_secret=None,
                 connection_class=Urllib3HttpConnection,
                 serializer=JSONSerializer(), end_point='nos-eastchina1.126.net',
                 max_retries=2, retry_on_status=(500, 501, 503, ),
                 retry_on_timeout=False, timeout=None, **kwargs):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.max_retries = max_retries
        self.retry_on_timeout = retry_on_timeout
        self.retry_on_status = retry_on_status
        self.timeout = timeout
        self.end_point = end_point

        # data serializer
        self.serializer = serializer
        # store all strategies...
        self.connection = connection_class(**kwargs)

    def perform_request(self, method, bucket=None, key=None, params={},
                        body=None, headers={}, timeout=None):
        method = method.encode('utf-8') \
                if isinstance(method, unicode) else method
        bucket = bucket.encode('utf-8') \
                if isinstance(bucket, unicode) else bucket
        key = key.encode('utf-8') if isinstance(key, unicode) else key

        if bucket is not None and bucket == '':
            raise InvalidBucketName()

        if key is not None and key == '':
            raise InvalidObjectName()

        if body is not None:
            body = self.serializer.dumps(body)
            length = 0
            if isinstance(body, file):
                if 'b' not in body.mode.lower():
                    raise FileOpenModeError()
                offset = body.tell()
                body.seek(0, 2)
                end = body.tell()
                body.seek(offset, 0)
                length = end - offset
            else:
                length = len(body)

            if length > MAX_OBJECT_SIZE:
                raise BadRequestError(
                    400,
                    'Bad Request',
                    'EntityTooLarge',
                    '',
                    'Request Entity Too Large'
                )

        meta_data = RequestMetaData(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            method=method,
            bucket=bucket,
            end_point=self.end_point,
            key=key,
            params=params,
            body=body,
            headers=headers
        )
        url = meta_data.get_url()
        headers = meta_data.get_headers()

        for attempt in xrange(self.max_retries + 1):
            try:
                status, headers, body = self.connection.perform_request(
                    method, url, body, headers,
                    timeout=(timeout or self.timeout)
                )

            except NOSException as e:
                retry = False
                if isinstance(e, ConnectionTimeout):
                    retry = self.retry_on_timeout
                elif isinstance(e, ConnectionError):
                    retry = True
                elif (isinstance(e, ServiceException) and
                      e.status_code in self.retry_on_status):
                    retry = True

                if retry:
                    # raise exception on last retry
                    if attempt >= self.max_retries:
                        raise
                else:
                    raise

            else:
                return status, headers, body
