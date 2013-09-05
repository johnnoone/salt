# -*- coding: utf-8 -*-

# Import Salt Testing libs
from salttesting import skipIf, TestCase
from salttesting.helpers import ensure_in_syspath
ensure_in_syspath('../../')

from salt.targeting.matcher import *
from salt.targeting.query import *

class MinionMock(object):
    def __init__(self, **kwargs):
        self.id = None
        self.grains = {}
        self.pillar = {}
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'ipv4' in kwargs:
            self.grains.update({'ipv4': kwargs['ipv4']})

class TestCompound(TestCase):
    def test_glob(self):
        matcher = compound.parse('web*')
        assert MinionMock(id='web*') in matcher
        assert compound.querify(matcher) == 'web*'
        assert isinstance(matcher, GlobMatcher)

    def test_grain(self):
        matcher = compound.parse('G@os:Ubuntu')
        assert MinionMock(grains={"os": "Ubuntu"}) in matcher
        assert compound.querify(matcher) == 'G@os:Ubuntu'
        assert isinstance(matcher, GrainMatcher)

    def test_grain_pcre(self):
        matcher = compound.parse('P@role:(web|back)\w+')
        assert MinionMock(grains={"role": ["weblol"]}) in matcher
        assert compound.querify(matcher) == 'P@role:(web|back)\w+'
        assert isinstance(matcher, GrainPCREMatcher)

    def test_list(self):
        matcher = compound.parse('L@foo,bar,baz*')
        assert MinionMock(id="bazinga") in matcher
        assert isinstance(matcher, AnyMatcher)

    def test_pillar(self):
        matcher = compound.parse('I@foo:bar')
        assert MinionMock(pillar={'foo': ['bar']}) in matcher
        assert compound.querify(matcher) == 'I@foo:bar'
        assert isinstance(matcher, PillarMatcher)

    def test_pcre(self):
        matcher = compound.parse('E@ic-(foo|bar)\w+')
        assert MinionMock(id="ic-foojistoo") in matcher
        assert compound.querify(matcher) == 'E@ic-(foo|bar)\w+'
        assert isinstance(matcher, PCREMatcher)

    def test_subnet_ip(self):
        matcher = compound.parse('S@192.168.1.0/24')
        assert MinionMock(ipv4=["192.168.1.0"]) in matcher
        assert compound.querify(matcher) == 'S@192.168.1.0/24'
        assert isinstance(matcher, SubnetIPMatcher)

    def test_all_simple_compound(self):
        matcher = compound.parse('foo and G@bar:baz')
        assert MinionMock(id="foo", grains={'bar':'baz'}) in matcher
        assert isinstance(matcher, AllMatcher)

    def test_or_simple_compound(self):
        matcher = compound.parse('foo or G@bar:baz')
        assert MinionMock(id="foo", grains={'bar':'foo'}) in matcher
        assert isinstance(matcher, AnyMatcher)

    def test_not_simple_compound(self):
        matcher = compound.parse('not (G@bar:baz or toto)')
        assert MinionMock(id="foo", grains={'bar':'bazinga'}) in matcher
        assert isinstance(matcher, NotMatcher)

    def test_complex_compound(self):
        matcher = compound.parse('not (G@bar:baz and not toto) or not not I@foo:bar:baz')
        assert MinionMock(id="foo", grains={'bar':'foo'}) in matcher

    def test_macros(self):
        prev_macros = compound.macros
        compound.macros = {
            'foo': 'bar'
        }
        matcher = compound.parse('G@bar:baz or not N@foo')
        assert MinionMock(id="foo", grains={'bar':'foo'}) in matcher
        assert isinstance(matcher, AnyMatcher)

if __name__ == '__main__':
    from integration import run_tests
    run_tests([TestCompound], needs_daemon=False)
