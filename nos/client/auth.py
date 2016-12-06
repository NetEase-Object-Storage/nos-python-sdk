# -*- coding:utf8 -*-

import base64
import hashlib
import hmac
import time
import urllib2
import copy
from .utils import (HTTP_HEADER, NOS_HEADER_PREFIX, TIME_CST_FORMAT,
                    CHUNK_SIZE, SUB_RESOURCE, USER_AGENT)


class RequestMetaData(object):
    """
    Used to generate authorization header  and request url
    """
    def __init__(self, access_key_id, access_key_secret, method,
                 bucket=None, key=None, end_point='nos.netease.com',
                 params={}, body=None, headers={}, enable_ssl=False):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.method = method
        self.bucket = bucket
        self.key = key
        self.end_point = end_point
        self.params = params
        self.headers = copy.deepcopy(headers)
        self.enable_ssl = enable_ssl
        self.body = body
        self.url = ''

        self._complete_headers()
        self._complete_url()

    def get_url(self):
        return self.url

    def get_headers(self):
        return self.headers

    def _complete_headers(self):
        # init date header
        self.headers[HTTP_HEADER.DATE] = time.strftime(
            TIME_CST_FORMAT, time.gmtime(time.time() + 8 * 3600)
        )

        # init user-agent header
        self.headers.setdefault(HTTP_HEADER.USER_AGENT, USER_AGENT)

        # init content-md5 header
        if self.body is not None:
            md5 = hashlib.md5()
            if isinstance(self.body, file):
                offset = self.body.tell()
                while True:
                    data = self.body.read(CHUNK_SIZE)
                    if not data:
                        break
                    md5.update(data)
                md5sum = md5.hexdigest()
                self.headers[HTTP_HEADER.CONTENT_MD5] = md5sum
                self.body.seek(offset, 0)
            else:
                md5.update(self.body)
                md5sum = md5.hexdigest()
                self.headers[HTTP_HEADER.CONTENT_MD5] = md5sum

        # init authorization header
        if None not in (self.access_key_id, self.access_key_secret):
            str_to_sign = self._get_string_to_sign()
            hmac_sha1 = hmac.new(str(self.access_key_secret),
                                 str_to_sign, hashlib.sha256)
            b64_hmac_sha1 = base64.encodestring(hmac_sha1.digest()).strip()
            authorization_string = b64_hmac_sha1.rstrip('\n')

            self.headers[HTTP_HEADER.AUTHORIZATION] = 'NOS %s:%s' % (
                self.access_key_id, authorization_string
            )

    def _complete_url(self):
        """
        build the url with query string
        :return: url with query string
        """
        self.url = "https://" if self.enable_ssl else "http://"

        if self.bucket is None:
            self.url += '%s/' % self.end_point
        else:
            self.url += '%s.%s/' % (self.bucket, self.end_point)

        if self.key is not None:
            self.url += urllib2.quote(self.key.strip('/'), '*')

        if not self.params:
            return

        pairs = []
        for k, v in self.params.iteritems():
            piece = k
            if v is not None:
                piece += "=%s" % urllib2.quote(str(v), '*')
            pairs.append(piece)
        query_string = '&'.join(pairs)
        self.url += ("?" + query_string)

    def _get_string_to_sign(self):
        """
        Generate string which should be signed and setted in header while
        sending request
        @rtype: string
        @return: canonical string for netease storage service
        """
        headers = dict([(k.lower(), str(v).strip().strip("'\""))
                        for k, v in self.headers.iteritems()])

        meta_headers = dict([(k, v) for k, v in headers.iteritems()
                             if k.startswith(NOS_HEADER_PREFIX)])

        content_type = headers.get(HTTP_HEADER.CONTENT_TYPE.lower(), '')
        content_md5 = headers.get(HTTP_HEADER.CONTENT_MD5.lower(), '')
        date = headers.get(HTTP_HEADER.DATE.lower(), '')
        expires = headers.get(HTTP_HEADER.EXPIRES.lower(), '')

        # compute string to sign
        str_to_sign = '%s\n%s\n%s\n%s\n' % (
            self.method,
            content_md5,
            content_type,
            expires or date
        )

        sorted_meta_headers = meta_headers.keys()
        sorted_meta_headers.sort()

        for meta_header in sorted_meta_headers:
            str_to_sign += '%s:%s\n' % (meta_header, meta_headers[meta_header])

        str_to_sign += "%s" % (self._get_canonicalized_resource())
        return str_to_sign

    def _get_canonicalized_resource(self):
        """
        get canoicalized resource /bucket/obj?upload
        """
        # append the root path
        buf = '/'
        # append the bucket if it exists
        if self.bucket is not None:
            buf += "%s/" % self.bucket

        # add the key.  even if it doesn't exist, add the slash
        if self.key is not None:
            buf += urllib2.quote(self.key.strip('/'), '*')

        # handle sub source in special query string arguments
        if self.params:
            buf += "?"
            pairs = []
            for k, v in self.params.iteritems():
                if k not in SUB_RESOURCE:
                    continue
                piece = k
                if v is not None:
                    piece += "=%s" % urllib2.quote(str(v), '*')
                pairs.append(piece)

            buf += '&'.join(pairs)
            if len(pairs) == 0:
                return buf.rstrip('?')

        return buf
