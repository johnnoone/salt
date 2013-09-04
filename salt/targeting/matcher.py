from abc import abstractmethod
import collections
from salt.utils.matching import glob_match, pcre_match
from salt.utils import yahoo_range

__all__ = [
    'Matcher',
    'NotMatcher',
    'AllMatcher',
    'AnyMatcher',
    'GrainMatcher',
    'PillarMatcher',
    'GlobMatcher',
    'PCREMatcher',
    'GrainPCREMatcher',
    'SubnetIPMatcher',
    'ExselMatcher',
    'LocalStoreMatcher',
    'YahooRangeMatcher',
]

class DelimeterError(ValueError): pass

def validate_expr(expr, delim=None):
    delim = delim or ':'
    if delim not in expr:
        raise DelimeterError('Expression must have {0} delimiter'.format(repr(delim)))
    return expr, delim

class Matcher(object):
    """The mother of all matchers.
    """

    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def __contains__(self, minion):
        return False

    def __eq__(self, other):
        raise NotImplementedError

    def __and__(self, other):
        return  AllMatcher(other, self)

    def __or__(self, other):
        return  AnyMatcher(other, self)

    def __neg__(self):
        """Negates is results.
        """
        return NotMatcher(self)

    def __str__(self):
        name = self.__class__.__name__
        args = repr(self.expr)
        return name + '(' + args + ')'


class NotMatcher(Matcher):
    """Evil twin of Matcher. Negates his brother.
    """
    def __init__(self, matcher):
        self.matcher = matcher

    def __contains__(self, minion):
        return minion not in self.matcher

    def __eq__(self, other):
        if isinstance(other, NotMatcher):
            return self.matcher == other.matcher
        return False

    def __neg__(self):
        """Gets out from negation.
        """
        return self.matcher

    def __str__(self):
        name = self.__class__.__name__
        args = str(self.matcher)
        return name + '(' + args + ')'

def parenthize(matchers):
    """Helper for parenthizing group matchers
    """
    for matcher in matchers:
        if isinstance(matcher, (AnyMatcher, AllMatcher)):
            yield '({0})'.format(str(matcher))
        else:
            yield str(matcher)


class AllMatcher(Matcher):
    """Minion musts match all of matchers.
    """
    def __init__(self, *matchers):
        out = set()
        for matcher in matchers:
            if isinstance(matcher, AllMatcher):
                out.update(matcher.matchers)
            else:
                out.add(matcher)
        self.matchers = out

    def __contains__(self, minion):
        return all(minion in matcher for matcher in self.matchers)

    def __str__(self):
        name = self.__class__.__name__
        args = ', '.join([str(matcher) for matcher in self.matchers])
        return name + '(' + args + ')'


class AnyMatcher(Matcher):
    """Minion musts match almost one of matchers.
    """
    def __init__(self, *matchers):
        out = set()
        for matcher in matchers:
            if isinstance(matcher, AnyMatcher):
                out.update(matcher.matchers)
            else:
                out.add(matcher)
        self.matchers = out

    def __contains__(self, minion):
        return any(minion in matcher for matcher in self.matchers)

    def __str__(self):
        name = self.__class__.__name__
        args = ', '.join([str(matcher) for matcher in self.matchers])
        return name + '(' + args + ')'


class GrainMatcher(Matcher):
    def __init__(self, expr, delim=None):
        self.expr, self.delim = validate_expr(expr, delim)

    def __contains__(self, minion):
        assert hasattr(minion, 'grains'), "Minion must define a grains property"
        assert isinstance(minion.grains, collections.Mapping), "Minion grains must be a dict"
        return glob_match(minion.grains, self.expr, self.delim)

    def __eq__(self, other):
        if isinstance(other, GrainMatcher):
            return self.expr == other.expr
        return False


class PillarMatcher(Matcher):
    def __init__(self, expr, delim=None):
        self.expr, self.delim = validate_expr(expr, delim)

    def __contains__(self, minion):
        assert hasattr(minion, 'pillars'), "Minion must define a pillars property"
        assert isinstance(minion.pillar, collections.Mapping), "Minion pillars must be a dict"
        return glob_match(minion.pillar, self.expr, self.delim)

    def __eq__(self, other):
        if isinstance(other, PillarMatcher):
            return self.expr == other.expr
        return False


