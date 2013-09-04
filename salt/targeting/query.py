from salt._compat import string_types
from salt.targeting import matcher
from salt.targeting.parser import parse

__all__ = [
    'Evaluator',
    'ListEvaluator',
    'MatcherEvaluator',
    'NodeGroupEvaluator',
    'Query',
    'compound',
]

class Evaluator(object):
    """Base for evaluator classes"""


class ListEvaluator(Evaluator):
    def __init__(self, parent=None):
        self.parent = parent

    def __call__(self, raw_value):
        if isinstance(raw_value, string_types):
            raw_value = raw_value.split(',')
        parameters = [matcher.GlobMatcher(value) for value in raw_value]

        return matcher.AnyMatcher(*parameters)


class NodeGroupEvaluator(Evaluator):
    def __init__(self, parent):
        self.parent = parent

    def __call__(self, raw_value):
        try:
            query = self.parent.macros[raw_value]
            return self.parent.parse(query)
        except KeyError:
            raise Exception('node group {0} is not defined'.format(raw_value))


class MatcherEvaluator(Evaluator):
    def __init__(self, matcher):
        self.matcher = matcher

    def __call__(self, raw_value):
        return self.matcher(raw_value)


def make_evaluator(obj, targeting=None):
    try:
        if issubclass(obj, matcher.Matcher):
            return MatcherEvaluator(obj)
        if issubclass(obj, Evaluator):
            return obj(targeting)
    except TypeError:
        pass

    raise Exception('Must be matcher.Matcher or a targeting.Evaluator class', obj)


class Query(object):
    def __init__(self, default_matcher=None, macros=None):
        self.registry = {}
        self.evaluators = {}
        self.default_matcher = default_matcher or matcher.GlobMatcher
        self.macros = macros or {}

    def register(self, prefix, obj):
        if prefix in self.registry:
            raise ValueError('Already registered')

        self.evaluators[prefix] = make_evaluator(obj, self)
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
compound.register('N', NodeGroupEvaluator)
