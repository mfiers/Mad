"""
Few random utilities
"""

import os
import sys
from madpy.conf import conf

def exer(message):
    """ Exit with an error message and rc -1 """

    sys.stderr.write('MAD ERROR: ')
    if type(message) == type([]):
        sys.stderr.write(" ".join(map(str, message)))
    else:
        sys.stderr.write(str(message))

    sys.stderr.write("\n")
    sys.exit(-1)

def get_conf_dir():
    outbase = os.path.abspath(os.path.expanduser(
        conf.general.config_dir))
    if not os.path.exists(outbase):
        os.mkdir(outbase)
    return outbase
