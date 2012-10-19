"""
define a key having a certain data type
"""

import os

def define_args(parser):
    """
    Set the arguments for 'help'
    """
    pass

def run(args):
    """
    add a key value pair to a file's metadata
    """
    commands = []
    for f in os.listdir(os.path.join(os.path.dirname(__file__))):
        if f[-3:] != '.py': continue        
        if f[0] in ['_', '.']: continue
        commands.append(f[:-3])
    commands.sort()
    print "Mad commands available: %s" % ", ".join(commands)
    print "for more information try:"
    print "mad [COMMAND] --help"
