"""
Representing metadata

"""

import os
import yaml
import collections

from madpy import plugin
from madpy import mvars
import madpy.util
from madpy.logger import G


class Metadata(object):

    def __init__(self, withname, mode='file'):
        """Object representing the metadata of filename.

        If mode == 'mad' - the filename is assumed to be the
        madfile. If mode == 'file', the metadata file is assumed to be
        the filename plus .mad.

        Note - started to ignore the 'mode' parameter - will determine
        that automatically (if the file ends with a .mad or not)
        """

        if withname[-4:] == '.mad':
            #this is the .mad file
            self.filename = withname[:-4]
            self.metafile = withname
        else:
            self.filename = withname
            self.metafile = withname + '.mad'

        if (not os.path.exists(self.filename)
                and not os.path.exists(self.metafile)):
            mad.util.exer("Neither filename not metadata file " +
                          "exist - do not know what to do")

        G.debug("created a metadata file for file %s" % self.filename)
        G.debug("metadata file is %s" % self.metafile)

        self.metadata = {}
        self.load()

    def apply_kv(self, k, v):
        mvars.update(self, k, v)

    def has_key(self, k):
        return k in self.metadata

    def keys(self):
        return self.metadata.keys()

    def __item__(self, k, v):
        self.metadata[k] = v

    def __getitem__(self, k):
        return self.metadata[k]

    def __setitem__(self, k, v):
        self.metadata[k] = v

    def load(self):
        """
        Check if there is a metadata file for *filename*.

        If so - load
        if not - return an empty dict

        """
        if os.path.exists(self.metafile):
            G.debug("loading metadata")
            with open(self.metafile) as F:
                self.metadata = yaml.load(F)

        plugin.run('post_metadata_load', self)

    def save(self):
        """
        Save the metadata for 'filename' - no questions asked
        """
        plugin.run('metadata_prepare', self)
        plugin.run('pre_metadata_save', self)
        with open(self.metafile, 'w') as F:
            F.write(yaml.dump(self.metadata, default_flow_style=False))

    def update(self, md):
        """
        First load the existing metadata, update it with the provided
        metadata, and save it again
        """
        self.metadata.update(md)

    def remove_keys(self, keys):
        """
        Remove a number of keys from the metadata
        """
        for k in keys:
            if k in self.metadata:
                del(self.metadata[k])
