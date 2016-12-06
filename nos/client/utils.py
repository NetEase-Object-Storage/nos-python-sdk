# -*- coding:utf8 -*-

import platform


def enum(**enums):
    return type('Enum', (), enums)

HTTP_METHOD = enum(
    HEAD='HEAD',
    GET='GET',
    POST='POST',
    PUT='PUT',
    DELETE='DELETE'
)

HTTP_HEADER = enum(
    AUTHORIZATION='Authorization',
    CONTENT_LENGTH='Content-Length',
    CONTENT_TYPE='Content-Type',
    CONTENT_MD5='Content-MD5',
    CONTENT_RANGE='Content-Range',
    RANGE='Range',
    LAST_MODIFIED='Last-Modified',
    ETAG='ETag',
    DATE='Date',
    EXPIRES='Expires',
    USER_AGENT='User-Agent',
    X_NOS_REQUEST_ID='x-nos-request-id',
    X_NOS_COPY_SOURCE='x-nos-copy-source',
    X_NOS_MOVE_SOURCE='x-nos-move-source',
    X_NOS_OBJECT_MD5='x-nos-Object-md5'
)

RETURN_KEY = enum(
    X_NOS_REQUEST_ID='x_nos_request_id',
    RESPONSE='response',
    ETAG='etag',
    CONTENT_LENGTH='content_length',
    CONTENT_RANGE='content_range',
    CONTENT_TYPE='content_type',
    LAST_MODIFIED='last_modified',
    BODY='body'
)

SUB_RESOURCE = set([
    'acl',
    'location',
    'versioning',
    'versions',
    'versionId',
    'uploadId',
    'uploads',
    'partNumber',
    'delete',
    'deduplication',
    'crop',
    'resize',
])

VERSION = '1.0.1'
CHUNK_SIZE = 65536
MAX_OBJECT_SIZE = 100 * 1024 * 1024
TIME_CST_FORMAT = '%a, %d %b %Y %H:%M:%S Asia/Shanghai'
METADATA_PREFIX = 'x-nos-meta-'
NOS_HEADER_PREFIX = 'x-nos-'
USER_AGENT = 'nos-python-sdk/%s python%s %s' % (VERSION, platform.python_version(), ' '.join(platform.uname()))
