# -*- coding: utf-8 -*-
'''
    salt.utils.serializers.yaml
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from __future__ import absolute_import

import yaml

from salt.utils.serializers import DeserializationError

__all__ = ['deserialize', 'serialize', 'available']

available = True

# prefer C bindings over python when available
Loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
Dumper = getattr(yaml, 'CSafeDumper', yaml.SafeDumper)


def deserialize(stream_or_string, **options):
    options.setdefault('Loader', Loader)
    try:
        return yaml.load(stream_or_string, **options)
    except Exception as e:
        raise DeserializationError(e)


def serialize(obj, **options):
    options.setdefault('Dumper', Dumper)
    response = yaml.dump(obj, **options)
    if response.endswith('\n...\n'):
        return response[:-5]
    if response.endswith('\n'):
        return response[:-1]
    return response
