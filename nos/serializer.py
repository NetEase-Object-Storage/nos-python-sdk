# -*- coding:utf8 -*-

try:
    import simplejson as json
except ImportError:
    import json
import uuid
from datetime import date, datetime
from decimal import Decimal

from .exceptions import SerializationError
from .compat import string_types

__all__ = ["JSONSerializer"]


class JSONSerializer(object):
    def default(self, data):
        if isinstance(data, (date, datetime)):
            return data.isoformat()
        elif isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, uuid.UUID):
            return str(data)
        raise TypeError("Unable to serialize %r (type: %s)" % (data, type(data)))

    def dumps(self, data):
        # don't serialize strings
        if isinstance(data, string_types):
            if isinstance(data, unicode):
                return data.encode("utf-8")
            else:
                return data

        # don't serialize file
        if isinstance(data, file):
            return data

        try:
            return json.dumps(data, default=self.default, ensure_ascii=False)
        except (ValueError, TypeError) as e:
            raise SerializationError(data, e)
