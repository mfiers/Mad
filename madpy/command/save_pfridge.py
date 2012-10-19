"""
generate file data
"""

import os
import sys

import mwclient
import socket
from datetime import datetime

from madpy.logger import G
from madpy import metadata
from madpy import pfridge


def hook_define_args(parser):
    """
    Set the arguments for 'smw upload'
    """
    parser.add_argument('file', nargs='+',
                        help='files to upload')


def run(args):
    """
    Upload the pages to SMW
    """

    files = args.file
    hostname = socket.gethostname()
    G.info("this is: %s" % hostname)

    for f in files:
        full_path = os.path.abspath(f)
        md = metadata.Metadata(f)
        G.info("Processing file %s" % f)
        md.metadata['Hostname'] = hostname
        md.metadata['FileLocation'] = full_path
        pfridge.save(md)

        # if args.attach:
        #     basename = os.path.basename(f)
        #     ufn = basename
        #     G.warning("Uploading file %s (%s)" % (ufn, full_path))
        #     with open(full_path, 'rb') as F:
        #         site.upload(file = F,
        #                     filename = ufn,
        #                     description = "Mad uploaded file for %s" % pname,
        #                     ignore=True)

        #     ppropps.append("[[AttachedFile::File:%s| ]]" % ufn)
