"""
module for assigning gids based on a local counter
"""

import os
import json
import urllib2

from madpy.conf import conf
from madpy.logger import G


def hook_define_args(parser):
    pass


def hook_metadata_prepare(mdf):

    if 'gid' in mdf.metadata:
        G.debug("metadata has a gid")
        return True

    if not 'Sha1sum' in mdf.metadata:
        G.debug("metadata does not have a shasum")
        return True
    gid = _get_gid(mdf.metadata['Sha1sum'])
    mdf.metadata['Gid'] = gid


def _get_gid(shasum):
    """
    get a gid from a yourl server based on a sahsum
    """
    server = conf.yourlgid.server
    url = server + shasum

    F = urllib2.urlopen(url)
    rvr = F.read().split("<br />", 1)[1]
    rv = json.loads(rvr)
    gid = conf.yourlgid.idform % str(rv[0]['shorturl'])
    return gid
