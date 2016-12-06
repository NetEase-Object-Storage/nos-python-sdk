NOS Python SDK
==============

NOS Python SDK实现了NOS对象操作接口，基于此SDK能方便快速地实现Python应用程序来使用NOS的对象存储服务。

支持的功能
----------

对象操作接口
^^^^^^^^^^^^

* Delete Object —— 删除一个对象
* Delete Multiple Objects —— 用一个HTTP请求删除同一个Bucket中的多个对象
* Get Object —— 读取对象内容
* Head Object —— 获取对象相关元数据信息
* List Objects —— 获取一个桶的对象列表
* Put Object —— 上传一个对象
* Put Object - Copy —— 拷贝一个对象
* Put Object - Move —— 桶内部move一个对象

大对象分块操作接口
^^^^^^^^^^^^^^^^^^

* Initiate Multipart Upload —— 初始化分块上传
* Upload Part —— 上传一个分块
* Complete Multipart Upload —— 完成分块上传
* Abort Multipart Upload —— 取消分块上传并删除已上传的分块
* List Parts —— 列出已上传的分块
* List Multipart Uploads —— 列出所有执行中的分块上传事件

接口实现
--------

在调用对象操作接口前需要生成一个nos.Client类的实例。且在调用操作接口时，都有可能抛出异常，可以使用`nos.exceptions.ServiceException`捕获nos服务器异常错误，使用`nos.exceptions.ClientException`捕获nos客户端异常错误。

nos.Client对象实例化
^^^^^^^^^^^^^^^^^^^^

使用举例

::

    client = nos.Client(
        access_key_id="string",
        access_key_secret="string",
        transport_class=nos.transport.Transport,
        **kwargs
    )

参数说明

* access_key_id(string) -- 访问凭证ID。当需要访问的桶属性为Public-read时，可以将该值设置成None。默认值为：None。
* access_key_secret(string) -- 访问凭证密钥。当需要访问的桶属性为Public-read时，可以将该值设置成None。默认值为：None。
* transport_class(class) -- 与NOS服务器进行数据传输的类型，类型中至少需要包含`perform_request`成员函数。默认值为：nos.transport.Transport。
* kwargs -- 其他可选参数，如下。
    * end_point(string) -- 与NOS服务器进行数据传输、交互的服务器的主域名。默认为：`nos-eastchina1.126.net`。
    * num_pools(integer) -- HTTP连接池的大小。默认值为：16。
    * timeout(integer) -- 连接超时的时间，单位：秒。
    * max_retries(integer) -- 当得到HTTP 5XX的服务器错误的响应时，进行重试的次数。默认值为：2。
    * enable_ssl(boolean) -- 与NOS服务器进行数据传输、交互时，是否使用HTTPS。默认值为：False，默认使用HTTP。

nos.Client可能引发的所有异常类型
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

在程序运行过程中，如果遇到错误，Python SDK会抛出相应的异常。所有异常均属于NOSException类，其下分为两个子类：ClientException、ServiceException。在调用Python SDK接口的时候，捕捉这些异常并打印必要的信息有利于定位问题。

ClientException
:::::::::::::::

ClientException包含SDK客户端的异常。比如，上传对象时对象名为空，就会抛出该异常。
ClientException类下有如下子类，用于细分客户端异常：

.. list-table::
    :widths: 5 10
    :header-rows: 1

    * - 类名
      - 抛出异常的原因
    * - InvalidBucketName
      - 传入的桶名为空
    * - InvalidObjectName
      - 传入的对象名为空
    * - FileOpenModeError
      - 出入的对象为文件且没有使用二进制文件方式打开
    * - XmlParseError
      - 解析服务端响应的XML内容失败
    * - SerializationError
      - 上传对象序列化失败
    * - ConnectionError
      - 连接服务端异常
    * - ConnectionTimeout
      - 连接服务端超时

ServiceException
::::::::::::::::

ServiceException包含NOS服务器返回的异常。当NOS服务器返回4xx或5xx的HTTP错误码时，Python SDK会将NOS Server的响应转换为ServiceException。
ServiceException类下有如下子类，用于细分NOS服务器返回的异常：

