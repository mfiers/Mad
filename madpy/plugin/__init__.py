"""
Manage plugins!
"""

from madpy.conf import conf
from madpy.logger import *

PLUGINS = []


def init():
    #Load the plugins
    for p in conf.plugins:
        #try to import the module corresponding to the "command"
        G.debug("try to load plugin %s" % p)
        try:
            mod = __import__('madpy.plugin.%s' % p,
                             globals(), locals(), [p], -1)
            PLUGINS.append(mod)
        except:
            G.critical("Cannot import plugin.%s" % p)
            raise


def run(command, *args, **kwargs):
    full_com_name = 'hook_%s' % command
    for p in PLUGINS:
        if full_com_name in dir(p):
            G.debug("running plugin command %s.%s" % (
                p.__name__, full_com_name))
            p.__dict__[full_com_name](*args, **kwargs)