class GlobMatcher(Matcher):
    def __init__(self, expr):
        self.expr = expr

    def __contains__(self, minion):
        assert hasattr(minion, 'id'), "Minion must define an id property"
        return glob_match(minion.id, self.expr, ':')

    def __eq__(self, other):
        if isinstance(other, GlobMatcher):
            return self.expr == other.expr
        return False


class PCREMatcher(Matcher):
    def __init__(self, expr):
        self.expr = expr

    def __contains__(self, minion):
        assert hasattr(minion, 'id'), "Minion must define an id property"
        return pcre_match(minion.id, self.expr, ':')

    def __eq__(self, other):
        if isinstance(other, PCREMatcher):
            return self.expr == other.expr
        return False


class GrainPCREMatcher(Matcher):
    def __init__(self, expr, delim=None):
        self.expr, self.delim = validate_expr(expr, delim)

    def __contains__(self, minion):
        assert hasattr(minion, 'grains'), "Minion must define a grains property"
        assert isinstance(minion.grains, collections.Mapping), "Minion grains must be a dict"
        return pcre_match(minion.grains, self.expr, self.delim)

    def __eq__(self, other):
        if isinstance(other, GrainMatcher):
            return self.expr == other.expr
        return False


class SubnetIPMatcher(Matcher):
    def __init__(self, expr):
        self.expr = expr

    def __contains__(self, minion):
        assert hasattr(minion, 'grains'), "Minion must define a grains property"
        assert isinstance(minion.grains, collections.Mapping), "Minion grains must be a dict"
        ipv4 = minion.grains.get('ipv4', [])
        if not ipv4:
            return False

        if '/' not in self.expr:
            return self.expr in ipv4

        # cidr matching

        import socket,struct
        def to_long(ipaddr):
            return struct.unpack('=L', socket.inet_aton(ipaddr))[0]

        def dotted_netmask(mask):
            bits = 0xffffffff ^ (1 << 32 - int(mask)) - 1
            return socket.inet_ntoa(struct.pack('>I', bits))

        netaddr, bits = self.expr.split('/', 1)
        netmask = to_long(dotted_netmask(bits))
        network = to_long(netaddr) & netmask
        return any(to_long(ip) & netmask == network & netmask for ip in ipv4)


class ExselMatcher(Matcher):
    def __init__(self, expr):
        self.expr = expr

    def __contains__(self, minion):
        assert hasattr(minion, 'functions'), "Minion must define a functions property"
        assert isinstance(minion.functions, collections.Mapping), "Minion functions must be a dict"
        if self.expr not in minion.functions:
            return False
        return bool(minion.functions[self.expr]())

    def __eq__(self, other):
        if isinstance(other, ExselMatcher):
            return self.expr == other.expr
        return False


class LocalStoreMatcher(Matcher):
    def __init__(self, expr, delim=None):
        self.expr, self.delim = validate_expr(expr, delim)

    def __contains__(self, minion):
        assert hasattr(minion, 'functions'), "Minion must define a functions property"
        assert isinstance(minion.functions, collections.Mapping), "Minion functions must be a dict"
        assert 'data.load' in minion.functions, "data.load must be defined"
        return glob_match(minion.functions['data.load'](), self.expr, separator=':')

    def __eq__(self, other):
        if isinstance(other, LocalStoreMatcher):
            return self.expr == other.expr
        return False


class YahooRangeMatcher(Matcher):
    """
    see https://github.com/ytoolshed/range
    https://github.com/grierj/range/wiki/Introduction-to-Range-with-YAML-files
    """

    def __init__(self, expr, provider=None):
        self.expr = expr
        self.provider = provider

    def get_provider(self, minion):
        if not self.provider:
            host = minion.opts.get('range_server', None)
            if host is None:
                raise Exception('Range server is not configured')
            self.provider = yahoo_range.Server(host)
        return self.provider

    def __contains__(self, minion):
        assert hasattr(minion, 'grains'), "Minion must define a grains property"
        assert isinstance(minion.grains, collections.Mapping), "Minion grains must be a dict"
        fqdn = minion.grains.get('fqdn', None)
        server = self.get_provider(minion)
        return fqdn in server.get(self.expr)

    def __eq__(self, other):
        if isinstance(other, YahooRangeMatcher):
            return self.expr == other.expr
        return False
