import collections
import fnmatch
import re

def dig(data, pointer, separator=':'):
    """Returns all relevant value -> pattern from data.
    """
    def decompose_pointer(key):
        yield key, None
        value, a, b, c = '', '', '', ''
        while separator in key:
            key, b, c = key.rpartition(separator)
            value, a = c + a + value, b
            yield key, value

    def explore(data, pointer):
        if isinstance(data, list):
            # loop thru elements
            for element in data:
                for k, v in explore(element, pointer):
                    yield k, v
        if isinstance(data, collections.Mapping):
            for key, value in decompose_pointer(pointer):
                if key in data:
                    for k, v in explore(data[key], value):
                        yield k, v
        else:
            yield data, pointer

    for k, v in explore(data, pointer):
        yield k, v


def glob_match(data, pointer, separator=':'):
    for value, pattern in dig(data, pointer, separator):
        if pattern is None:
            return bool(value)
        if fnmatch.fnmatch(str(value), pattern):
            return True
    return False


def pcre_match(data, pointer, separator=':'):
    for value, pattern in dig(data, pointer, separator):
        if pattern is None:
            return bool(value)
        if re.match(pattern, str(value)):
            return True
    return False
