from .matcher import *
from .parser import *
from .query import *



class LocalMinion(object):
    def __init__(self, opts, functions=None):
        self.opts = opts
        self.functions = functions or {}

    @property
    def id(self):
        return self.opts['id']

    @property
    def grains(self):
        return self.opts['grains']

    @property
    def pillar(self):
        return self.opts['pillar']

