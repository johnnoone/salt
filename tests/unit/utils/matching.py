# -*- coding: utf-8 -*-
'''
    tests.unit.utils.matching
    ~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from salttesting import TestCase, expectedFailure
from salt.utils import matching
from salttesting import skipIf, TestCase
from salttesting.helpers import ensure_in_syspath
ensure_in_syspath('../../')

class MatchingTest(TestCase):
    def test_foo(self):
        self.assertTrue(matching.pcre_match('f.o', 'foo'))
        self.assertFalse(matching.pcre_match('f.o', 'foobar'))
        self.assertTrue(matching.glob_match('f?o', 'foo'))
        self.assertFalse(matching.glob_match('f?o', 'foobar'))

if __name__ == '__main__':
    from integration import run_tests
    run_tests(MatchingTest, needs_daemon=False)
