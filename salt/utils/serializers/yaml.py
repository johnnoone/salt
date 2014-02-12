# -*- coding: utf-8 -*-
'''
    salt.utils.serializers.yaml
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from __future__ import absolute_import

import yaml
from yaml.constructor import ConstructorError
from yaml.scanner import ScannerError

from salt.utils.serializers import DeserializationError

__all__ = ['deserialize', 'serialize', 'available']

available = True

# prefer C bindings over python when available
Loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
Dumper = getattr(yaml, 'CSafeDumper', yaml.SafeDumper)

ERROR_MAP = {
    ("found character '\\t' "
     "that cannot start any token"): 'Illegal tab character'
}


def deserialize(stream_or_string, **options):
    options.setdefault('Loader', Loader)
    try:
        return yaml.load(stream_or_string, **options)
    except ScannerError as error:
        err_type = ERROR_MAP.get(error.problem, 'Unknown yaml render error')
        line_num = error.problem_mark.line + 1
        raise DeserializationError(err_type,
                                   line_num,
                                   error.problem_mark.buffer)
    except ConstructorError as error:
        raise DeserializationError(error)
    except Exception as error:
        raise DeserializationError(error)


def serialize(obj, **options):
    options.setdefault('Dumper', Dumper)
    response = yaml.dump(obj, **options)
    if response.endswith('\n...\n'):
        return response[:-5]
    if response.endswith('\n'):
        return response[:-1]
    return response
