"""
generate file data
"""

import os
import sys

import mwclient
import socket
from datetime import datetime

from madpy.conf import conf
from madpy.logger import G
from madpy import metadata
import madpy.smw


def hook_define_args(parser):
    """
    Set the arguments for 'smw upload'
    """
    madpy.smw.define_args(parser)
    parser.add_argument('file', nargs='+',
                        help='files to gather stats for')


def run(args):
    """
    Upload the pages to SMW
    """

    files = args.file
    hostname = socket.gethostname()
    G.info("this is: %s" % hostname)

    site = madpy.smw.get_site(args)

    for f in files:
        full_path = os.path.abspath(f)
        md = metadata.Metadata(f, mode=args.madmode)
        if not 'Gid' in md:
            G.critical("No Gid found - run 'mad init %s'" % f)
            sys.exit()
        G.info("Processing file %s" % f)

        pname = "%s" % (md.metadata['Gid'])
        page = site.Pages[pname]
        old_page_text = page.edit()
        separator = '<!-- MAD - Do not change anything above this line -->'
        if separator in old_page_text:
            old_page_text = old_page_text.split(separator)[1]
        md.metadata['Hostname'] = hostname
        md.metadata['FileLocation'] = full_path
        ppropps = []
        for k in md.metadata.keys():
            v = md.metadata[k]
            dti = conf.datatypes[k]
            if type(v) == type([]):
                for sv in v:
                    ppropps.append("[[%s::%s| ]]" % (k, sv))
            else:
                ppropps.append("[[%s::%s| ]]" % (k, v))

        if args.attach:
            basename = os.path.basename(f)
            ufn = basename
            G.warning("Uploading file %s (%s)" % (ufn, full_path))
            with open(full_path, 'rb') as F:
                site.upload(file = F,
                            filename = ufn,
                            description = "Mad uploaded file for %s" % pname,
                            ignore=True)

            ppropps.append("[[AttachedFile::File:%s| ]]" % ufn)

        if args.force:
            new_page = "\n" + " ".join(ppropps) + "[[Category:MadObject]]\n{{" + \
                       args.template + "}}\n" + separator
        else:
            new_page = "\n" + " ".join(ppropps) + "[[Category:MadObject]]\n{{" + \
                       args.template + "}}\n" + separator + old_page_text
        #print new_page
        page.save(new_page, summary="Mad created/refreshed object data")
