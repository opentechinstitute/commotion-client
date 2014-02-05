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

from utils import fsUtils

#set function logger
log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.

def findConfigs(configType, name=None):
    """
    Function used to obtain the path to a config file.

    @param configType The type of configuration file sought. (global, user, extension)
    @param name optional The name of the configuration file if known

    @return list of tuples containing the path and name of found config files or False if a config matching the description cannot be found.
    """
    configFiles = getConfigPaths(configType)
    if configFiles:
        configs = getConfig(configFiles)
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

def getConfigPaths(configType):

    configLocations = {"global":"data/global/", "user":"data/user/", "extension":"data/extensions/"}
    configFiles = []
    
    try:
        path = configLocations[configType]
    except KeyError as e:
        log.error(QtCore.QCoreApplication.translate("logs", "Cannot search for config type {0} as it is an unsupported type.".format(configType)))
        self.log.debug(e, exc_info=1)
        return False
    try:
        for root, dirs, files in fsUtils.walklevel(path):
            for file_name in files:
                if file_name.endswith(".conf"):
                    configFiles.append(os.path.join(root, file_name))
    except AssertionError as e:
        log.error(QtCore.QCoreApplication.translate("logs", "Config file folder at path {0} does not exist. No Config files loaded.".format(path)))
        self.log.debug(e, exc_info=1)
    except TypeError as e:
        log.error(QtCore.QCoreApplication.translate("logs", "No config files found at path {0}. No Config files loaded.".format(path)))
        self.log.debug(e, exc_info=1)
    if configFiles:
        return configFiles
    else:
        return False


def getConfig(paths):
    """
    Generator to retreive config files for the paths passed to it

    @param a list of paths of the configuration file to retreive
    @return config file as a dictionary
    """
    #load config file
    for path in paths:
        try:
            if fsUtils.is_file(path):
                config = loadConfig(path)
                if config:
                    yield config
            else:
                log.error(QtCore.QCoreApplication.translate("logs", "Config file {0} does not exist and therefore cannot be loaded.".format(path)))
        except Exception as e:
            log.error(QtCore.QCoreApplication.translate("logs", "Config file {0} cannot be loaded.".format(path)))
            self.log.debug(e, exc_info=1)
        

def loadConfig(config):
    """
    This function loads a json formatted config file and returns it.

    @param fileName the name of the config file
    @param path the path to the configuration file in question
    @return a dictionary containing the config files values
    """
    #Open the file
    try:
        f = open(config, mode='r', encoding="utf-8", errors="strict")
    except ValueError as e:
        log.error(QtCore.QCoreApplication.translate("logs", "Config files must be in utf-8 format to avoid data loss. The config file {0} is improperly formatted ".format(config)))
        self.log.debug(e, exc_info=1)
        return False
    except Exception as e:
        log.error(QtCore.QCoreApplication.translate("logs", "An unknown error has occured in opening config file {0}. Please check that this file exists and is not corrupted.".format(config)))
        self.log.debug(e, exc_info=1)
        return False
    else:
        tmpMsg = f.read()
    #Parse the JSON
    try:
        data = json.loads(tmpMsg)
        log.debug(QtCore.QCoreApplication.translate("logs", "Successfully loaded {0}".format(config)))
        return data
    except ValueError as e:
        log.error(QtCore.QCoreApplication.translate("logs", "Failed to load {0} due to a non-json or otherwise invalid file type".format(config)))
        self.log.debug(e, exc_info=1)
        return False
    except Exception as e:
        log.error(QtCore.QCoreApplication.translate("logs", "Failed to load {0} due to an unknown error.".format(config)))
        self.log.debug(e, exc_info=1)
