"""
Store metadata in the Pfridge!
"""

from madpy import pfridge


def hook_pre_metadata_save(md):
    pfridge.save(md)
