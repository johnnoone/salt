import collections
import fnmatch
import re

__all__ = [
    'glob_match',
    'pcre_match',
    'glob_filter',
    'pcre_filter',
    'pcre_compile',
]


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


def glob_match(data, pointer, separator=None):
    def match(value, expr):
        return fnmatch.fnmatch(value, expr)

    if not separator:
        return match(data, pointer)

    for value, expr in dig(data, pointer, separator):
        if pattern is None:
            return bool(value)
        if match(str(value), expr):
            return True
    return False


def pcre_match(data, pointer, separator=None):
    def match(value, expr):
        return pcre_compile(expr, value).match(value)

    if not separator:
        return match(data, pointer)
    for value, expr in dig(data, pointer, separator):
        if expr is None:
            return bool(value)
        if match(str(value), expr):
            return True
    return False


def glob_filter(values, expr):
    """
    Filters a list of values by glob.
    """
    return fnmatch.filter(values, expr)


def pcre_filter(values, expr):
    """
    Filters a list of values by pcre.
    """
    compiled = re.compile('^(' + expr + ')$')
    return set([value for value in value if compiled.match(value)])


def pcre_compile(expr):
    """Forces exact matching
    """
    return re.compile('^({0})$'.format(expr))
