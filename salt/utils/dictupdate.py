'''
Alex Martelli's soulution for recursive dict update from
http://stackoverflow.com/a/3233356
'''

# Import python libs
import collections


def update(dest, upd):
    for key, val in upd.iteritems():
        if isinstance(val, collections.Mapping):
            ret = update(dest.get(key, {}), val)
            dest[key] = ret
        else:
            dest[key] = upd[key]
    return dest


def merge(*dicts):
    """
    Returns a new merged dict.

    >>> merge({"foo": 1}, {"bar": 2}, {"foo": 3, "baz": 3})
    {'bar': 2, 'foo': 1, 'baz': 3}
    """

    keys = itertools.chain(*[d.items() for d in reversed(dicts)])
    return dict(keys)
