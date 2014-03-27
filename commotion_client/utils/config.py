#!/usr/bin/env python3
# -*- coding: utf-8 -*-
                

"""
config

The configuration manager.
"""
import sys
import os
import json
import logging

from PyQt4 import QtCore

from commotion_client.utils import fs_utils

#set function logger
log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.

def find_configs(config_type, name=None):
    """
    Function used to obtain a config file.

    @param config_type The type of configuration file sought. (global, user, extension)
    @param name optional The name of the configuration file if known

    @return list of tuples containing a config name and its config.
    """
    config_files = get_config_paths(config_type)
    if config_files:
        configs = get_configs(config_files)
        return configs
    elif name != None:
        for conf in configs:
            if conf["name"] and conf["name"] == name:
                return conf
        log.error(QtCore.QCoreApplication.translate("logs", "No config of the chosed type named {0} found".format(name)))
        return False
    else:
        log.error(QtCore.QCoreApplication.translate("logs", "No Configs of the chosed type found"))
        return False

def get_config_paths(config_type):
    """
    Returns the paths to all config files.

    @param config_type string The type of config to get [ global|user|extension ]
    """
    configLocations = {"global":"data/global/configs", "user":"data/user/configs", "extension":"data/extensions/configs"}
    config_files = []
    
    try:
        path = os.path.join(QtCore.QDir.currentPath(), configLocations[config_type])
    except KeyError as _excp:
        log.warn(QtCore.QCoreApplication.translate("logs", "Cannot search for config type {0} as it is an unsupported type.".format(config_type)))
        log.exception(_excp)
        return False
    try:
        for root, dirs, files in fs_utils.walklevel(path):
            for file_name in files:
                if file_name.endswith(".conf"):
                    config_files.append(os.path.join(root, file_name))
    except AssertionError as _excp:
        log.error(QtCore.QCoreApplication.translate("logs", "Config file folder at path {0} does not exist. No Config files loaded.".format(path)))
        log.exception(_excp)
    except TypeError as _excp:
        log.error(QtCore.QCoreApplication.translate("logs", "No config files found at path {0}. No Config files loaded.".format(path)))
        log.exception(_excp)
    if config_files:
        return config_files
    else:
        return False


def get_configs(paths):
    """
    Generator to retreive config files for the paths passed to it

    @param a list of paths of the configuration file to retreive
    @return config file as a dictionary
    """
    #load config file
    for path in paths:
        if fs_utils.is_file(path):
            config = load_config(path)
            if config:
                yield config
        else:
            log.error(QtCore.QCoreApplication.translate("logs", "Config file {0} does not exist and therefore cannot be loaded.".format(path)))

def load_config(config):
    """
    This function loads a json formatted config file and returns it.

    @param config the path to a config file
    @return a dictionary containing the config files values
    """
    #Open the file
    try:
        f = open(config, mode='r', encoding="utf-8", errors="strict")
    except ValueError as _excp:
        log.warn(QtCore.QCoreApplication.translate("logs", "Config files must be in utf-8 format to avoid data loss. The config file {0} is improperly formatted ".format(config)))
        log.exception(_excp)
        return False
    except TypeError as _excp:
        log.warn(QtCore.QCoreApplication.translate("logs", "An unknown error has occured in opening config file {0}. Please check that this file is the correct type.".format(config)))
        log.exception(_excp)
        return False
    else:
        tmpMsg = f.read()
    #Parse the JSON
    try:
        data = json.loads(tmpMsg)
        log.info(QtCore.QCoreApplication.translate("logs", "Successfully loaded {0}".format(config)))
        return data
    except ValueError as _excp:
        log.warn(QtCore.QCoreApplication.translate("logs", "Failed to load {0} due to a non-json or otherwise invalid file type".format(config)))
        log.exception(_excp)
        return False
    except Exception as _excp:
        log.warn(QtCore.QCoreApplication.translate("logs", "Failed to load {0} due to an unknown error.".format(config)))
        log.exception(_excp)
