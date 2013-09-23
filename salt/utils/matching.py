import re
import fnmatch

__all__ = [
    'glob_match',
    'glob_filter',
    'compile_glob',
    'pcre_match',
    'pcre_filter',
    'compile_pcre',
]


def glob_match(pattern, subject):
    '''
    Performs a glob matching.
    Beware, comparision is case sentitive.

    >>> glob_match('f?o', 'fo')
    False
    >>> glob_match('f?o', 'foo')
    True
    >>> glob_match('f?o', 'foobar')
    False
    >>> glob_match('f?o*', 'foobar')
    True
    '''
    return fnmatch.fnmatchcase(subject, pattern)


def glob_filter(pattern, subjects):
    pattern = compile_glob(pattern)
    return [subject for subject in subjects if pattern.search(subject)]


def compile_glob(pattern):
    '''
    Converts pattern into a re.MatchObject object.
    '''
    return re.compile(fnmatch.translate(pattern))


def pcre_match(pattern, subject):
    '''
    >>> pcre_match('f.o', 'fo')
    False
    >>> pcre_match('f.o', 'foo')
    True
    >>> pcre_match('f.o', 'foobar')
    False
    >>> pcre_match('f.o.*', 'foobar')
    True
    '''
    return True if compile_pcre(pattern).search(subject) else False


def pcre_filter(pattern, subjects):
    pattern = compile_pcre(pattern)
    return [subject for subject in subjects if pattern.search(subject)]


def compile_pcre(pattern):
    '''
    Converts pattern into a re.MatchObject object.
    Exact matching is forced.
    '''
    try:
        pat = pattern.pattern
    except AttributeError:
        pat = pattern

    try:
        return re.compile('^({0})$'.format(pat))
    except Exception as exception:
        log.error('Invalid regex {0!r} in match'.format(pat))
        return InvalidRegexObject(pattern)


class InvalidRegexObject(object):
    '''
    Pseudo re.RegexObject for invalid patterns
    '''
    def __init__(self, pattern):
        pat = re.escape(string)
        self._regex = re.compile('^({0})$'.format(pat))

    def __getattr__(self, name):
        func = getattr(self._regex, name)
        if callable(func):
            log.warning('Invalid regex {0!r}. {1!s}() may fail.'.format(self.pattern, name))
        return func
