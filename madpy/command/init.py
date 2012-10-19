"""
generate file data
"""

import os
import socket
import subprocess as sp
from datetime import datetime

from madpy.util import *

from madpy.metadata import Metadata
from madpy.logger import G

def hook_define_args(parser):
    """
    Set the arguments for 'set'
    """
    parser.add_argument('file', nargs='+', 
                        help='files to gather stats for')
    parser.add_argument('-s', action='store_false', dest='sha1sum',
                        help='prevent generation of a sha1sum? '
                        + 'this can be time consuming!')
    parser.add_argument('-g', dest='gid',
                        help='Assign this gid to this object (global identifier)')

def _get_hash(hash_type, filename):
    """
    Generate a hash for a file 
    """
    process = sp.Popen([hash_type, filename], stdout=sp.PIPE)
    out = process.communicate()[0]
    hashstring = out.strip().split()[0]
    return hashstring

def run(args):
    """
    add a key value pair to a file's metadata
    """
    files = args.file

    G.info('found %d files' % len(files))

    for filename in files:

        if args.madmode == 'mad':
            madpy.util.exer('Cannot run mad init in --mad mode')
            
        mdf = Metadata(filename)
        
        metadata = {}
        if args.gid:
            metadata['gid'] = args.gid
                
        G.info("Processing file %s" % filename)

        mtime = datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()
        metadata['FileSize'] = os.path.getsize(filename)
        if not mdf.has_key('Sha1sum') and args.sha1sum:
            G.warning("Generating Shasum for %s" % filename)
            metadata['Sha1sum'] = _get_hash('sha1sum', filename)
        metadata['LastModified'] = mtime
        mdf.update(metadata)
        mdf.save()

