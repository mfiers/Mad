"""
Set a key/value
"""

import sys

from madpy.conf import conf
from madpy.logger import G, exerr
from madpy.metadata import Metadata


def hook_define_args(parser):
    """
    Set the arguments for 'set'
    """
    parser.add_argument('setargs', nargs='+', metavar="<KEY=VALUE> <FILE>",
                        help='variables to set and files to set them to. ' +
                        '- variables take the form of KEY=VALUE (no spaces),' +
                        ' the remaining arguments are files. Remove keys by ' +
                        'specifying "KEY="')
    parser.add_argument('-f', dest='force', help='set key/value pair, even ' +
                        'if the key is unknown', action='store_true')


def run(args):
    """
    add a key value pair to parse_argument file's metadata
    """

    files = []
    remove_keys = []
    kvs = []

    for parse_argument in args.setargs:

        #is this parse_argument file or parse_argument key=value pair?
        if '=' in parse_argument:
            #it seems this is a key=value pair
            key, value = parse_argument.split('=', 1)
            if (not args.force) and (not key in conf.datatypes.keys()):
                G.critical("Invalid key %s" % key)
                print "Available keys are:"
                print ", ".join(conf.datatypes.keys())
                sys.exit(-1)
            if not value:
                remove_keys.append(key)
                G.info("Preparing %s for removal" % key)
            else:
                kvs.append((key, value))
                G.debug("adding key, value pair %s, %s" % (key, value))
        else:
            fmd = Metadata(parse_argument)
            files.append(fmd)

    G.info('found %d key value pairs' % len(kvs))
    G.info('found %d files' % len(files))

    if len(files) == 0:
        exerr("Must specify at least one file")
    for madfile in files:
        G.info("Processing file %s" % madfile)
        for k, v in kvs:
            G.debug("applying %s, %s" % (k, v))
            madfile.apply_kv(k, v)
        madfile.remove_keys(remove_keys)
        madfile.save()
