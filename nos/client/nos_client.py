# -*- coding:utf8 -*-

from .utils import (HTTP_METHOD, HTTP_HEADER, RETURN_KEY)
from ..exceptions import (XmlParseError, MultiObjectDeleteException,
                          InvalidBucketName, InvalidObjectName)
from ..transport import Transport
from ..compat import ET

import cgi
import urllib2


def parse_xml(status, headers, body):
    try:
        data = body.read()
        return ET.fromstring(data)
    except Exception as e:
        raise XmlParseError(
            '\n%s\nstatus: %s\nheaders: %s\nbody: \n%s\n' % (
                str(e), status, headers, data
            ),
            e
        )


class Client(object):
    """
    The client for accessing the Netease NOS web service.

    You can use it as follows:


        import nos

        access_key_id = 'xxxxxxxxx'
        access_key_secret = 'xxxxxxxxx'
        bucket = 'xxxx'
        key = 'xxxx'

        client = nos.Client(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        try:
            resp = client.get_object(
                bucket=bucket,
                key=key
            )
        except nos.exceptions.ServiceException as e:
            print (
                'ServiceException: %s\n'
                'status_code: %s\n'
                'error_type: %s\n'
                'error_code: %s\n'
                'request_id: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.status_code,
                e.error_type,
                e.error_code,
                e.request_id,
                e.message
            )
        except nos.exceptions.ClientException as e:
            print (
                'ClientException: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.message
            )

    """
    def __init__(self, access_key_id=None, access_key_secret=None,
                 transport_class=Transport, **kwargs):
        """
        If the bucket is public-read, the parameter of `access_key_id` or
        `access_key_secret` can be set to `None`, else the parameter should be
        given by string.

        :arg access_key_id(string): The access key ID. `None` is set by default.
        :arg access_key_secret(string): The secret access key. `None` is set by
          default.
        :arg transport_class(class): The class will be used for
          transport. `nos.transport.Transport` is set by default.
        :arg kwargs: Other optional parameters.
            :opt_arg end_point(string): The point which the object will
              transport to. `nos.netease.com` is set by default.
            :opt_arg num_pools(integer): Number of connection pools to cache
              before discarding the leastrecently used pool. `16` is set by
              default.
            :opt_arg timeout(integer): Timeout while connecting to server.
            :opt_arg max_retries(integer): The count of retry when get http 5XX.
              `2` is set by default.
            :opt_arg retry_backoff_factor(float): A backoff factor to apply
                between attempts after the second try (most errors are resolved immediately
                by a second try without a delay). client will sleep for::
                    {backoff factor} * (2 ** ({number of total retries} - 1))
                seconds. If the backoff_factor is 0.1, then :func:`.sleep` will sleep for
                [0.1s, 0.2s, 0.4s, ...] between retries. It will never be longer than `BACKOFF_MAX`.
                By default, backoff is disabled (set to 0).
            :opt_arg enable_ssl(boolean): Use https while connecting to server.
              False is set by default, so default use http.
        """
        self.transport = transport_class(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            **kwargs
        )

    def delete_object(self, bucket, key):
        """
        Delete the specified object in the specified bucket.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        _, headers, _ = self.transport.perform_request(
            HTTP_METHOD.DELETE, bucket, key
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            )
        }

    def delete_objects(self, bucket, keys, quiet=False):
        """
        Delete the objects in the specified bucket.

        :arg bucket(string): The name of the Nos bucket.
        :arg keys(list): The list of the Nos object which can be deleted.
        :arg quiet(boolean): Is quiet mode enabled, false by default.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element response(ElementTree): The response body of NOS server.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        body = self.__get_delete_objects_body(keys, quiet)
        params = {'delete': None}
        status, headers, body = self.transport.perform_request(
            HTTP_METHOD.POST, bucket, params=params, body=body
        )

        ret_xml = parse_xml(status, headers, body)
        errors = [
            {
                'key': i.findtext('Key', ''),
                'code': i.findtext('Code', ''),
                'message': i.findtext('Message', '')
            }
            for i in ret_xml.findall('Error')
        ]
        if errors:
            raise MultiObjectDeleteException(errors)

        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.RESPONSE: ret_xml
        }

    def get_object(self, bucket, key, **kwargs):
        """
        Get the object stored in NOS under the specified bucket and key.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :arg kwargs: Other optional parameters.
            :opt_arg range(string): The Range header of request.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element content_length(integer): The Content-Length header of
              response.
            :element content_range(string): The Content-Range header of
              response.
            :element content_type(string): The Content-Type header of response.
            :element etag(string): The ETag header of response.
            :element body(StreamingBody): The response body of NOS server, which
              can use functions such as read(), readline().
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        headers = {}
        if 'range' in kwargs:
            headers[HTTP_HEADER.RANGE] = kwargs['range']

        _, headers, body = self.transport.perform_request(
            HTTP_METHOD.GET, bucket, key, headers=headers
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.CONTENT_LENGTH: int(
                headers.get(HTTP_HEADER.CONTENT_LENGTH, 0)
            ),
            RETURN_KEY.CONTENT_RANGE: headers.get(
                HTTP_HEADER.CONTENT_RANGE, ''
            ),
            RETURN_KEY.CONTENT_TYPE: headers.get(HTTP_HEADER.CONTENT_TYPE, ''),
            RETURN_KEY.ETAG: headers.get(HTTP_HEADER.ETAG, '').strip("'\""),
            RETURN_KEY.BODY: body
        }

    def head_object(self, bucket, key):
        """
        Get info of the object stored in NOS under the specified bucket and key.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element content_length(integer): The Content-Length header of
              response.
            :element last_modified(string): The Last-Modified header of
              response.
            :element content_type(string): The Content-Type header of response.
            :element etag(string): The ETag header of response.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        _, headers, _ = self.transport.perform_request(
            HTTP_METHOD.HEAD, bucket, key
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.CONTENT_LENGTH: int(
                headers.get(HTTP_HEADER.CONTENT_LENGTH, 0)
            ),
            RETURN_KEY.LAST_MODIFIED: headers.get(
                HTTP_HEADER.LAST_MODIFIED, ''
            ),
            RETURN_KEY.CONTENT_TYPE: headers.get(HTTP_HEADER.CONTENT_TYPE, ''),
            RETURN_KEY.ETAG: headers.get(HTTP_HEADER.ETAG, '').strip("'\"")
        }

    def list_objects(self, bucket, **kwargs):
        """
        Return a list of summary information about the objects in the specified
        buckets.

        :arg bucket(string): The name of the Nos bucket.
        :arg kwargs: Other optional parameters.
            :opt_arg delimiter(string): Optional parameter that causes keys
              that contain the same string between the prefix and the first
              occurrence of the delimiter to be rolled up into a single result
              element. These rolled-up keys are not returned elsewhere in the
              response. The most commonly used delimiter is "/", which
              simulates a hierarchical organization similar to a file system
              directory structure.
            :opt_arg marker(string): Optional parameter indicating where in the
              bucket to begin listing. The list will only include keys that
              occur lexicographically after the marker.
            :opt_arg limit(integer): Optional parameter indicating the maximum
              number of keys to include in the response. Nos might return fewer
              than this, but will not return more. Even if maxKeys is not
              specified, Nos will limit the number of results in the response.
            :opt_arg prefix(string): Optional parameter restricting the response
              to keys which begin with the specified prefix. You can use
              prefixes to separate a bucket into different sets of keys in a way
              similar to how a file system uses folders.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element response(ElementTree): The response body of NOS server.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        keys = set(['delimiter', 'marker', 'limit', 'prefix'])
        params = {}
        for k, v in kwargs.iteritems():
            if k in keys:
                params[k] = v

        limit = params.pop('limit', None)
        if limit is not None:
            params['max-keys'] = str(limit)

        status, headers, body = self.transport.perform_request(
            HTTP_METHOD.GET, bucket, params=params
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.RESPONSE: parse_xml(status, headers, body)
        }

    def put_object(self, bucket, key, body, **kwargs):
        """
        Upload the specified object to NOS under the specified bucket and key
        name.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :arg body(serializable_object): The content of the Nos object, which can
          be file, dict, list, string or any other serializable object.
        :arg kwargs: Other optional parameters.
            :opt_arg meta_data(dict): Represents the object metadata that is
              stored with Nos. This includes custom user-supplied metadata and
              the key should start with 'x-nos-meta-'.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element etag(string): The ETag header of response.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        headers = {}
        for k, v in kwargs.get('meta_data', {}).iteritems():
            headers[k] = v

        _, headers, body = self.transport.perform_request(
            HTTP_METHOD.PUT, bucket, key, body=body, headers=headers
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.ETAG: headers.get(HTTP_HEADER.ETAG, '').strip("'\"")
        }

    def copy_object(self, src_bucket, src_key, dest_bucket, dest_key):
        """
        Copy a source object to a new destination in NOS.

        :arg src_bucket(string): The name of the source bucket.
        :arg src_key(string): The name of the source object.
        :arg dest_bucket(string): The name of the destination bucket.
        :arg dest_key(string): The name of the destination object.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        src_bucket = src_bucket.encode('utf-8') \
                if isinstance(src_bucket, unicode) else src_bucket
        src_key = src_key.encode('utf-8') \
                if isinstance(src_key, unicode) else src_key
        if src_bucket is not None and src_bucket == '':
            raise InvalidBucketName()
        if src_key is not None and src_key == '':
            raise InvalidObjectName()

        headers = {}
        headers[HTTP_HEADER.X_NOS_COPY_SOURCE] = '/%s/%s' % (
            src_bucket, urllib2.quote(src_key.strip('/'), '*')
        )

        _, headers, _ = self.transport.perform_request(
            HTTP_METHOD.PUT, dest_bucket, dest_key, headers=headers
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            )
        }

    def move_object(self, src_bucket, src_key, dest_bucket, dest_key):
        """
        Move a source object to a new destination in NOS.

        :arg src_bucket(string): The name of the source bucket.
        :arg src_key(string): The name of the source object.
        :arg dest_bucket(string): The name of the destination bucket.
        :arg dest_key(string): The name of the destination object.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        src_bucket = src_bucket.encode('utf-8') \
                if isinstance(src_bucket, unicode) else src_bucket
        src_key = src_key.encode('utf-8') \
                if isinstance(src_key, unicode) else src_key
        if src_bucket is not None and src_bucket == '':
            raise InvalidBucketName()
        if src_key is not None and src_key == '':
            raise InvalidObjectName()

        headers = {}
        headers[HTTP_HEADER.X_NOS_MOVE_SOURCE] = '/%s/%s' % (
            src_bucket, urllib2.quote(src_key.strip('/'), '*')
        )

        _, headers, _ = self.transport.perform_request(
            HTTP_METHOD.PUT, dest_bucket, dest_key, headers=headers
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            )
        }

    def create_multipart_upload(self, bucket, key, **kwargs):
        """
        Initiate a multipart upload and returns an response which contains an
        upload ID. This upload ID associates all the parts in the specific
        upload and is used in each of your subsequent requests. You also include
        this upload ID in the final request to either complete, or abort the
        multipart upload request.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :arg kwargs: Other optional parameters.
            :opt_arg meta_data(dict): Represents the object metadata that is
              stored with Nos. This includes custom user-supplied metadata and
              the key should start with 'x-nos-meta-'.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element response(ElementTree): The response body of NOS server.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        headers = {}
        for k, v in kwargs.get('meta_data', {}).iteritems():
            headers[k] = v

        params = {'uploads': None}
        body = ''
        status, headers, body = self.transport.perform_request(
            HTTP_METHOD.POST, bucket, key, body=body,
            params=params, headers=headers
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.RESPONSE: parse_xml(status, headers, body)
        }

    def upload_part(self, bucket, key, part_num, upload_id, body):
        """
        Upload a part in a multipart upload. You must initiate a multipart
        upload before you can upload any part.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :arg part_num(integer): The part number describing this part's position
          relative to the other parts in the multipart upload. Part number must
          be between 1 and 10,000 (inclusive).
        :arg upload_id(string): The ID of an existing, initiated multipart
          upload, with which this new part will be associated.
        :arg body(serializable_object): The content of the Nos object, which can
          be file, dict, list, string or any other serializable object.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element etag(string): The ETag header of response.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        params = {
            'partNumber': str(part_num),
            'uploadId': upload_id
        }
        _, headers, body = self.transport.perform_request(
            HTTP_METHOD.PUT, bucket, key, body=body, params=params
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.ETAG: headers.get(HTTP_HEADER.ETAG, '').strip("'\"")
        }

    def complete_multipart_upload(self, bucket, key, upload_id, info, **kwargs):
        """
        Complete a multipart upload by assembling previously uploaded parts.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :arg upload_id(string): The ID of an existing, initiated multipart
          upload, with which this new part will be associated.
        :arg info(list): The list of part numbers and ETags to use when
          completing the multipart upload.
        :arg kwargs: Other optional parameters.
            :opt_arg object_md5(string): MD5 of the whole object which is
              multipart uploaded.
            :opt_arg meta_data(dict): Represents the object metadata that is
              stored with Nos. This includes custom user-supplied metadata and
              the key should start with 'x-nos-meta-'.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element response(ElementTree): The response body of NOS server.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        params = {'uploadId': upload_id}
        headers = {}
        if 'object_md5' in kwargs:
            headers[HTTP_HEADER.X_NOS_OBJECT_MD5] = kwargs['object_md5']

        for k, v in kwargs.get('meta_data', {}).iteritems():
            headers[k] = v

        parts_xml = []
        part_xml = '<Part><PartNumber>%s</PartNumber><ETag>%s</ETag></Part>'
        for i in info:
            parts_xml.append(part_xml % (i['part_num'], i['etag']))
        body = ('<CompleteMultipartUpload>%s</CompleteMultipartUpload>' %
                (''.join(parts_xml)))

        status, headers, body = self.transport.perform_request(
            HTTP_METHOD.POST, bucket, key, body=body,
            params=params, headers=headers
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.RESPONSE: parse_xml(status, headers, body)
        }

    def abort_multipart_upload(self, bucket, key, upload_id):
        """
        Abort a multipart upload. After a multipart upload is aborted, no
        additional parts can be uploaded using that upload ID. The storage
        consumed by any previously uploaded parts will be freed. However, if any
        part uploads are currently in progress, those part uploads may or may
        not succeed. As a result, it may be necessary to abort a given multipart
        upload multiple times in order to completely free all storage consumed
        by all parts.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :arg upload_id(string): The ID of an existing, initiated multipart
          upload, with which this new part will be associated.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        params = {'uploadId': upload_id}
        _, headers, _ = self.transport.perform_request(
            HTTP_METHOD.DELETE, bucket, key, params=params
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            )
        }

    def list_parts(self, bucket, key, upload_id, **kwargs):
        """
        List the parts that have been uploaded for a specific multipart upload.

        This method must include the upload ID, returned by the
        `create_multipart_upload` operation. This request returns a maximum of
        1000 uploaded parts by default. You can restrict the number of parts
        returned by specifying the limit parameter.

        :arg bucket(string): The name of the Nos bucket.
        :arg key(string): The name of the Nos object.
        :arg upload_id(string): The ID of an existing, initiated multipart
          upload, with which this new part will be associated.
        :arg kwargs: Other optional parameters.
            :opt_arg limit(integer): The optional maximum number of parts to be
              returned in the part listing.
            :opt_arg part_number_marker(string): The optional part number marker
              indicating where in the results to being listing parts.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element response(ElementTree): The response body of NOS server.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        params = {'uploadId': upload_id}
        if 'limit' in kwargs:
            params['max-parts'] = str(kwargs['limit'])
        if 'part_number_marker' in kwargs:
            params['part-number-marker'] = kwargs['part_number_marker']

        status, headers, body = self.transport.perform_request(
            HTTP_METHOD.GET, bucket, key, params=params
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.RESPONSE: parse_xml(status, headers, body)
        }

    def list_multipart_uploads(self, bucket, **kwargs):
        """
        List in-progress multipart uploads. An in-progress multipart upload is
        a multipart upload that has been initiated, using the
        `create_multipart_upload` request, but has not yet been completed or
        aborted.

        This operation returns at most 1,000 multipart uploads in the response
        by default. The number of multipart uploads can be further limited using
        the limit parameter.

        :arg bucket(string): The name of the Nos bucket.
        :arg kwargs: Other optional parameters.
            :opt_arg limit(integer): The optional maximum number of uploads to
              return.
            :opt_arg key_marker(string): The optional key marker indicating
              where in the results to begin listing.
        :ret return_value(dict): The response of NOS server.
            :element x_nos_request_id(string): ID which can point out the
              request.
            :element response(ElementTree): The response body of NOS server.
        :raise ClientException: If any errors are occured in the client point.
        :raise ServiceException: If any errors occurred in NOS server point.
        """
        params = {'uploads': None}
        if 'limit' in kwargs:
            params['max-uploads'] = str(kwargs['limit'])
        if 'key_marker' in kwargs:
            params['key-marker'] = kwargs['key_marker']

        status, headers, body = self.transport.perform_request(
            HTTP_METHOD.GET, bucket, params=params
        )
        return {
            RETURN_KEY.X_NOS_REQUEST_ID: headers.get(
                HTTP_HEADER.X_NOS_REQUEST_ID, ''
            ),
            RETURN_KEY.RESPONSE: parse_xml(status, headers, body)
        }

    def __get_delete_objects_body(self, objects, quiet):
        objs = ['<Object><Key>%s</Key></Object>' % (cgi.escape(i))
                for i in objects]
        if not objs:
            objs = ['<Object><Key></Key></Object>']
        return '<Delete><Quiet>%s</Quiet>%s</Delete>' % (
            str(quiet).lower(), ''.join(objs)
        )
