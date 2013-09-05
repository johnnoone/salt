# -*- coding: utf-8 -*-

# Import Salt Testing libs
from salttesting import skipIf, TestCase
from salttesting.helpers import ensure_in_syspath
ensure_in_syspath('../../')

from salt.targeting.matcher import *

class MinionMock(object):
    def __init__(self, **kwargs):
        self.id = None
        self.grains = {}
        self.pillar = {}
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestMatcher(TestCase):
    def test_inheritance(self):
        m = GrainMatcher('foo:bar')
        n = -m

        assert isinstance(m, GrainMatcher)
        assert not isinstance(m, NotMatcher)
        assert not isinstance(n, GrainMatcher)
        assert isinstance(n, NotMatcher)

        assert issubclass(GrainMatcher, Matcher)
        assert issubclass(NotMatcher, Matcher)
        assert not issubclass(GrainMatcher, NotMatcher)
        assert not issubclass(NotMatcher, GrainMatcher)

    def test_grain_matcher(self):
        matcher = GrainMatcher('os:Ubuntu')
        assert "GrainMatcher('os:Ubuntu')" == str(matcher)
        assert matcher == eval(str(matcher))

        minion = MinionMock(grains={'os': 'Ubuntu'})
        assert minion in matcher
        assert minion not in -matcher

    def test_grain_pillar(self):
        matcher = PillarMatcher('user:admin')
        assert "PillarMatcher('user:admin')" == str(matcher)
        assert matcher == eval(str(matcher))

        minion = MinionMock(pillar={'user': 'root'})
        assert minion not in matcher
        assert minion in -matcher

    def test_compound_matcher(self):
        g = GrainMatcher('os:Ubuntu')
        h = PillarMatcher('user:adm:toto')
        i = GlobMatcher('127.0.**')
        j = PCREMatcher('.*admin')

        k = g | i & -h | j

        minion = MinionMock(id="127.0.-testadmin", grains={'os': 'Ubuntu'})

        assert minion in g
        assert minion not in h
        assert minion in -h
        assert minion in i
        assert minion in j
        assert minion in k

        # TODO
        # __str__ must represent a compound query
        # print k

        # __repr__ must return an evaluable python string
        evaluated = eval(str(k))
        assert isinstance(evaluated, AnyMatcher)

    def test_exsel(self):
        matcher = ExselMatcher('foo.bar')
        assert "ExselMatcher('foo.bar')" == str(matcher)
        assert matcher == eval(str(matcher))

        minion = MinionMock(functions={'foo.bar': lambda: True})
        assert minion in matcher
        assert minion not in -matcher

    def test_local_store(self):
        matcher = LocalStoreMatcher('foo:bar')
        assert "LocalStoreMatcher('foo:bar')" == str(matcher)
        assert matcher == eval(str(matcher))

        minion = MinionMock(functions={'data.load': lambda: {"foo": "bar"}})
        assert minion in matcher
        assert minion not in -matcher

    def test_yahoo_range(self):
        server = {'%foo': ['bar.example.com']}
        matcher = YahooRangeMatcher('%foo', server)
        assert "YahooRangeMatcher('%foo')" == str(matcher)
        assert matcher == eval(str(matcher))

        minion = MinionMock(grains={"fqdn": "bar.example.com"})
        assert minion in matcher
        assert minion not in -matcher

if __name__ == '__main__':
    from integration import run_tests
    run_tests([TestMatcher], needs_daemon=False)
