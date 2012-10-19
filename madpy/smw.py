"""
Few random utilities
"""

import os
import sys

import getpass

import mwclient

from madpy.logger import G
from madpy.conf import conf
from madpy.util import exer

def get_site(args):

    if args.password:
        pwd = args.password
    else:
        pwd = getpass.getpass("SMW Password: ")

    G.info("Connecting to SMW")
    if conf.smw.https:
        site = mwclient.Site(('https', conf.smw.host), path=conf.smw.path)

    try:
        site = mwclient.Site(('http', conf.smw.host), path=conf.smw.path)
    except:
        try:
            site = mwclient.Site(('https', conf.smw.host), path=conf.smw.path)
        except:
            G.critical("Cannot login the swm site")
            raise
        
    try:
        site.login(args.username, pwd)
    except mwclient.errors.LoginError:
        exer("Can not login. (Wrong password?)")

    G.info("Connected to SMW")
    return site


def define_args(parser):
    """
    Define arguments for all interaction with SMW
    """
    parser.add_argument('-u', dest='username', help='mediawiki username')
    parser.add_argument('-p', dest='password', help='mediawiki password (optional)')
