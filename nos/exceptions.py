# -*- coding:utf8 -*-

__all__ = [
    "NOSException",
    "ClientException",
    "ServiceException",
    "InvalidBucketName",
    "InvalidObjectName",
    "XmlParseError",
    "SerializationError",
    "ConnectionError",
    "ConnectionTimeout",
    "MultiObjectDeleteException",
    "BadRequestError",
    "ForbiddenError",
    "NotFoundError",
    "MethodNotAllowedError",
    "ConflictError",
    "LengthRequiredError",
    "RequestedRangeNotSatisfiableError",
    "InternalServerErrorError",
    "NotImplementedError",
    "ServiceUnavailableError"
]


class NOSException(Exception):
    """
    Base class for all exceptions raised by this package's operations.
    """


class ClientException(NOSException):
    """
    Exception raised when there was an exception while sdk client working.
    """
    @property
    def error(self):
        return self.args[0]

    @property
    def info(self):
        return self.args[1]

    @property
    def message(self):
        return '%s(%s) caused by: %s(%s)' % (
            self.__class__.__name__,
            self.error,
            self.info.__class__.__name__,
            self.info
        )

    def __str__(self):
        return self.message


class ServiceException(NOSException):
    """
    Exception raised when NOS returns a non-OK (>=400) HTTP status code.
    """
    @property
    def status_code(self):
        return self.args[0]

    @property
    def error_type(self):
        return self.args[1]

    @property
    def error_code(self):
        return self.args[2]

    @property
    def request_id(self):
        return self.args[3]

    @property
    def message(self):
        return self.args[4]

    def __str__(self):
        return '%s(%s, %s, %s, %s, %s)' % (
            self.__class__.__name__,
            self.status_code,
            self.error_type,
            self.error_code,
            self.request_id,
            self.message
        )


class InvalidBucketName(ClientException):
    """
    Exception raised when bucket name is invalid.
    """
    @property
    def error(self):
        pass

    @property
    def info(self):
        pass

    @property
    def message(self):
        return 'InvalidBucketName caused by: bucket name is empty.'

    def __str__(self):
        return self.message


class InvalidObjectName(ClientException):
    """
    Exception raised when object name is invalid.
    """
    @property
    def error(self):
        pass

    @property
    def info(self):
        pass

    @property
    def message(self):
        return 'InvalidObjectName caused by: object name is empty.'

    def __str__(self):
        return self.message


class FileOpenModeError(ClientException):
    """
    Exception raised when upload object is a file that opened without the mode
    for binary files.
    """
    @property
    def error(self):
        pass

    @property
    def info(self):
        pass

    @property
    def message(self):
        return ('FileOpenModeError caused by: object is a file that opened '
                'without the mode for binary files.')

    def __str__(self):
        return self.message


class XmlParseError(ClientException):
    """
    Error raised when there was an exception while parse xml.
    """


class SerializationError(ClientException):
    """
    Data passed in failed to serialize properly in the Serializer being
    used.
    """


class ConnectionError(ClientException):
    """
    Error raised when there was an exception while talking to NOS server.
    """


class ConnectionTimeout(ConnectionError):
    """ A network timeout. """


class MultiObjectDeleteException(ServiceException):
    """
    Exception raised when there was an exception while delete objects.
    """
    @property
    def status_code(self):
        pass

    @property
    def error_type(self):
        pass

    @property
    def error_code(self):
        pass

    @property
    def request_id(self):
        pass

    @property
    def message(self):
        return ('MultiObjectDeleteException caused by: some objects delete '
                'unsuccessfully.')

    @property
    def errors(self):
        return self.args[0]

    def __str__(self):
        return '%s %s' % (
            self.message,
            self.errors
        )


class BadRequestError(ServiceException):
    """ Exception representing a 400 status code. """


class ForbiddenError(ServiceException):
    """ Exception representing a 403 status code. """


class NotFoundError(ServiceException):
    """ Exception representing a 404 status code. """


class MethodNotAllowedError(ServiceException):
    """ Exception representing a 405 status code. """


class ConflictError(ServiceException):
    """ Exception representing a 409 status code. """


class LengthRequiredError(ServiceException):
    """ Exception representing a 411 status code. """


class RequestedRangeNotSatisfiableError(ServiceException):
    """ Exception representing a 416 status code. """


class InternalServerErrorError(ServiceException):
    """ Exception representing a 500 status code. """


class NotImplementedError(ServiceException):
    """ Exception representing a 501 status code. """


class ServiceUnavailableError(ServiceException):
    """ Exception representing a 503 status code. """


# more generic mappings from status_code to python exceptions
HTTP_EXCEPTIONS = {
    400: BadRequestError,
    403: ForbiddenError,
    404: NotFoundError,
    405: MethodNotAllowedError,
    409: ConflictError,
    411: LengthRequiredError,
    416: RequestedRangeNotSatisfiableError,
    500: InternalServerErrorError,
    501: NotImplementedError,
    503: ServiceUnavailableError,
}