.. list-table::
    :widths: 5 10
    :header-rows: 1

    * - 类名
      - 抛出异常的原因
    * - MultiObjectDeleteException
      - 批量删除对象时，存在部分对象无法删除
    * - BadRequestError
      - 服务端返回HTTP 400响应
    * - ForbiddenError
      - 服务端返回HTTP 403响应
    * - NotFoundError
      - 服务端返回HTTP 404响应
    * - MethodNotAllowedError
      - 服务端返回HTTP 405响应
    * - ConflictError
      - 服务端返回HTTP 409响应
    * - LengthRequiredError
      - 服务端返回HTTP 411响应
    * - RequestedRangeNotSatisfiableError
      - 服务端返回HTTP 416响应
    * - InternalServerErrorError
      - 服务端返回HTTP 500响应
    * - NotImplementedError
      - 服务端返回HTTP 501响应
    * - ServiceUnavailableError
      - 服务端返回HTTP 503响应

nos.Client的使用和异常处理的示例代码
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

 try:
    resp = client.XXX(
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
        e.status_code,  # 错误http状态码
        e.error_type,   # NOS服务器定义错误类型
        e.error_code,   # NOS服务器定义错误码
        e.request_id,   # 请求ID，有利于nos开发人员跟踪异常请求的错误原因
        e.message       # 错误描述信息
    )
 except nos.exceptions.ClientException as e:
    print (
        'ClientException: %s\n'
        'message: %s\n'
    ) % (
        e,
        e.message       # 客户端错误信息
    )

对象操作接口
^^^^^^^^^^^^

Delete Object
:::::::::::::

使用举例

::

    resp = client.delete_object(
        bucket="string",
        key="string"
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240"
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。


Delete Multiple Objects
:::::::::::::::::::::::

使用举例

::

    resp = client.delete_objects(
        bucket="string",
        keys=[
            "string1",
            "string2",
            ...
        ],
        quiet=True|False
    )

参数说明

* bucket(string) -- 桶名。
* objects(list) -- 待删除的对象名称列表。
* quiet(boolean) -- 是否开启安静模式（安静模式不显示具体删除信息）。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "response": xml.etree.ElementTree()    # xml.etree.ElementTree类型对象
    }

返回值的`response`的字符形式可能如下：

::

    <?xml version="1.0" encoding="UTF-8"?>
    <DeleteResult>
        <Deleted>
                <Key>1.jpg</Key>
        </Deleted>
        <Error>
                <Key>2.jpg</Key>
                <Code>AccessDenied</Code>
                <Message>Access Denied</Message>
        </Error>
        <Error>
                <Key>3.jpg</Key>
                <Code>NoSuchKey</Code>
                <Message>No Such Key</Message>
        </Error>
    </DeleteResult>

*注意：下列各项通过xml.etree.ElementTree的成员函数获取具体值时，得到的均为字符串；目前标注的类型为原类型名称，需自行转换。*

.. list-table::
    :widths: 10 30 
    :header-rows: 1

    * - Element
      - 描述
    * - DeleteResult
      - | 多重删除的响应容器元素
        | 类型：容器
    * - Deleted
      - | 已被成功删除的容器元素
        | 类型：容器
        | 父节点：DeleteResult
    * - Key
      - | 已删除的对象键值
        | 类型：字符串
        | 父节点：Deleted，Error
    * - VersionId
      - | 已删除的对象版本号
        | 类型：数字
        | 父节点：Deleted，Error
    * - Error
      - | 删除失败的对象版本号
        | 类型：容器
        | 父节点：DeleteResult
    * - Code
      - | 删除失败返回的错误码
        | 类型：字符串
        | 父节点：Error
    * - Message
      - | 删除失败返回的详细错误描述
        | 类型：字符串
        | 父节点：Error

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。
* response(xml.etree.ElementTree) -- 包含返回信息的xml对象。


Get Object
::::::::::

使用举例

