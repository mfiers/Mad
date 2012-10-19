"""
Pfridge related code!
"""

import os
import sys
import json
import urllib
import urllib2

from madpy.logger import G
from madpy.conf import conf


def _PUT(url):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.get_method = lambda: 'PUT'
    F = opener.open(request)
    return F.read()


def _GET(url):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.get_method = lambda: 'GET'
    F = opener.open(request)
    return F.read()


def _POST(url, data):
    data = urllib.urlencode({'value': data})
    G.debug('data encoded %s' % data)
    G.debug('contacting %s' % url)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data)
    request.get_method = lambda: 'POST'
    F = opener.open(request)
    return F.read()


def save(md):

    G.debug('pfridge save')
    if not 'Gid' in md.keys():
        G.critical("error - no gid defined")
        sys.exit(-1)

    if not 'Pfridge' in md.keys():
        url = conf.pfridge.gidserver
        url += 'register/%s' % md['Gid']
        md['pfridge'] = md['Gid']
        G.debug("pfridge GID register")
        G.debug("calling %s" % url)

    for k in md.keys():
        if k == 'Gid':
            continue
        if k == 'Pfridge':
            continue

        v = md[k]
        url = conf.pfridge.metaserver + 'set/%s/%s' % (md['Gid'], k)
        G.debug("pfridge metadata store: %s %s" % (k, v))
        rv = _POST(url, v)
        G.debug("rv %s" % rv)
