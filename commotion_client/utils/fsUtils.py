#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fs_utils


"""

import os
import logging

#set function logger
log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.


def is_file(unknown):
    """
	Determines if a file is accessable. It does NOT check to see if the file contains any data.
	"""
#stolen from https://github.com/isislovecruft/python-gnupg/blob/master/gnupg/_util.py
    try:
        assert os.lstat(unknown).st_size > 0, "not a file: %s" % unknown
    except (AssertionError, TypeError, IOError, OSError) as err:
#end stolen <3
        log.debug("is_file():"+err.strerror)
        return False
    if os.access(unknown, os.R_OK):
        return True
    else:
        log.warn("is_file():You do not have permission to access that file")
        return False

def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
