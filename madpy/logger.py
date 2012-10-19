#!/usr/bin/env python

# TODO: cut this file up in multiple subfiles

import os
import sys
import logging

G = logging.getLogger('mad')
handler = logging.StreamHandler()
logmark = chr(27) + '[0;37;43mMAD' + \
          chr(27) + '[0m ' 

formatter = logging.Formatter(
    logmark + '%(levelname)-6s %(message)s')

handler.setFormatter(formatter)
G.addHandler(handler)

def exerr(message):
    G.critical(message)
    sys.exit(-1)