::

    resp = client.get_object(
        bucket="string",
        key="string",
        **kwargs
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。
* kwargs -- 其他可选参数，如下。
    * range(string) -- 下载指定的数据块，Range Header参考RFC2616。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "content_length": 1024,
        "content_range": "0-1024/234564",
        "content_type": "application/octet-stream;charset=UTF-8",
        "etag": "3adbbad1791fbae3ec908894c4963870",
        "body": StreamingBody()
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。
* content_length(integer) -- 返回的数据块的字节数。
* content_range(string) -- 返回的数据块的范围。
* content_type(string) -- 返回的数据块的类型。
* etag(string) -- 对象的哈希值，反应对象内容的更改情况。
* body(StreamingBody) -- 对象数据。


Head Object
:::::::::::

使用举例

::

    resp = client.head_object(
        bucket="string",
        key="string"
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "content_length": 1024,
        "content_type": "application/octet-stream;charset=UTF-8",
        "etag": "3adbbad1791fbae3ec908894c4963870",
        "last_modified": "Mon, 23 May 2016 16:07:15 Asia/Shanghai"
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。
* content_length(integer) -- 返回的数据块的字节数。
* content_type(string) -- 返回的数据块的类型。
* etag(string) -- 对象的哈希值，反应对象内容的更改情况。
* last_modified(string) -- 最近一次修改对象的时间。


List Objects
::::::::::::

使用举例

::

    resp = client.list_objects(
        bucket="string",
        **kwargs
    )

参数说明

* bucket(string) -- 桶名。
* kwargs -- 其他可选参数。
    * delimiter(string) -- 分界符，用于做groupby操作。
    * marker(string) -- 字典序的起始标记，只列出该标记之后的部分。
    * limit(integer) -- 限定返回的数量，返回的结果小于或等于该值。取值范围：0-1000，默认：100
    * prefix(string) -- 只返回Key以特定前缀开头的那些对象。可以使用前缀把一个桶里面的对象分成不同的组，类似文件系统的目录一样。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "response": xml.etree.ElementTree()    # xml.etree.ElementTree类型对象
    }

返回值的`response`的字符形式可能如下：

::

    <?xml version="1.0" encoding="UTF-8"?>
    <ListBucketResult xmlns="http://doc.nos.netease.com/2012-03-01">
        <Name>dream</Name>
        <Prefix>user</Prefix>
        <MaxKeys>2</MaxKeys>
        <NextMarker>user/yao</NextMarker>
        <IsTruncated>true</IsTruncated>
        <Contents>
                <Key>user/lin</Key>
                <LastModified>2012-01-01T12:00:00.000Z</LastModified>
                <Etag>258ef3fdfa96f00ad9f27c383fc9acce</ Etag>
                <Size>143663</Size>
                <StorageClass>Standard</StorageClass>
        </Contents>
        <Contents>
                <Key>user/yao</Key>
                <LastModified>2012-01-01T12:00:00.000Z</LastModified>
                < Etag>828ef3fdfa96f00ad9f27c383fc9ac7f</ Etag>
                <Size>423983</Size>
                <StorageClass>Standard</StorageClass>
        </Contents>
    </ListBucketResult>

*注意：下列各项通过xml.etree.ElementTree的成员函数获取具体值时，得到的均为字符串；目前标注的类型为原类型名称，需自行转换。*

.. list-table::
    :widths: 10 35
    :header-rows: 1

    * - 元素
      - 描述
    * - Contents
      - | 对象元数据，代表一个对象描述
        | 类型：容器
        | 父节点：ListBucketObjects
        | 子节点：Key，LastModified，Size，Etag
    * - CommonPrefixes
      - | 只有当指定了delimiter分界符时，才会有这个响应
        | 类型：字符串
        | 父节点：ListBucketObjects
    * - delimiter
      - | 分界符
        | 类型：字符串
        | 父节点：ListBucketObjects
    * - DisplayName
      - | 对象的拥有者
        | 类型：字符串
        | 父节点：ListBucketObjects.Contents.Owner
    * - Etag 
      - | 对象的哈希描述
        | 类型：字符串
        | 父节点：ListBucketObjects.Contents
    * - ID
      - | 对象拥有者的ID
        | 类型：字符串
        | 父节点：ListBucketObjects.Contents.Owner
    * - IsTruncated
      - | 是否截断，如果因为设置了limit导致不是所有的数据集都返回，则该值设置为true
        | 类型：布尔值
        | 父节点：ListBucketObjects
    * - Key
      - | 对象的名称
        | 类型：字符串
        | 父节点：ListBucketObjects.Contents
    * - LastModified
      - | 对象最后修改日期和时间
        | 类型：日期 格式：yyyy-MM-dd"T"HH:mm:ss.SSSZ
        | 父节点：ListBucketObjects.Contents
    * - Marker
      - | 列表的起始位置，等于请求参数设置的Marker值
        | 类型：字符串
        | 父节点：ListBucketObjects
    * - NextMark
      - | 下一次分页的起点
        | 类型：字符串
        | 父节点：ListBucketObjects
    * - MaxKeys
      - | 请求的对象个数限制
        | 类型：数字
        | 父节点：ListBucketObjects
    * - Name
      - | 请求的桶名称
        | 类型：字符串
        | 父节点：ListBucketObjects
    * - Owner
      - | 桶拥有者
        | 类型：容器
        | 父节点：ListBucketObjects.contents | CommonPrefixes
        | 子节点：DisplayName|ID
    * - Prefix
      - | 请求的对象的Key的前缀
        | 类型：字符串
        | 父节点：ListBucketObjects
    * - Size
      - | 对象的大小字节数
        | 类型：数字
        | 父节点：ListBucketObjects.contents
    * - StorageClasss
      - | 存储级别
        | 类型：字符串
        | 父节点：ListBucketObjects.contents

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。
* response(xml.etree.ElementTree) -- 包含返回信息的xml对象。


Put Object
::::::::::

使用举例

::

    resp = client.put_object(
        bucket="string",
        key="string",
        body=serializable_object,
        **kwargs
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。
* body(serializable_object) -- 对象内容，可以是文件句柄、字符串、字典等任何可序列化的对象。
* kwargs -- 其他可选参数。
    * meta_data(dict) -- 用户自定义的元数据，通过键值对的形式上报，键名和值均为字符串，且键名需以\`x-nos-meta-\`开头。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "etag": "fbacf535f27731c9771645a39863328"
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的id号。
* etag(string) -- 对象的哈希值，反应对象内容的更改情况。


Put Object - Copy
:::::::::::::::::

使用举例

::

    resp = client.copy_object(
        src_bucket="string",
        src_key="string",
        dest_bucket="string",
        dest_key="string"
    )

参数说明

* src_bucket(string) -- 来源对象的桶名。
* src_key(string) -- 来源对象的对象名。
* dest_bucket(string) -- 目标对象的桶名。
* dest_key(string) -- 目标对象的对象名。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240"
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。


Move Object
:::::::::::

使用举例

::

    resp = client.move_object(
        src_bucket="string",
        src_key="string",
        dest_bucket="string",
        dest_key="string"
    )

参数说明

* src_bucket(string) -- 来源对象的桶名。
* src_key(string) -- 来源对象的对象名。
* dest_bucket(string) -- 目标对象的桶名。
* dest_key(string) -- 目标对象的对象名。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240"
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。


Initiate Multipart Upload
:::::::::::::::::::::::::

使用举例

::

    resp = client.create_multipart_upload(
        bucket="string",
        key="string",
        **kwargs
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。
* kwargs -- 其他可选参数。
    * meta_data(dict) -- 用户自定义的元数据，通过键值对的形式上报，键名和值均为字符串，且键名需以\`x-nos-meta-\`开头。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "response": xml.etree.ElementTree()    # xml.etree.ElementTree类型对象
    }

返回值的`response`的字符形式可能如下：

::

    <?xml version="1.0" encoding="UTF-8"?>
    <InitiateMultipartUploadResult>
        <Bucket>filestation</Bucket>
        <Key>movie.avi</Key>
        <UploadId>VXBsb2FkIElEIGZvciA2aWWpbmcncyBteS1tb3S5tMnRzIHVwbG9hZA</UploadId>
    </InitiateMultipartUploadResult>

*注意：下列各项通过xml.etree.ElementTree的成员函数获取具体值时，得到的均为字符串；目前标注的类型为原类型名称，需自行转换。*

.. list-table::
    :widths: 10 30
    :header-rows: 1

    * - 元素
      - 描述
    * - InitiateMultipartUploadResult
      - | 响应容器元素
        | 类型：容器
        | 子节点：Key，Bucket
    * - Key	
      - | 对象的Key
        | 类型：字符串
        | 父节点：InitiateMultipartUploadResult
    * - Bucket
      - | 对象的桶
        | 类型：字符串
        | 父节点：InitiateMultipartUploadResult
    * - UploadId
      - | 分块上传的ID，用这个ID来作为各块属于这个文件的标识
        | 类型：字符串
        | 父节点：InitiateMultipartUploadResult

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的id号。
* response(xml.etree.ElementTree) -- 包含返回信息的xml对象。


Upload Part
:::::::::::

使用举例

::

    resp = client.upload_part(
        bucket="string",
        key="string",
        part_num=2,
        upload_id="string",
        body=serializable_object
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。
* part_num(integer) -- 数据分块编码号（1-10000）。
* upload_id(string) -- 数据上传标识号。
* body(serializable_object) -- 对象内容，可以是文件句柄、字符串、字典等任何可序列化的对象。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "etag": "fbacf535f27731c9771645a39863328"
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的id号。
* etag(string) -- 对象的哈希值，反应对象内容的更改情况。


Complete Multipart Upload
:::::::::::::::::::::::::

在将所有数据Part都上传完成后，必须调用Complete Multipart Upload API来完成整个文件的Multipart Upload。在执行该操作时，用户必须提供所有有效的数据Part的列表（包括part号码和ETAG）；NOS收到用户提交的Part列表后，会逐一验证每个数据Part的有效性。当所有的数据Part验证通过后，NOS将把这些数据part组合成一个完整的Object。
使用x-nos-Object-md5扩展头发送对象的MD5值，用作去重库的建立（Put Object使用Content-MD5建立对象去重库）。

使用举例

::

    resp = client.complete_multipart_upload(
        bucket="string",
        key="string",
        upload_id="string",
        info=[
            {
                "part_num": 1,
                "etag": "string"
            },
            {
                "part_num": 2,
                "etag": "string"
            },
            ...
        ],
        **kwargs
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。
* upload_id(string) -- 数据上传标识号。
* info(list) -- 所有有效的数据Part的列表（包括part号码和etag）
* kwargs -- 其他可选参数，如下。
    * object_md5(string) -- 发送对象的md5值，用于后续去重。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "response": xml.etree.ElementTree()    # xml.etree.ElementTree类型对象
    }

返回值的`response`的字符形式可能如下：

::

    <?xml version="1.0" encoding="UTF-8"?>
    <CompleteMultipartUploadResult xmlns="">
        <Location> filestation.nos.netease.com/movie.avi</Location>
        <Bucket>filestation </Bucket>
        <Key>movie.avi </Key>
        <ETag>"3858f62230ac3c915f300c664312c11f-9"</ETag>
    </CompleteMultipartUploadResult>

*注意：下列各项通过xml.etree.ElementTree的成员函数获取具体值时，得到的均为字符串；目前标注的类型为原类型名称，需自行转换。*

.. list-table::
    :widths: 10 30
    :header-rows: 1

    * - 元素
      - 描述
    * - Bucket
      - | 新创建对象所在的桶
        | 类型：字符串
        | 父节点：CompleteMultipartUploadResult
    * - CompleteMultipartUploadResult
      - | 响应容器元素
        | 类型：容器
        | 子节点：Location，Bucket，Key，ETag
    * - ETag
      - | 新创建的对象的Entity Tag
        | 类型：字符串
        | 父节点：CompleteMultipartUploadResult
    * - Key
      - | 新创建对象的Key
        | 类型：字符串
        | 父节点：CompleteMultipartUploadResult
    * - Location
      - | 新创建的这个对象的资源定位URL
        | 类型：字符串
        | 父节点：CompleteMultipartUploadResult

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。
* response(xml.etree.ElementTree) -- 包含返回信息的xml对象。


Abort Multipart Upload
::::::::::::::::::::::

使用举例

::

    resp = client.abort_multipart_upload(
        bucket="string",
        key="string",
        upload_id="string"
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。
* upload_id(string) -- 数据上传标识号。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240"
    }

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。


List Parts
::::::::::

使用举例

::

    resp = client.list_parts(
        bucket="string",
        key="string",
        upload_id="string",
        **kwargs
    )

参数说明

* bucket(string) -- 桶名。
* key(string) -- 对象名。
* upload_id(string) -- 数据上传标识号。
* kwargs -- 其他可选参数，如下。
    * limit(integer) -- 限制响应中返回的记录个数。取值范围：0-1000，默认1000。
    * part_number_marker(string) -- 分块号的界限，只有更大的分块号会被列出来。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "response": xml.etree.ElementTree()    # xml.etree.ElementTree类型对象
    }

返回值的`response`的字符形式可能如下：

::

    <?xml version="1.0" encoding="UTF-8"?>
    <ListPartsResult xmlns=" ">
        <Bucket>example-Bucket</Bucket>
        <Key>example-Object</Key>
        <UploadId>23r54i252358235332523f23 </UploadId>
        <Owner>
                <ID>75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a</ID>
                <DisplayName>someName</DisplayName>
        </Owner>
        <StorageClass>STANDARD</StorageClass>
        <PartNumberMarker>1</PartNumberMarker>
        <NextPartNumberMarker>3</NextPartNumberMarker>
        <MaxParts>2</MaxParts>
        <IsTruncated>true</IsTruncated>
        <Part>
                <PartNumber>2</PartNumber>
                <LastModified>2010-11-10T20:48:34.000Z</LastModified>
                <ETag>"7778aef83f66abc1fa1e8477f296d394"</ETag>
                <Size>10485760</Size>
        </Part>
        <Part>
                <PartNumber>3</PartNumber>
                <LastModified>2010-11-10T20:48:33.000Z</LastModified>
                <ETag>"aaaa18db4cc2f85cedef654fccc4a4x8"</ETag>
                <Size>10485760</Size>
        </Part>
    </ListPartsResult>

*注意：下列各项通过xml.etree.ElementTree的成员函数获取具体值时，得到的均为字符串；目前标注的类型为原类型名称，需自行转换。*

.. list-table::
    :widths: 10 30
    :header-rows: 1

    * - 元素
      - 描述
    * - ListPartsResult
      - | 列出已上传块信息
        | 类型：容器
        | 子节点：Bucket、Key、UploadId、Owner、StorageClass、PartNumberMarker、NextPartNumberMarker、MaxParts, IsTruncated、Part
    * - Bucket
      - | 桶的名称
        | 类型: String
        | 父节点: ListPartsResult
    * - Key
      - | 对象的Key
        | 类型: String
        | 父节点: ListPartsResult
    * - UploadId
      - | 分块上传操作的ID
        | 类型: String
        | 父节点: ListPartsResult
    * - ID
      - | 对象拥有者的ID
        | 类型: String
        | 父节点: Owner
    * - DisplayName
      - | 对象的拥有者.
        | 类型: String
        | 父节点: Owner
    * - Owner
      - | 桶拥有者的信息
        | 子节点：ID, DisplayName
        | 类型: 容器
        | 父节点: ListPartsResult
    * - StorageClass
      - | 存储级别.
        | 类型: String
        | 父节点: ListPartsResult
    * - PartNumberMarker
      - | 上次List操作后的Part number
        | 类型: Integer
        | 父节点: ListPartsResult
    * - NextPartNumberMarker
      - | 作为后续List操作的part-number-marker
        | 类型: Integer
        | 父节点: ListPartsResult
    * - MaxParts
      - | 响应允许返回的的最大part数目
        | 类型: Integer
        | 父节点: ListPartsResult
    * - IsTruncated
      - | 是否截断，如果因为设置了limit导致不是所有的数据集都返回了，则该值设置为true
        | 类型: Boolean
        | 父节点: ListPartsResult
    * - Part
      - | 列出相关part信息
        | 子节点:PartNumber, LastModified, ETag, Size
        | 类型: String
        | 父节点: ListPartsResult
    * - PartNumber
      - | 识别特定part的一串数字
        | 类型: Integer
        | 父节点: Part
    * - LastModified
      - | 该part上传的时间
        | 类型: Date
        | 父节点: Part
    * - ETag
      - | 当该part被上传时返回
        | 类型: String
        | 父节点: Part
    * - Size
      - | 已上传的 part数据的大小.
        | 类型: Integer
        | 父节点: Part

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。
* response(xml.etree.ElementTree) -- 包含返回信息的xml对象。


List Multipart Uploads
::::::::::::::::::::::

使用举例：

::

    resp = client.list_multipart_uploads(
        bucket="string",
        **kwargs
    )

参数说明

* bucket(string) -- 桶名。
* kwargs -- 其他可选参数，如下。
    * limit(integer) -- 限制响应中返回的记录个数。取值范围：0-1000，默认1000。
    * key_marker(string) -- 指定某一uploads key，只有大于该key-marker的才会被列出。

返回值举例

::

    {
        "x_nos_request_id": "17b21e42ac11000001390ab891440240",
        "response": xml.etree.ElementTree()    # xml.etree.ElementTree类型对象
    }

返回值的`response`的字符形式可能如下：

::

    <?xml version="1.0" encoding="UTF-8"?>
    <ListMultipartUploadsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
        <Bucket>Bucket</Bucket>
        <NextKeyMarker>my-movie.m2ts</NextKeyMarker>
        <Upload>
            <Key>my-divisor</Key>
            <UploadId>XMgbGlrZSBlbHZpbmcncyBub3QgaGF2aW5nIG11Y2ggbHVjaw</UploadId>
            <Owner>
                <ID>75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a</ID>
                <DisplayName>OwnerDisplayName</DisplayName>
            </Owner>
            <StorageClass>STANDARD</StorageClass>
        </Upload>
        <Upload>
            <Key>my-movie.m2ts</Key>
            <UploadId>VXBsb2FkIElEIGZvciBlbHZpbcyBteS1tb3ZpZS5tMnRzIHVwbG9hZA</UploadId>
            <Owner>
                <ID>b1d16700c70b0b05597d7acd6a3f92be</ID>
                <DisplayName>OwnerDisplayName</DisplayName>
            </Owner>
            <StorageClass>STANDARD</StorageClass>
        </Upload>
    </ListMultipartUploadsResult>

*注意：下列各项通过xml.etree.ElementTree的成员函数获取具体值时，得到的均为字符串；目前标注的类型为原类型名称，需自行转换。*

.. list-table::
    :widths: 10 30
    :header-rows: 1

    * - 元素
      - 描述
    * - ListMultipartUploadsResult
      - | 响应容器元素
        | 类型：容器
        | 子节点：Bucket，KeyMarker，Upload，NextKeyMarker, owner
    * - Bucket
      - | 对象的桶
        | 类型：字符串
        | 父节点：ListMultipartUploadsResult
    * - NextKeyMarker
      - | 作为后续查询的key-marker
        | 类型：String
        | 父节点：ListMultipartUploadsResult
    * - IsTruncated
      - | 是否截断，如果因为设置了limit导致不是所有的数据集都返回了，则该值设置为true
        | 类型:Boolean
        | 父节点: ListMultipartUploadsResult
    * - Upload
      - | 类型：容器
        | 子节点：Key，UploadId
        | 父节点：ListMultipartUploadsResult
    * - Key
      - | 对象的Key
        | 类型：字符串
        | 父节点：Upload
    * - UploadId
      - | 分块上传操作的ID
        | 类型String
        | 父节点：Upload
    * - ID
      - | 对象拥有者的ID
        | 类型: String
        | 父节点: Owner
    * - DisplayName
      - | 对象的拥有者
        | 类型: String
        | 父节点: Owner
    * - Owner
      - | 桶拥有者的信息
        | 类型：容器
        | 子节点：DisplayName|ID
        | 父节点：Upload
    * - StorageClass
      - | 存储级别
        | 类型: String
        | 父节点: Upload
    * - Initiated
      - | 该分块上传操作被初始化的时间
        | 类型:Date
        | 父节点: Upload
    * - ListMultipartUploadsResult.Prefix
      - | 当请求中包含了prefix参数时，响应中会填充这一prefix
        | 类型:String
        | 父节点: ListMultipartUploadsResult

返回值说明
返回值为字典类型

* x_nos_request_id(string) -- 唯一定位一个请求的ID号。
* response(xml.etree.ElementTree) -- 包含返回信息的xml对象。
