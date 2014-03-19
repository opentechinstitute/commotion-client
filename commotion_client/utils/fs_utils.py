#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fs_utils


"""

#PyQt imports
from PyQt4 import QtCore

#Standard Library Imports
import os
import logging
import uuid

def is_file(unknown):
    """
	Determines if a file is accessable. It does NOT check to see if the file contains any data.
	"""
    #stolen from https://github.com/isislovecruft/python-gnupg/blob/master/gnupg/_util.py
    #set function logger
    log = logging.getLogger("commotion_client."+__name__)
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

def make_temp_dir(new=None):
    """Makes a temporary directory and returns the QDir object.

    @param new bool Create a new uniquely named directory within the exiting Commotion temp directory and return the new folder object
    """
    log = logging.getLogger("commotion_client."+__name__)
    temp_path = "/Commotion/"
    if new:
        unique_dir_name = uuid.uuid4()
        temp_path += str(unique_dir_name)
#    temp_dir = QtCore.QDir(QtCore.QDir.tempPath() + temp_path)
    temp_dir = QtCore.QDir(os.path.join(QtCore.QDir.tempPath(), temp_path))
    if QtCore.QDir().mkpath(temp_dir.path()):
        log.debug(QtCore.QCoreApplication.translate("logs", "Creating main temporary directory"))
    else:
        _error = QtCore.QCoreApplication.translate("logs", "Error creating temporary directory")
        log.error(_error)
        raise IOError(_error)
    return temp_dir


def clean_dir(path=None):
    """ Cleans a directory. If not given a path it will clean the FULL temporary directory"""
    log = logging.getLogger("commotion_client."+__name__)
    if not path:
        path = QtCore.QDir(os.path.join(QtCore.QDir.tempPath(), "Commotion"))
    path.setFilter(QtCore.QDir.NoSymLinks | QtCore.QDir.Files)
    list_of_files = path.entryList()

    for file_ in list_of_files:
        file_ = os.path.join(path.path(), file_)
        if not QtCore.QFile(file_).remove():
            _error = QtCore.QCoreApplication.translate("logs", "Error saving extension to extensions directory.")
            log.error(_error)
            raise IOError(_error)
    path.rmpath(path.path())
    return True

def copy_contents(start, end):
    """ Copies the contents of one directory into another

    @param start QDir A Qdir object for the first directory
    @param end QDir A Qdir object for the final directory
    """
    log = logging.getLogger("commotion_client."+__name__)
    start.setFilter(QtCore.QDir.NoSymLinks | QtCore.QDir.Files)
    list_of_files = start.entryList()

    for file_ in list_of_files:
        source = os.path.join(start.path(), file_)
        dest = os.path.join(end.path(), file_)
        if not QtCore.QFile(source).copy(dest):
            _error = QtCore.QCoreApplication.translate("logs", "Error copying file into extensions directory. File already exists.")
            log.error(_error)
            raise IOError(_error)
    return True
