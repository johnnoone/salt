'''
The match module allows for match routines to be run and determine target
specs.
'''

# Import python libs
import logging

# Import salt libs
import salt.targeting

__func_alias__ = {
    'list_': 'list'
}

log = logging.getLogger(__name__)

def compound(tgt):
    '''
    Return True if the minion matches the given compound target

    CLI Example:

    .. code-block:: bash

        salt '*' match.compound 'L@cheese,foo and *'
    '''
    try:
        matcher = salt.targeting.compound.parse(tgt)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def ipcidr(tgt):
    '''
    Return True if the minion matches the given ipcidr target

    CLI Example:

    .. code-block:: bash

        salt '*' match.ipcidr '192.168.44.0/24'
    '''
    try:
        matcher = salt.targeting.SubnetIPMatcher(tgt)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def pillar(tgt, delim=':'):
    '''
    Return True if the minion matches the given pillar target. The
    ``delim`` argument can be used to specify a different delimiter.

    CLI Example:

    .. code-block:: bash

        salt '*' match.pillar 'cheese:foo'
        salt '*' match.pillar 'clone_url|https://github.com/saltstack/salt.git' delim='|'

    .. versionchanged:: 0.16.4
        ``delim`` argument added
    '''
    try:
        matcher = salt.targeting.PillarMatcher(tgt, delim=delim)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def data(tgt):
    '''
    Return True if the minion matches the given data target

    CLI Example:

    .. code-block:: bash

        salt '*' match.data 'spam:eggs'
    '''
    try:
        matcher = salt.targeting.LocalStoreMatcher(tgt)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def grain_pcre(tgt, delim=':'):
    '''
    Return True if the minion matches the given grain_pcre target. The
    ``delim`` argument can be used to specify a different delimiter.

    CLI Example:

    .. code-block:: bash

        salt '*' match.grain_pcre 'os:Fedo.*'
        salt '*' match.grain_pcre 'ipv6|2001:.*' delim='|'

    .. versionchanged:: 0.16.4
        ``delim`` argument added
    '''
    try:
        matcher = salt.targeting.GrainPCREMatcher(tgt, delim=delim)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def grain(tgt, delim=':'):
    '''
    Return True if the minion matches the given grain target. The ``delim``
    argument can be used to specify a different delimiter.

    CLI Example:

    .. code-block:: bash

        salt '*' match.grain 'os:Ubuntu'
        salt '*' match.grain_pcre 'ipv6|2001:db8::ff00:42:8329' delim='|'

    .. versionchanged:: 0.16.4
        ``delim`` argument added
    '''
    try:
        matcher = salt.targeting.GrainMatcher(tgt, delim=delim)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def list_(tgt):
    '''
    Return True if the minion matches the given list target

    CLI Example:

    .. code-block:: bash

        salt '*' match.list 'server1,server2'
    '''
    try:
        matcher = salt.targeting.ListEvaluator()(tgt)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def pcre(tgt):
    '''
    Return True if the minion matches the given pcre target

    CLI Example:

    .. code-block:: bash

        salt '*' match.pcre '.*'
    '''
    try:
        matcher = salt.targeting.PCREMatcher(tgt)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False


def glob(tgt):
    '''
    Return True if the minion matches the given glob target

    CLI Example:

    .. code-block:: bash

        salt '*' match.glob '*'
    '''
    try:
        matcher = salt.targeting.GlobMatcher(tgt)
        minion = salt.targeting.LocalMinion(__opts__, __salt__)
        return minion in matcher
    except Exception as exc:
        log.exception(exc)
        return False
