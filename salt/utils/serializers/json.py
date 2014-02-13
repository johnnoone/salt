# -*- coding: utf-8 -*-
'''
    salt.utils.serializers.json
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from __future__ import absolute_import

try:
    import simplejson as json
except ImportError:
    import json

from salt._compat import string_types
from salt.utils.serializers import DeserializationError

__all__ = ['deserialize', 'serialize', 'available']

available = True


def deserialize(stream_or_string, **options):
    try:
        if not isinstance(stream_or_string, (bytes, string_types)):
            return json.load(stream_or_string, **options)

        if isinstance(stream_or_string, bytes):
            stream_or_string = stream_or_string.decode('utf-8')

        return json.loads(stream_or_string)
    except Exception as e:
        raise DeserializationError(e)


def serialize(obj, **options):
    if 'fp' in options:
        return json.dump(obj, **options)
    else:
        return json.dumps(obj, **options)
