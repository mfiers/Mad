"""
Set a key/value
"""

import sys

from madpy import mvars
from madpy.conf import conf
from madpy.logger import G, exerr
from madpy.metadata import Metadata

def hook_define_args(parser):
    """
    Set the arguments for 'set'
    """
    parser.add_argument('setargs', nargs='+', metavar="<KEY=VALUE> <FILE>",
                        help='variables to check, or look up in the ontology')
    
def run(args):
    """
    add a key value pair to parse_argument file's metadata
    """
    
    metadata = {}

    for parse_argument in args.setargs:

        #is this parse_argument file or parse_argument key=value pair?
        if '=' in parse_argument:
            #it seems this is a key=value pair
            key, value = parse_argument.split('=', 1)
            if (not key in conf.datatypes.keys()):
                G.critical("Invalid key %s" % key)
                print "Available keys are:"
                print ", ".join(conf.datatypes.keys())
                sys.exit(-1)                                
            else:
                mup = mvars.check(key, value)
                print mup
        else:
            G.critical("Please specifiy a key=value pair")

