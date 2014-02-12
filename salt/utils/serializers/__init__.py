# -*- coding: utf-8 -*-
'''
    salt.utils.serializers
    ~~~~~~~~~~~~~~~~~~~~~~
'''

from __future__ import absolute_import
from salt.exceptions import SaltRenderError


class DeserializationError(SaltRenderError, RuntimeError):
    """raised when stream of string failed to be deserialized"""
    pass
