# -*- coding: utf-8 -*-
'''
    salt.utils.serializers.msgpack
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

from __future__ import absolute_import
from copy import copy
import logging

from salt.log import setup_console_logger

log = logging.getLogger(__name__)


try:
    # Attempt to import msgpack
    import msgpack
    # There is a serialization issue on ARM and potentially other platforms
    # for some msgpack bindings, check for it
    if msgpack.loads(msgpack.dumps([1, 2, 3]), use_list=True) is None:
        raise ImportError
    available = True
except ImportError:
    # Fall back to msgpack_pure
    try:
        import msgpack_pure as msgpack
    except ImportError:
        # TODO: Come up with a sane way to get a configured logfile
        #       and write to the logfile when this error is hit also
        LOG_FORMAT = '[%(levelname)-8s] %(message)s'
        setup_console_logger(log_format=LOG_FORMAT)
        log.fatal('Unable to import msgpack or msgpack_pure python modules')
        # Don't exit if msgpack is not available, this is to make local mode
        # work without msgpack
        #sys.exit(1)
        available = False


if not available:

    def _fail():
        raise RuntimeError('msgpack is not available')

    def _serialize(obj, **options):
        _fail()

    def _deserialize(obj, **options):
        _fail()

elif msgpack.version >= (0, 2, 0):

    def _serialize(obj, **options):
        if options:
            log.warning('options are currently unusued')
        return msgpack.dumps(obj)

    def _deserialize(obj, **options):
        options.setdefault('use_list', True)
        return msgpack.loads(obj, **options)

else:  # msgpack.version < 0.2.0

    def dummy_encoder(obj):
        '''
        Since OrderedDict is identified as a dictionary, we can't make use of
        msgpack custom types, we will need to convert by hand.

        This means iterating through all elements of dictionaries, lists and
        tuples.
        '''
        if isinstance(obj, dict):
            data = [(key, dummy_encoder(value)) for key, value in obj.items()]
            return dict(data)
        elif isinstance(obj, (list, tuple)):
            return [dummy_encoder(value) for value in obj]
        return copy(obj)

    def dummy_decoder(obj):
        return obj

    def _serialize(obj, **options):
        if options:
            log.warning('options are currently unusued')
        obj = dummy_encoder(obj)
        return msgpack.dumps(obj)

    def _deserialize(obj, **options):
        options.setdefault('use_list', True)
        return msgpack.loads(obj)

serialize = _serialize
deserialize = _deserialize
