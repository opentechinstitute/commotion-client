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
import json

translate = QtCore.QCoreApplication.translate
log = logging.getLogger("commotion_client."+__name__)


def is_file(unknown):
    """Determines if a file is accessable. It does NOT check to see if the file contains any data.
    
    Args:
      unknown (string): The path to check for a accessable file.
    
    Returns:
      bool True if a file is accessable and readable, False if a file is unreadable, or unaccessable.
    
    """
    translate = QtCore.QCoreApplication.translate
    this_file = QtCore.QFile(str(unknown))
    if not this_file.exists():
        log.warn(translate("logs","The file {0} does not exist.".format(str(unknown))))
        return False
    if not os.access(unknown, os.R_OK):
        log.warn(translate("logs","You do not have permission to access the file {0}".format(str(unknown))))
        return False
    return True

def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    log.debug(translate("logs", "attempting to walk directory {0}".format(some_dir)))
    if not os.path.isdir(some_dir):
        raise NotADirectoryError(translate("logs", "{0} is not a directory. Can only 'walk' down through directories.".format(some_dir)))
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
    temp_path = "Commotion"
    temp_dir = QtCore.QDir.tempPath()
    if new:
        unique_dir_name = uuid.uuid4()
        temp_path = os.path.join(temp_path, str(unique_dir_name))
    temp_full = QtCore.QDir(os.path.join(temp_dir, temp_path))
    if temp_full.mkpath(temp_full.path()):
        log.debug(QtCore.QCoreApplication.translate("logs", "Creating main temporary directory"))
    else:
        _error = QtCore.QCoreApplication.translate("logs", "Error creating temporary directory")
        log.debug(_error)
        raise IOError(_error)
    return temp_full


def clean_dir(path=None):
    """ Cleans a directory. If not given a path it will clean the FULL temporary directory"""
    log = logging.getLogger("commotion_client."+__name__)
    if not path:
        path = QtCore.QDir(os.path.join(QtCore.QDir.tempPath(), "Commotion"))
    path.setFilter(QtCore.QDir.NoSymLinks | QtCore.QDir.Files)
    list_of_files = path.entryInfoList()

    for file_info in list_of_files:
        file_path = file_info.absoluteFilePath()
        if not QtCore.QFile(file_path).remove():
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
    list_of_files = start.entryInfoList()

    for file_info in list_of_files:
        source = file_info.absoluteFilePath()
        dest = os.path.join(end.path(), file_info.fileName())
        if not QtCore.QFile(source).copy(dest):
            _error = QtCore.QCoreApplication.translate("logs", "Error copying file into extensions directory. File already exists.")
            log.error(_error)
            raise IOError(_error)
    return True

def json_load(path):
    """This function loads a JSON file and returns a formatted dictionary.
    
    Args:
    path (string): The path to a json formatted file.
    
    Returns:
      The JSON data from the file formatted as a dictionary.
    
    Raises:
      TypeError: The file could not be opened due to an unknown error.
      ValueError: The file was of an invalid type (eg. not in utf-8 format, etc.)
    
    """
    translate = QtCore.QCoreApplication.translate
    log = logging.getLogger("commotion_client."+__name__)
    
    #Open the file
    try:
        f = open(string, mode='r', encoding="utf-8", errors="strict")
    except ValueError:
        log.warn(translate("logs", "Config files must be in utf-8 format to avoid data loss. The config file {0} is improperly formatted ".format(path)))
        raise
    except TypeError:
        log.warn(translate("logs", "An unknown error has occured in opening config file {0}. Please check that this file is the correct type.".format(path)))
        raise
    else:
       tmpMsg = f.read()
       #Parse the JSON
    try:
        data = json.loads(tmpMsg)
        log.info(translate("logs", "Successfully loaded {0}".format(path)))
        return data
    except ValueError:
        log.warn(translate("logs", "Failed to load {0} due to a non-json or otherwise invalid file type".format(path)))
        raise
