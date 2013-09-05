# -*- coding: utf-8 -*-

# Import Salt Testing libs
from salttesting import skipIf, TestCase
from salttesting.helpers import ensure_in_syspath
ensure_in_syspath('../../')

from salt.minion import Matcher

class TestMinionMatcher(TestCase):
    def test_glob_match(self):
        opts, functions = {'id': 'web1'}, {}
        matcher = Matcher(opts, functions)
        assert matcher.glob_match('web*')
        assert matcher.glob_match('web1')
        assert not matcher.glob_match('web2')
        assert not matcher.glob_match('foo*')

    def test_pcre_match(self):
        opts, functions = {'id': 'web1'}, {}
        matcher = Matcher(opts, functions)
        assert matcher.pcre_match('web\d+')
        assert matcher.pcre_match('web1')
        assert not matcher.pcre_match('web')

    def test_list_match(self):
        opts, functions = {'id': 'web1'}, {}
        matcher = Matcher(opts, functions)
        assert matcher.list_match(['web1', 'web2'])
        assert matcher.list_match('web1,web2')
        assert matcher.list_match('web*')
        assert not matcher.pcre_match(['web2', 'web3'])
        assert not matcher.pcre_match('web2,web3')
        assert not matcher.list_match('*web')

    def test_grain_match(self):
        opts, functions = {'grains': {'foo': 'bar'}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_match('foo:bar')
        assert matcher.grain_match('foo:ba*')
        assert not matcher.grain_match('foo:baz')

        opts, functions = {'grains': {'foo': [ 'bar' ]}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_match('foo:bar')
        assert matcher.grain_match('foo:ba*')
        assert not matcher.grain_match('foo:baz')

        opts, functions = {'grains': {'foo': {'bar': True}}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_match('foo:bar')
        assert not matcher.grain_match('foo:ba*')
        assert not matcher.grain_match('foo:baz')

        opts, functions = {'grains': {'foo': {'bar': False}}}, {}
        matcher = Matcher(opts, functions)
        assert not matcher.grain_match('foo:bar')
        assert not matcher.grain_match('foo:ba*')
        assert not matcher.grain_match('foo:baz')

        opts, functions = {'grains': {'foo': [{'bar': True}]}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_match('foo:bar')
        assert not matcher.grain_match('foo:ba*')
        assert not matcher.grain_match('foo:baz')

        opts, functions = {'grains': {'foo': [{'bar': False}]}}, {}
        matcher = Matcher(opts, functions)
        assert not matcher.grain_match('foo:bar')
        assert not matcher.grain_match('foo:ba*')
        assert not matcher.grain_match('foo:baz')

    def test_grain_pcre_match(self):
        opts, functions = {'grains': {'foo': 'bar'}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_pcre_match('foo:bar')
        assert matcher.grain_pcre_match('foo:bar+')
        assert not matcher.grain_pcre_match('foo:baz+')

        opts, functions = {'grains': {'foo': [ 'bar' ]}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_pcre_match('foo:bar')
        assert matcher.grain_pcre_match('foo:bar+')
        assert not matcher.grain_pcre_match('foo:baz+')

        opts, functions = {'grains': {'foo': {'bar': True}}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_pcre_match('foo:bar')
        assert not matcher.grain_pcre_match('foo:bar+')
        assert not matcher.grain_pcre_match('foo:baz+')

        opts, functions = {'grains': {'foo': {'bar': False}}}, {}
        matcher = Matcher(opts, functions)
        assert not matcher.grain_pcre_match('foo:bar')
        assert not matcher.grain_pcre_match('foo:bar+')
        assert not matcher.grain_pcre_match('foo:baz+')

        opts, functions = {'grains': {'foo': [{'bar': True}]}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.grain_pcre_match('foo:bar')
        assert not matcher.grain_pcre_match('foo:bar+')
        assert not matcher.grain_pcre_match('foo:baz+')

        opts, functions = {'grains': {'foo': [{'bar': False}]}}, {}
        matcher = Matcher(opts, functions)
        assert not matcher.grain_pcre_match('foo:bar')
        assert not matcher.grain_pcre_match('foo:bar+')
        assert not matcher.grain_pcre_match('foo:baz+')

    def test_data_match(self):
        # TODO implement this test
        return
        opts, functions = {'grains': {'foo': 'bar'}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.data_match('foo:bar')
        assert matcher.data_match('foo:bar+')
        assert not matcher.data_match('foo:baz+')

    def test_exsel_match(self):
        # TODO implement this test
        return
        opts, functions = {'grains': {'foo': 'bar'}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.exsel_match('foo:bar')
        assert matcher.exsel_match('foo:bar+')
        assert not matcher.exsel_match('foo:baz+')

    def test_pillar_match(self):
        opts, functions = {'pillar': {'foo': 'bar'}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.pillar_match('foo:bar')
        assert matcher.pillar_match('foo:ba*')
        assert not matcher.pillar_match('foo:baz')

        opts, functions = {'pillar': {'foo': [ 'bar' ]}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.pillar_match('foo:bar')
        assert matcher.pillar_match('foo:ba*')
        assert not matcher.pillar_match('foo:baz')

        opts, functions = {'pillar': {'foo': {'bar': True}}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.pillar_match('foo:bar')
        assert not matcher.pillar_match('foo:ba*')
        assert not matcher.pillar_match('foo:baz')

        opts, functions = {'pillar': {'foo': {'bar': False}}}, {}
        matcher = Matcher(opts, functions)
        assert not matcher.pillar_match('foo:bar')
        assert not matcher.pillar_match('foo:ba*')
        assert not matcher.pillar_match('foo:baz')

        opts, functions = {'pillar': {'foo': [{'bar': True}]}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.pillar_match('foo:bar')
        assert not matcher.pillar_match('foo:ba*')
        assert not matcher.pillar_match('foo:baz')

        opts, functions = {'pillar': {'foo': [{'bar': False}]}}, {}
        matcher = Matcher(opts, functions)
        assert not matcher.pillar_match('foo:bar')
        assert not matcher.pillar_match('foo:ba*')
        assert not matcher.pillar_match('foo:baz')

    def test_ipcidr_match(self):
        opts, functions = {'grains': {'ipv4': ['11.12.13.14']}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.ipcidr_match('11.12.13.14')
        assert matcher.ipcidr_match('11.12.0.0/20')
        assert not matcher.ipcidr_match('11.12.0.0/21')

    def test_range_match(self):
        # TODO implement this test
        return
        opts, functions = {'grains': {'ipv4': ['11.12.13.14']}}, {}
        matcher = Matcher(opts, functions)
        assert matcher.range_match('11.12.13.14')
        assert matcher.range_match('11.12.0.0/20')
        assert not matcher.range_match('11.12.0.0/21')

    def test_compound_match(self):
        opts, functions = {'grains': {'foo': 'bar'}, 'id': 'web1' }, {}
        matcher = Matcher(opts, functions)
        assert matcher.compound_match('G@foo:bar')
        assert matcher.compound_match('not G@foo:baz')
        assert matcher.compound_match('not G@foo:baz and G@foo:bar')
        assert matcher.compound_match('G@foo:baz or G@foo:bar')
        assert not matcher.compound_match('not (G@foo:baz or G@foo:bar)')
        assert not matcher.compound_match('(G@foo:baz and G@foo:bar)')

    def test_nodegroup_match(self):
        opts, functions = {'grains': {'foo': 'bar'}, 'id': 'web1' }, {}
        groups = {'foo': 'web* or G@foo:bar', 'bar': 'N@foo and not baz'}
        matcher = Matcher(opts, functions)
        assert matcher.nodegroup_match('bar', groups)


if __name__ == '__main__':
    from integration import run_tests
    run_tests([TestMinionMatcher], needs_daemon=False)
