from salt._compat import string_types
from salt.targeting import matcher
from salt.targeting.parser import parse
import re

__all__ = [
    'Evaluator',
    'ListEvaluator',
    'MatcherEvaluator',
    'GroupEvaluator',
    'Query',
    'compound',
]

class Evaluator(object):
    """Base for evaluator classes"""


class ListEvaluator(Evaluator):
    def __init__(self, parent=None, prefix=None):
        self.parent = parent
        self.prefix = prefix

    def __call__(self, raw_value):
        if isinstance(raw_value, string_types):
            raw_value = raw_value.split(',')
        parameters = [matcher.GlobMatcher(value) for value in raw_value]

        return matcher.AnyMatcher(*parameters)


class GroupEvaluator(Evaluator):
    def __init__(self, parent, prefix=None):
        self.parent = parent
        self.prefix = prefix

    def __call__(self, raw_value):
        if not raw_value in self.parent.groups:
            raise Exception('Group {0} is not defined'.format(raw_value))

        skip = set([raw_value])
        query = self.parent.groups[raw_value]
        def subfunc(matchobj):
            name = matchobj.groupdict()['name']
            if name in skip:
                raise RuntimeError('Recursivity found {0}'.format(name))
            skip.add(name)

            if not name in self.parent.groups:
                raise Exception('Group {0} is not defined'.format(name))
            return self.parent.groups[name]

        while self.inspect.search(query):
            query = self.inspect.sub(subfunc, query)

        try:
            return self.parent.parse(query)
        except KeyError:
            raise Exception('node group {0} is not defined'.format(raw_value))

    @property
    def inspect(self):
        if getattr(self, '_pattern', None) is None:
            q = r'\b{0}@(?P<name>\w+)\b'.format(re.escape(self.prefix))
            self._pattern = re.compile(q)
        return self._pattern


class MatcherEvaluator(Evaluator):
    def __init__(self, matcher):
        self.matcher = matcher

    def __call__(self, raw_value):
        return self.matcher(raw_value)


def make_evaluator(obj, targeting=None, prefix=None):
    try:
        if issubclass(obj, matcher.Matcher):
            return MatcherEvaluator(obj)
        if issubclass(obj, Evaluator):
            return obj(targeting, prefix)
    except TypeError:
        pass

    raise Exception('Must be matcher.Matcher or a targeting.Evaluator class', obj)


class Query(object):
    def __init__(self, default_matcher=None, groups=None):
        self.registry = {}
        self.evaluators = {}
        self.default_matcher = default_matcher or matcher.GlobMatcher
        self.groups = groups or {}

    def register(self, prefix, obj):
        if prefix in self.registry:
            raise ValueError('Already registered')

        self.evaluators[prefix] = make_evaluator(obj, self, prefix)
        self.registry[prefix] = obj

    def parse(self, query):
        if not isinstance(query, string_types):
            raise ValueError('query must be a string')
        return parse(query, self.parse_matcher)

    def parse_matcher(self, value):
        prefix, sep, raw_value = value.partition('@')
        if prefix and raw_value and prefix in self.evaluators:
            return self.evaluators[prefix](raw_value)
        return self.default_matcher(value)

    def parse_group(self, value):
        try:
            query = self.groups[value]
        except KeyError:
            raise Exception('Group {0} is not defined'.format(repr(value)))
        return self.parse(query)

    def register_groups(self, groups, overlap=False, reset=False):
        assert isinstance(groups, dict)
        if reset:
            self.groups.clear()

        if not overlap:
            overlapping = set(self.groups.keys()) & set(groups.keys())
            if overlapping:
                raise ValueError('Some groups are already registered: ' \
                        '{0}'.format(', '.join(repr(o) for o in overlapping)))
        self.groups.update(groups)

    def querify(self, obj):
        def parenthize(objs):
            for obj in objs:
                if isinstance(obj, (matcher.AnyMatcher, matcher.AllMatcher)):
                    yield '({0})'.format(self.querify(obj))
                else:
                    yield self.querify(obj)

        if isinstance(obj, matcher.NotMatcher):
            return 'not ' + ''.join(parenthize([obj.matcher]))
        if isinstance(obj, matcher.AnyMatcher):
            return ' or '.join(parenthize(obj.matchers))
        if isinstance(obj, matcher.AllMatcher):
            return ' and '.join(parenthize(obj.matchers))
        if isinstance(obj, self.default_matcher):
            return obj.expr
        for prefix, base in self.registry.items():
            if isinstance(obj, base):
                return prefix + '@' + obj.expr
        raise Exception('Not defined for {0}'.format(repr(obj.__class__.__name__)))

compound = Query()
compound.register('G', matcher.GrainMatcher)
compound.register('I', matcher.PillarMatcher)
compound.register('E', matcher.PCREMatcher)
compound.register('P', matcher.GrainPCREMatcher)
compound.register('S', matcher.SubnetIPMatcher)
compound.register('X', matcher.ExselMatcher)
compound.register('D', matcher.LocalStoreMatcher)
compound.register('R', matcher.YahooRangeMatcher)
compound.register('L', ListEvaluator)
compound.register('N', GroupEvaluator)
