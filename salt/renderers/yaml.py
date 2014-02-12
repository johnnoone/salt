# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Import python libs
import logging
import warnings

# Import salt libs
from salt.utils.odict import OrderedDict
from salt.utils.serializers import silas, DeserializationError
from salt.exceptions import SaltRenderError

log = logging.getLogger(__name__)


def render(yaml_data, saltenv='base', sls='', argline='', **kws):
    '''
    Accepts YAML as a string or as a file object and runs it through the YAML
    parser.

    :rtype: A Python data structure
    '''
    with warnings.catch_warnings(record=True) as warn_list:
        data = silas.deserialize(yaml_data)
        if len(warn_list) > 0:
            for item in warn_list:
                log.warn(
                    '{warn} found in salt://{sls} environment={saltenv}'.format(
                        warn=item.message, sls=sls, saltenv=saltenv
                    )
                )
        if not data:
            data = {}
        elif isinstance(__salt__, dict):
            if 'config.get' in __salt__:
                if __salt__['config.get']('yaml_utf8', False):
                    data = _yaml_result_unicode_to_utf8(data)
        elif __opts__.get('yaml_utf8'):
            data = _yaml_result_unicode_to_utf8(data)
        log.debug('Results of YAML rendering: \n{0}'.format(data))
        return data


def _yaml_result_unicode_to_utf8(data):
    ''''
    Replace `unicode` strings by utf-8 `str` in final yaml result

    This is a recursive function
    '''
    if isinstance(data, OrderedDict):
        for key, elt in data.iteritems():
            if isinstance(elt, unicode):
                # Here be dragons
                data[key] = elt.encode('utf-8')
            elif isinstance(elt, OrderedDict):
                data[key] = _yaml_result_unicode_to_utf8(elt)
            elif isinstance(elt, list):
                for i in xrange(len(elt)):
                    elt[i] = _yaml_result_unicode_to_utf8(elt[i])
    elif isinstance(data, list):
        for i in xrange(len(data)):
            data[i] = _yaml_result_unicode_to_utf8(data[i])
    elif isinstance(data, unicode):
        # here also
        data = data.encode('utf-8')
    return data
