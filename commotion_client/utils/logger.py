#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This program is a part of The Commotion Client

Copyright (C) 2014  Seamus Tuohy s2e@opentechinstitute.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#TODO create seperate levels for the stream, the file, and the full logger
from PyQt4 import QtCore
import logging
from logging import handlers
import os
import sys

class LogHandler(object):
    """
    Main logging controls for Commotion-Client. 
    
    This application is ONLY to be called by the main application. This logger sets up the main namespace for all other logging to take place within. All other loggers should be the core string "commotion_client" and the packages __name__ to use inheretance from the main commotion package. This way the code in an indivdual extension will be small and will inheret the logging settings that were defined in the main application.
    
    Example Use for ALL other modules and packages:
    
        from commotion-client.utils import logger
        log = logger.getLogger("commotion_client"+__name__)
    
    """
    
    def __init__(self, name, verbosity=None, logfile=None):
        #set core logger
        self.logger = logging.getLogger(str(name))
        self.logger.setLevel('DEBUG')
        #set defaults
        self.levels = {"CRITICAL":logging.CRITICAL, "ERROR":logging.ERROR, "WARN":logging.WARN, "INFO":logging.INFO, "DEBUG":logging.DEBUG}
        self.formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(lineno)d : %(message)s')
        self.stream = None
        self.file_handler = None
        self.logfile = None
        #setup logger
        self.set_logfile(logfile)
        self.set_verbosity(verbosity)

    def set_logfile(self, logfile=None):
        """Set the file to log to.
        
        Args:
        logfile (string): The absolute path to the file to log to.
          optional: defaults to the default system logfile path.
        """
        if logfile:
            log_dir = QtCore.QDir(os.path.dirname(logfile))
            if not log_dir.exists():
                if log_dir.mkpath(log_dir.absolutePath()):
                    self.logfile = logfile
        platform = sys.platform
        if platform == 'darwin':
            #Try <user>/Library/Logs first
            log_dir = QtCore.QDir(os.path.join(QtCore.QDir.homePath(), "Library", "Logs"))
            #if it does not exist try and create it
            if not log_dir.exists():
                if not log_dir.mkpath(log_dir.absolutePath()):
                    raise NotADirectoryError(self.translate("logs", "Attempted to set logging to the user's Commotion directory. The directory '<home>/.Commotion' does not exist and could not be created."))
            self.logfile = log_dir.filePath("commotion.log")
        elif platform in ['win32', 'cygwin']:
            #Try ../AppData/Local/Commotion first
            log_dir = QtCore.QDir(os.path.join(os.getenv('APPDATA'), "Local", "Commotion"))
            #if it does not exist try and create it
            if not log_dir.exists():
                if not log_dir.mkpath(log_dir.absolutePath()):
                    raise NotADirectoryError(self.translate("logs", "Attempted to set logging to the user's Commotion directory. The directory '<home>/.Commotion' does not exist and could not be created."))
            self.logfile = log_dir.filePath("commotion.log")
        elif platform == 'linux':
            #Try /var/logs/
            log_dir = QtCore.QDir("/var/logs/")
            if not log_dir.exists(): #Seriously! What kind of twisted linux system is this?
                if log_dir.mkpath(log_dir.absolutePath()):
                    self.logfile = log_dir.filePath("commotion.log")
                else:
                    #If fail then just write logs in home directory
                    #TODO check if this is appropriate... its not.
                    home = QtCore.QDir.home()
                    if not home.mkdir(".Commotion"):
                        raise NotADirectoryError(self.translate("logs", "Attempted to set logging to the user's Commotion directory. The directory '<home>/.Commotion' does not exist and could not be created."))
                    else:
                        home.cd(".Commotion")
                        self.logfile = home.filePath("commotion.log")
            else:
                self.logfile = log_dir.filePath("commotion.log")
        else:
            #I'm out!
            raise OSError(self.translate("logs", "Could not create a logfile."))

    def set_verbosity(self, verbosity=None, log_type=None):
        """Set's the verbosity of the logging for the application.
        
        Args:
          verbosity (string|int): The verbosity level for logging to take place.
            optional: Defaults to "Error" level
          log_type (string): The type of logging whose verbosity is to be changed.
            optional: If not specified ALL logging types will be changed.
        
        Returns:
          bool True if successful, False if failed
        
        Raises:
        exception: Description.
        
        """
        try:
            int_level = int(verbosity)
        except ValueError:
            if str(verbosity).upper() in self.levels.keys():
                level = self.levels[str(verbosity).upper()]
            else:
                return False
        else:
            if 1 <= int_level <= 5:
                _levels = [ 'CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG']
                level = self.levels[_levels[int_level-1]]
            else:
                return False
                
        if log_type == "stream":
            set_stream = True
        elif log_type == "logfile":
            set_logfile = True
        else:
            set_logfile = True
            set_stream = True

        if set_stream == True:
            self.logger.removeHandler(self.stream)
            self.stream = None
            self.stream = logging.StreamHandler()
            self.stream.setFormatter(self.formatter)
            self.stream.setLevel(level)
            self.logger.addHandler(self.stream)
        if set_logfile == True:
            self.logger.removeHandler(self.file_handler)
            self.file_handler = None
            self.file_handler = handlers.RotatingFileHandler(self.logfile,
                                                            maxBytes=5000000,
                                                            backupCount=5)
            self.file_handler.setFormatter(self.formatter)
            self.file_handler.setLevel(level)
            self.logger.addHandler(self.file_handler)
        return True

    def get_logger(self):
        return self.logger
