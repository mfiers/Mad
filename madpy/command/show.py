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
    parser.add_argument('file', nargs='+', 
                        help='Files to show the metadata from')

def run(args):
    """
    add a key value pair to parse_argument file's metadata
    """
    
    metadata = {}
    files = []

    remove_keys = []

    for f   in args.file:

        fmd = Metadata(f, mode=args.madmode)
        print fmd.filename
        for k in fmd.keys():
            print '  %20s : %s' % (k, fmd[k])

        print

