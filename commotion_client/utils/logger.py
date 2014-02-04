#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2014 Seamus Tuohy
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Main logging controls for Commotion-Client
"""

#TODO create seperate levels for the stream, the file, and the full logger

import logging
#TODO Create a config parser and uncomment the following line to use it
#from . import config

def set_logging(name, verbosity=None, logfile=None):
    """
    Creates a logger object
    """
    logger = logging.getLogger(name) 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(processName)s:%(lineno)d - %(levelname)s - %(message)s')
    if logfile:
        fh = logging.FileHandler(logfile)
    else:
        #TODO Create a config parser and uncomment the following line to use it
        #default_logfile = config.get("logfile")
        fh = logging.FileHandler(default_logfile)
    fh.setFormatter(formatter)
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    #set alternate verbosity
    if verbosity == None:
        stream.setLevel(logging.ERROR)
        fh.setLevel(logging.WARN)
    elif 1 <= verbosity <= 5:
        levels = [logging.CRITICAL, logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
        print(verbosity)
        stream.setLevel(levels[(verbosity-1)])
        fh.setLevel(levels[(verbosity-1)])
        logger.setLevel(levels[(verbosity-1)])
    else:
        raise TypeError("""The Logging level you have defined is not supported please enter a number between 1 and 5""")
    #Add handlers to logger
    logger.addHandler(fh)
    logger.addHandler(stream)
    return logger


#    [TO CALL LOGGER]
#
#    from commotion-client.utils import logger
#    #This logger should be the packages __name__ to use inheretance from the main commotion package. This way the code in an indivdual extension will be small and it will use the logging settings that were defined in the main logging function.
#    log = logger.getLogger(__name__)
#    #The main function calls log = logger.set_logging("commotion_client", 5, "/os/specific/logfile/loc")
