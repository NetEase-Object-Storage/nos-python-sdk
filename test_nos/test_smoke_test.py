# -*- coding:utf8 -*-

from .test_cases import TestCase
import hashlib
import json
import nos


class TestSmokeTest(TestCase):
    ACCESS_KEY_ID = 'xxxxxxxxxx'
    ACCESS_KEY_SECRET = 'xxxxxxxxxx'
    BUCKET = 'xxxx'
    KEYS = [
        u'1特殊 字符`-=[]\\;\',./ ~!@#$%^&*()_+{}|:<>?"',
        u'2特殊 字符`-=[]\\;\',./ ~!@#$%^&*()_+{}|:<>?"',
        u'3特殊 字符`-=[]\\;\',./ ~!@#$%^&*()_+{}|:<>?"',
        u'4特殊 字符`-=[]\\;\',./ ~!@#$%^&*()_+{}|:<>?"',
    ]
    BODY_STR = 'This is a test string!\r\n\r\n'
    BODY_DICT = {"a": 1, "b": 2, "c": 3}
    BODY_LIST = ["a", "b", "c"]
    BODY_FILE = open('setup.py', 'rb')

    def clean_objects_http(self):
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=False
        )

        # delete objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        keys = [i.findtext('Key') for i in resp.findall('Contents')]
        if keys:
            client.delete_objects(self.BUCKET, keys)

        # head object to check
        for i in keys:
            self.assertRaises(nos.exceptions.NotFoundError,
                              client.head_object, self.BUCKET, i)

        # list objects to check
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        keys = [i.findtext('Key') for i in resp.findall('Contents')]
        self.assertEquals([], keys)

        # abort multipart upload
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Upload'):
            client.abort_multipart_upload(
                bucket=self.BUCKET,
                key=i.findtext('Key'),
                upload_id=i.findtext('UploadId')
            )

        # list multipart uploads to check
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        self.assertEquals([], [i for i in resp.findall('Upload')])

    def test_client_http(self):
        self.assertEquals(self.ACCESS_KEY_ID.startswith('xxxx'), False)
        self.assertEquals(self.ACCESS_KEY_SECRET.startswith('xxxx'), False)
        self.assertEquals(self.BUCKET.startswith('xxxx'), False)

        self.clean_objects_http()

        # create client
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=False
        )

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[0], self.BODY_STR)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[0])
        g_md5 = r['etag']

        body = r['body'].read()
        self.assertEquals(p_md5, g_md5)
        self.assertEquals(self.BODY_STR, body)

        md5sum = hashlib.md5(self.BODY_STR).hexdigest()
        self.assertEquals(md5sum, p_md5)

    def test_multipart_upload_http(self):
        self.clean_objects_http()
        info = {}
        body_part1 = self.BODY_STR * 1024 * 1024 * 2
        body_part2 = self.BODY_STR * 1024 * 1024 * 1
        body_all = body_part1 + body_part2
        md5sum_part1 = hashlib.md5(body_part1).hexdigest()
        md5sum_part2 = hashlib.md5(body_part2).hexdigest()
        md5sum = hashlib.md5("%s-%s-" % (md5sum_part1, md5sum_part2)).hexdigest()

        # create client
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=False
        )

        # create multipart upload
        r = client.create_multipart_upload(
            self.BUCKET, self.KEYS[0],
            meta_data={'x-nos-meta-hello': 'world'}
        )
        resp = r['response']
        self.assertEquals(self.BUCKET, resp.findtext('Bucket'))
        self.assertEquals(self.KEYS[0], resp.findtext('Key'))
        upload_id = resp.findtext('UploadId')

        # upload part
        r = client.upload_part(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            part_num=1,
            upload_id=upload_id,
            body=body_part1
        )
        info['1'] = r['etag']
        self.assertEquals(md5sum_part1, r['etag'])

        # upload part
        r = client.upload_part(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            part_num=2,
            upload_id=upload_id,
            body=body_part2
        )
        info['2'] = r['etag']
        self.assertEquals(md5sum_part2, r['etag'])

        # list parts
        r = client.list_parts(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            upload_id=upload_id
        )
        resp = r['response']
        for i in resp.findall('Part'):
            self.assertEquals(
                i.findtext('ETag').strip('a'),
                info[i.findtext('PartNumber')]
            )

        # list multipart uploads
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Upload'):
            if upload_id == i.findtext('UploadId'):
                self.assertEquals(self.KEYS[0], i.findtext('Key'))

        # complete multipart upload
        r = client.complete_multipart_upload(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            upload_id=upload_id,
            info=[{'part_num': x, 'etag': y} for x, y in info.iteritems()],
            meta_data={'x-nos-meta-hello': 'world'}
        )
        resp = r['response']
        self.assertEquals(self.BUCKET, resp.findtext('Bucket'))
        self.assertEquals(self.KEYS[0], resp.findtext('Key'))
        self.assertEquals(md5sum, resp.findtext('ETag').strip())

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[0])
        g_md5 = r['etag'].split('-')[0]

        body = r['body'].read()
        self.assertEquals(body_all, body)
        self.assertEquals(md5sum, g_md5)

        # create multipart upload
        r = client.create_multipart_upload(self.BUCKET, self.KEYS[1])
        resp = r['response']
        self.assertEquals(self.BUCKET, resp.findtext('Bucket'))
        self.assertEquals(self.KEYS[1], resp.findtext('Key'))
        upload_id = resp.findtext('UploadId')

        # abort multipart upload
        r = client.abort_multipart_upload(
            bucket=self.BUCKET,
            key=self.KEYS[1],
            upload_id=upload_id
        )

        # list multipart uploads
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Upload'):
            if upload_id == i.findtext('UploadId'):
                raise

    def test_nos_client_http(self):
        self.clean_objects_http()
        info = {}

        # create client
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=False
        )

        # put invalid object name
        self.assertRaises(nos.exceptions.InvalidObjectName,
                          client.put_object, 'aa', '', '')

        # put invalid bucket name
        self.assertRaises(nos.exceptions.InvalidBucketName,
                          client.put_object, '', 'bb', '')

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[0], self.BODY_STR,
                              meta_data={'x-nos-meta-hello': 'world'})
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[0])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[0])
        h_md5 = r['etag']

        b_str = self.BODY_STR
        md5_str = hashlib.md5(b_str).hexdigest()
        info[self.KEYS[0]] = md5_str
        self.assertEquals(h_md5, md5_str)
        self.assertEquals(g_md5, md5_str)
        self.assertEquals(p_md5, md5_str)
        self.assertEquals(b_str, body)

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[1], self.BODY_DICT)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[1])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[1])
        h_md5 = r['etag']

        b_dict = json.dumps(self.BODY_DICT)
        md5_dict = hashlib.md5(b_dict).hexdigest()
        info[self.KEYS[1]] = md5_dict
        self.assertEquals(h_md5, md5_dict)
        self.assertEquals(g_md5, md5_dict)
        self.assertEquals(p_md5, md5_dict)
        self.assertEquals(b_dict, body)

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[2], self.BODY_LIST)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[2])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[2])
        h_md5 = r['etag']

        b_list = json.dumps(self.BODY_LIST)
        md5_list = hashlib.md5(b_list).hexdigest()
        info[self.KEYS[2]] = md5_list
        self.assertEquals(h_md5, md5_list)
        self.assertEquals(g_md5, md5_list)
        self.assertEquals(p_md5, md5_list)
        self.assertEquals(b_list, body)

        # put object
        self.BODY_FILE.seek(0)
        r = client.put_object(self.BUCKET, self.KEYS[3], self.BODY_FILE)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[3])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[3])
        h_md5 = r['etag']

        self.BODY_FILE.seek(0)
        b_file = self.BODY_FILE.read()
        md5_file = hashlib.md5(b_file).hexdigest()
        info[self.KEYS[3]] = md5_file
        self.assertEquals(h_md5, md5_file)
        self.assertEquals(g_md5, md5_file)
        self.assertEquals(p_md5, md5_file)
        self.assertEquals(b_file, body)

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # move object
        r = client.move_object(
            self.BUCKET,
            self.KEYS[0],
            self.BUCKET,
            self.KEYS[3]
        )
        info[self.KEYS[3]] = info.pop(self.KEYS[0])

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # copy object
        r = client.copy_object(
            self.BUCKET,
            self.KEYS[1],
            self.BUCKET,
            self.KEYS[0]
        )
        info[self.KEYS[0]] = info[self.KEYS[1]]

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # delete object
        r = client.delete_object(
            self.BUCKET,
            self.KEYS[3]
        )
        info.pop(self.KEYS[3], '')
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[3])

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # delete objects
        r = client.delete_objects(
            self.BUCKET,
            [self.KEYS[1], self.KEYS[2]]
        )
        self.assertRaises(nos.exceptions.BadRequestError,
                          client.delete_objects, self.BUCKET, [])
        self.assertRaises(nos.exceptions.MultiObjectDeleteException,
                          client.delete_objects, self.BUCKET, [self.KEYS[3]])
        info.pop(self.KEYS[1], '')
        info.pop(self.KEYS[2], '')
        info.pop(self.KEYS[3], '')
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[1])
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[2])
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[3])

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # head object
        client.head_object(
            bucket=self.BUCKET,
            key=self.KEYS[0]
        )

    def clean_objects_https(self):
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=True
        )

        # delete objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        keys = [i.findtext('Key') for i in resp.findall('Contents')]
        if keys:
            client.delete_objects(self.BUCKET, keys)

        # head object to check
        for i in keys:
            self.assertRaises(nos.exceptions.NotFoundError,
                              client.head_object, self.BUCKET, i)

        # list objects to check
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        keys = [i.findtext('Key') for i in resp.findall('Contents')]
        self.assertEquals([], keys)

        # abort multipart upload
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Upload'):
            client.abort_multipart_upload(
                bucket=self.BUCKET,
                key=i.findtext('Key'),
                upload_id=i.findtext('UploadId')
            )

        # list multipart uploads to check
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        self.assertEquals([], [i for i in resp.findall('Upload')])

    def test_client_https(self):
        self.assertEquals(self.ACCESS_KEY_ID.startswith('xxxx'), False)
        self.assertEquals(self.ACCESS_KEY_SECRET.startswith('xxxx'), False)
        self.assertEquals(self.BUCKET.startswith('xxxx'), False)

        self.clean_objects_https()

        # create client
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=True
        )

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[0], self.BODY_STR)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[0])
        g_md5 = r['etag']

        body = r['body'].read()
        self.assertEquals(p_md5, g_md5)
        self.assertEquals(self.BODY_STR, body)

        md5sum = hashlib.md5(self.BODY_STR).hexdigest()
        self.assertEquals(md5sum, p_md5)

    def test_multipart_upload_https(self):
        self.clean_objects_https()
        info = {}
        body_part1 = self.BODY_STR * 1024 * 1024 * 2
        body_part2 = self.BODY_STR * 1024 * 1024 * 1
        body_all = body_part1 + body_part2
        md5sum_part1 = hashlib.md5(body_part1).hexdigest()
        md5sum_part2 = hashlib.md5(body_part2).hexdigest()
        md5sum = hashlib.md5("%s-%s-" % (md5sum_part1, md5sum_part2)).hexdigest()

        # create client
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=True
        )

        # create multipart upload
        r = client.create_multipart_upload(
            self.BUCKET, self.KEYS[0],
            meta_data={'x-nos-meta-hello': 'world'}
        )
        resp = r['response']
        self.assertEquals(self.BUCKET, resp.findtext('Bucket'))
        self.assertEquals(self.KEYS[0], resp.findtext('Key'))
        upload_id = resp.findtext('UploadId')

        # upload part
        r = client.upload_part(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            part_num=1,
            upload_id=upload_id,
            body=body_part1
        )
        info['1'] = r['etag']
        self.assertEquals(md5sum_part1, r['etag'])

        # upload part
        r = client.upload_part(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            part_num=2,
            upload_id=upload_id,
            body=body_part2
        )
        info['2'] = r['etag']
        self.assertEquals(md5sum_part2, r['etag'])

        # list parts
        r = client.list_parts(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            upload_id=upload_id
        )
        resp = r['response']
        for i in resp.findall('Part'):
            self.assertEquals(
                i.findtext('ETag').strip('a'),
                info[i.findtext('PartNumber')]
            )

        # list multipart uploads
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Upload'):
            if upload_id == i.findtext('UploadId'):
                self.assertEquals(self.KEYS[0], i.findtext('Key'))

        # complete multipart upload
        r = client.complete_multipart_upload(
            bucket=self.BUCKET,
            key=self.KEYS[0],
            upload_id=upload_id,
            info=[{'part_num': x, 'etag': y} for x, y in info.iteritems()]
        )
        resp = r['response']
        self.assertEquals(self.BUCKET, resp.findtext('Bucket'))
        self.assertEquals(self.KEYS[0], resp.findtext('Key'))
        self.assertEquals(md5sum, resp.findtext('ETag').strip())

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[0])
        g_md5 = r['etag'].split('-')[0]

        body = r['body'].read()
        self.assertEquals(body_all, body)
        self.assertEquals(md5sum, g_md5)

        # create multipart upload
        r = client.create_multipart_upload(self.BUCKET, self.KEYS[1])
        resp = r['response']
        self.assertEquals(self.BUCKET, resp.findtext('Bucket'))
        self.assertEquals(self.KEYS[1], resp.findtext('Key'))
        upload_id = resp.findtext('UploadId')

        # abort multipart upload
        r = client.abort_multipart_upload(
            bucket=self.BUCKET,
            key=self.KEYS[1],
            upload_id=upload_id
        )

        # list multipart uploads
        r = client.list_multipart_uploads(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Upload'):
            if upload_id == i.findtext('UploadId'):
                raise

    def test_nos_client_https(self):
        self.clean_objects_https()
        info = {}

        # create client
        client = nos.Client(
            access_key_id=self.ACCESS_KEY_ID,
            access_key_secret=self.ACCESS_KEY_SECRET,
            enable_ssl=True
        )

        # put invalid object name
        self.assertRaises(nos.exceptions.InvalidObjectName,
                          client.put_object, 'aa', '', '')

        # put invalid bucket name
        self.assertRaises(nos.exceptions.InvalidBucketName,
                          client.put_object, '', 'bb', '')

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[0], self.BODY_STR,
                              meta_data={'x-nos-meta-hello': 'world'})
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[0])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[0])
        h_md5 = r['etag']

        b_str = self.BODY_STR
        md5_str = hashlib.md5(b_str).hexdigest()
        info[self.KEYS[0]] = md5_str
        self.assertEquals(h_md5, md5_str)
        self.assertEquals(g_md5, md5_str)
        self.assertEquals(p_md5, md5_str)
        self.assertEquals(b_str, body)

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[1], self.BODY_DICT)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[1])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[1])
        h_md5 = r['etag']

        b_dict = json.dumps(self.BODY_DICT)
        md5_dict = hashlib.md5(b_dict).hexdigest()
        info[self.KEYS[1]] = md5_dict
        self.assertEquals(h_md5, md5_dict)
        self.assertEquals(g_md5, md5_dict)
        self.assertEquals(p_md5, md5_dict)
        self.assertEquals(b_dict, body)

        # put object
        r = client.put_object(self.BUCKET, self.KEYS[2], self.BODY_LIST)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[2])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[2])
        h_md5 = r['etag']

        b_list = json.dumps(self.BODY_LIST)
        md5_list = hashlib.md5(b_list).hexdigest()
        info[self.KEYS[2]] = md5_list
        self.assertEquals(h_md5, md5_list)
        self.assertEquals(g_md5, md5_list)
        self.assertEquals(p_md5, md5_list)
        self.assertEquals(b_list, body)

        # put object
        self.BODY_FILE.seek(0)
        r = client.put_object(self.BUCKET, self.KEYS[3], self.BODY_FILE)
        p_md5 = r['etag']

        # get object
        r = client.get_object(self.BUCKET, self.KEYS[3])
        g_md5 = r['etag']
        body = r['body'].read()

        # head object
        r = client.head_object(self.BUCKET, self.KEYS[3])
        h_md5 = r['etag']

        self.BODY_FILE.seek(0)
        b_file = self.BODY_FILE.read()
        md5_file = hashlib.md5(b_file).hexdigest()
        info[self.KEYS[3]] = md5_file
        self.assertEquals(h_md5, md5_file)
        self.assertEquals(g_md5, md5_file)
        self.assertEquals(p_md5, md5_file)
        self.assertEquals(b_file, body)

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # move object
        r = client.move_object(
            self.BUCKET,
            self.KEYS[0],
            self.BUCKET,
            self.KEYS[3]
        )
        info[self.KEYS[3]] = info.pop(self.KEYS[0])

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # copy object
        r = client.copy_object(
            self.BUCKET,
            self.KEYS[1],
            self.BUCKET,
            self.KEYS[0]
        )
        info[self.KEYS[0]] = info[self.KEYS[1]]

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # delete object
        r = client.delete_object(
            self.BUCKET,
            self.KEYS[3]
        )
        info.pop(self.KEYS[3], '')
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[3])

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # delete objects
        r = client.delete_objects(
            self.BUCKET,
            [self.KEYS[1], self.KEYS[2]]
        )
        self.assertRaises(nos.exceptions.BadRequestError,
                          client.delete_objects, self.BUCKET, [])
        self.assertRaises(nos.exceptions.MultiObjectDeleteException,
                          client.delete_objects, self.BUCKET, [self.KEYS[3]])
        info.pop(self.KEYS[1], '')
        info.pop(self.KEYS[2], '')
        info.pop(self.KEYS[3], '')
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[1])
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[2])
        self.assertRaises(nos.exceptions.NotFoundError, client.head_object,
                          self.BUCKET, self.KEYS[3])

        # list objects
        r = client.list_objects(
            bucket=self.BUCKET
        )
        resp = r['response']
        for i in resp.findall('Contents'):
            self.assertEquals(
                info[i.findtext('Key')],
                i.findtext('ETag').strip('"')
            )

        # head object
        client.head_object(
            bucket=self.BUCKET,
            key=self.KEYS[0]
        )