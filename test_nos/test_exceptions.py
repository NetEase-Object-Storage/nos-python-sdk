# -*- coding:utf8 -*-

from nos.exceptions import (ClientException, ServiceException,
                            InvalidObjectName, InvalidBucketName,
                            FileOpenModeError, MultiObjectDeleteException)

from .test_cases import TestCase


class TestClientException(TestCase):
    def test_default(self):
        message = "ClientException(hello) caused by: KeyError('key error')"
        err = KeyError("key error")
        exception = ClientException('hello', err)
        self.assertEquals('hello', exception.error)
        self.assertEquals(err, exception.info)
        self.assertEquals(message, exception.message)
        self.assertEquals(message, str(exception))


class TestServiceException(TestCase):
    def test_default(self):
        status_code = 400
        error_type = 'Bad Request'
        error_code = 'InvalidArgument'
        request_id = '9b8932d70aa000000154d729c6b0840e'
        message = 'uploadId=23r54i252358235-3253222'
        exception = ServiceException(status_code, error_type, error_code,
                                     request_id, message)
        self.assertEquals(status_code, exception.status_code)
        self.assertEquals(error_type, exception.error_type)
        self.assertEquals(error_code, exception.error_code)
        self.assertEquals(request_id, exception.request_id)
        self.assertEquals(message, exception.message)
        self.assertEquals(
            'ServiceException(400, Bad Request, InvalidArgument,'
            ' 9b8932d70aa000000154d729c6b0840e, '
            'uploadId=23r54i252358235-3253222)',
            str(exception))


class TestInvalidObjectName(TestCase):
    def test_default(self):
        message = 'InvalidObjectName caused by: object name is empty.'
        exception = InvalidObjectName()
        self.assertEquals(None, exception.error)
        self.assertEquals(None, exception.info)
        self.assertEquals(message, exception.message)
        self.assertEquals(message, str(exception))


class TestInvalidBucketName(TestCase):
    def test_default(self):
        message = 'InvalidBucketName caused by: bucket name is empty.'
        exception = InvalidBucketName()
        self.assertEquals(None, exception.error)
        self.assertEquals(None, exception.info)
        self.assertEquals(message, exception.message)
        self.assertEquals(message, str(exception))


class TestFileOpenModeError(TestCase):
    def test_default(self):
        message = ('FileOpenModeError caused by: object is a file that opened '
                   'without the mode for binary files.')
        exception = FileOpenModeError()
        self.assertEquals(None, exception.error)
        self.assertEquals(None, exception.info)
        self.assertEquals(message, exception.message)
        self.assertEquals(message, str(exception))


class TestMultiObjectDeleteException(TestCase):
    def test_default(self):
        info = [{
            'key': '2.jpg',
            'code': 'NoSuchKey',
            'message': 'No Such Key'
        }]
        message = ('MultiObjectDeleteException caused by: some objects delete '
                   'unsuccessfully.')
        exception = MultiObjectDeleteException(info)
        self.assertEquals(None, exception.status_code)
        self.assertEquals(None, exception.error_type)
        self.assertEquals(None, exception.error_code)
        self.assertEquals(None, exception.request_id)
        self.assertEquals(message, exception.message)
        self.assertEquals(info, exception.errors)
        self.assertEquals(
            "%s %s" % (message, info),
            str(exception)
        )
