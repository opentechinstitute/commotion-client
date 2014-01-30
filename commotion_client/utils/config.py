#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
config

The configuration manager.
"""

import configparser  #sorry Jordan...
import os

#set function logger
log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.


def splitConfig(config):
    """
    Iterator that returns all configuration files (sections) nested in a specific config.
    """
    sections = config.section()
    for section in sections:
        yield config[section]


def findConfig(config_type):
    config = [

    #for 
    #if getConfig(name):

        
def getConfig(name):
    """
    Function to get a config file.

    @param name the name of the configuration file to retreive
    """
    #load config file
    try:
        checkFile(name) #TODO
        path = configPath(name)
        config = loadConfig(path)
    except:
        log.error(QtCore.QCoreApplication.translate("logs", "Config file {0} cannot be loaded.".format(name)))
        return False
    else:
        return config
    

def checkFile(name):
    
        
def addSectionHeader(properties_file, header_name):
   """
   add a config file does not have a section header. This adds it.
   
   configparser.ConfigParser requires at least one section header in a properties file.
   Our properties file doesn't have one, so add a header to it on the fly.
   https://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/2819788#2819788
   """
   yield '[{}]\n'.format(header_name)
   for line in properties_file:
     yield line


def loadConfig(path):
    """
    Load a single config file.

    @param path the path to the config file
    @return parsed config file
    """
    config_file = open(path, encoding="utf_8")
    config = configparser.ConfigParser()
    default_section_header = "CONFIG"
    try:
        config.read_file(config_file)
    except MissingSectionHeaderError:
        config.read_file(addSectionHeader(config_file, default_section_header))
    except:
        log.error(QtCore.QCoreApplication.translate("logs", "Config file {0} is not correctly formatted.".format(name)))
    else:
        return config
