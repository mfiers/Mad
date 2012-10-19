"""
module for assigning gids based on a local counter
"""

import os
from madpy.conf import conf


def hook_define_args(parser):
    pass


def hook_post_metadata_load(mdf):
    if not 'gid' in mdf.metadata:
        mdf.metadata['gid'] = get_gid()


def toBaseN(num, b, ln=5, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    rv = ((num == 0) and numerals[0]) or \
        (toBaseN(num // b, b, ln, numerals).lstrip(numerals[0])
         + numerals[num % b])

    if len(rv) < ln:
        return numerals[0] * (ln - len(rv)) + rv
    else:
        return rv


def frBaseN(num, b, numerals):
    rv = 0
    for i, c in enumerate(num):
        rv += numerals.index(c) * (b ** (len(num) - i - 1))
    return rv


def get_gid():
    """
    Tmp solution - hands out gid IDs based on a local counter - we'll
    replace this with a more permanent solution.
    """
    gidFile = conf.localgid.gidfile
    gidBase = conf.localgid.base
    if os.path.exists(gidFile):
        gid = open(gidFile).read()
    else:
        gid = gidBase[0] * 5
        with open(gidFile, 'w') as F:
            F.write(gid)

    newGid = toBaseN(frBaseN(gid, 36, gidBase) + 1, 36, 5, gidBase)

    with open(gidFile, 'w') as F:
        F.write(newGid)
    return gid
