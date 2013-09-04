from .matcher import *
from .parser import *
from .query import *



class LocalMinion(object):
    def __init__(self, opts, functions):
        self.opts = opts
        self.functions = functions

    @property
    def id(self):
        return self.opts['id']

    @property
    def grains(self):
        return self.opts['grains']

    @property
    def pillar(self):
        return opts['pillar']

    @property
    def functions(self):
        return self.functions

