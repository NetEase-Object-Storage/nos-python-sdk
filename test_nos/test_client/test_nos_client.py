# -*- coding:utf8 -*-

from datetime import datetime
from StringIO import StringIO
from ..test_cases import ClinetTestCase
from nos.client.nos_client import parse_xml
from nos.exceptions import XmlParseError, InvalidBucketName, InvalidObjectName


class TestClient(ClinetTestCase):
    def test_parse_xml(self):
        status, headers, body = 200, {}, StringIO('')
        self.assertRaises(XmlParseError, parse_xml, status, headers, body)

    def test_delete_object(self):
        self.client.delete_object('bucket', 'key')
        self.assert_url_called('DELETE', 'bucket', 'key')

    def test_delete_objects(self):
        self.client.delete_objects('bucket', ['key1', 'key2'])
        self.assert_url_called('POST', 'bucket', '')

    def test_get_object(self):
        self.client.get_object(
            'bucket', 'key', range='0-100',
            if_modified_since=datetime(2015, 1, 1)
        )
        self.assert_url_called('GET', 'bucket', 'key')

    def test_head_object(self):
        self.client.head_object('bucket', 'key')
        self.assert_url_called('HEAD', 'bucket', 'key')

    def test_list_objects(self):
        self.client.list_objects('bucket', delimiter='', marker='',
                                 limit=10, prefix='')
        self.assert_url_called('GET', 'bucket', '')

    def test_put_object(self):
        self.client.put_object('bucket', 'key', 'hello', storage_class='cheap')
        self.assert_url_called('PUT', 'bucket', 'key')

    def test_copy_object(self):
        self.client.copy_object('bucket', 'key2', 'bucket', 'key')
        self.assert_url_called('PUT', 'bucket', 'key', 1)
        self.client.copy_object(u'bucket', u'key2', u'bucket', u'key')
        self.assert_url_called('PUT', 'bucket', 'key', 2)
        self.assertRaises(InvalidBucketName, self.client.copy_object,
                          '', 'key2', 'bucket', 'key')
        self.assertRaises(InvalidObjectName, self.client.copy_object,
                          'bucket', '', 'bucket', 'key')

    def test_move_object(self):
        self.client.move_object('bucket', 'key2', 'bucket', 'key')
        self.assert_url_called('PUT', 'bucket', 'key', 1)
        self.client.move_object(u'bucket', u'key2', u'bucket', u'key')
        self.assert_url_called('PUT', 'bucket', 'key', 2)
        self.assertRaises(InvalidBucketName, self.client.move_object,
                          '', 'key2', 'bucket', 'key')
        self.assertRaises(InvalidObjectName, self.client.move_object,
                          'bucket', '', 'bucket', 'key')

    def test_create_multipart_upload(self):
        self.client.create_multipart_upload('bucket', 'key',
                                            storage_class='cheap')
        self.assert_url_called('POST', 'bucket', 'key')

    def test_upload_part(self):
        self.client.upload_part('bucket', 'key', 1, '21', 'hello')
        self.assert_url_called('PUT', 'bucket', 'key')

    def test_complete_multipart_upload(self):
        self.client.complete_multipart_upload(
            'bucket', 'key', '11212sd',
            [{'part_num': 1, 'etag': 'ab1234'},
             {'part_num': 2, 'etag': 'da4513'}],
            object_md5='3425b2123')
        self.assert_url_called('POST', 'bucket', 'key')

    def test_abort_multipart_upload(self):
        self.client.abort_multipart_upload('bucket', 'key', 'asdsa')
        self.assert_url_called('DELETE', 'bucket', 'key')

    def test_list_parts(self):
        self.client.list_parts('bucket', 'key', 'asdsa',
                               limit=10, part_number_marker='')
        self.assert_url_called('GET', 'bucket', 'key')

    def test_list_multipart_uploads(self):
        self.client.list_multipart_uploads('bucket', limit=10, key_marker='')
        self.assert_url_called('GET', 'bucket', '')
