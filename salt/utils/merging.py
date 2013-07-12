from copy import deepcopy
from itertools import chain

def update(*dictionnaries):
    """
    Returns a new merged dict.

    >>> update({"foo": 1}, {"bar": 2}, {"foo": 3, "baz": 3})
    {'bar': 2, 'foo': 3, 'baz': 3}, []
    """

    keys = chain(*[d.items() for d in dictionnaries])
    return dict(keys), []


def merge(*dictionnaries):
    """
    Returns a new merged dict.

    >>> merge({"foo": 1}, {"bar": 2}, {"foo": 3, "baz": 3})
    {'bar': 2, 'foo': 1, 'baz': 3}, []
    """

    keys = chain(*[d.items() for d in reversed(dictionnaries)])
    return dict(keys), []


def extend(*dictionnaries):
    source, extenderers = dictionnaries[0], dictionnaries[1:]
    errors = []
    response = deepcopy(source)
    for extenderer in extenderers:
        for name, body in extenderer.items():
            if name not in response:
                response[name] = body
            elif isinstance(body, dict) \
                and isinstance(response[name], dict):
                response[name] = merge(response[name], body)
            elif isinstance(body, list) \
                and isinstance(response[name], list):
                response[name].extends(body)
            else:
                errors.append(
                    'Cannot extend ID {0} in "{1}:{2}".'
                    ' Type mixmatch.'.format(
                        name,
                        env,
                        sls)
                    )

    return response, errors
