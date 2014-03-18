#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
validate

A collection of validation functions

Key componenets handled within:

"""
#Standard Library Imports
import logging
import sys
import re

#PyQt imports
from PyQt4 import QtCore


class ClientConfig():

    def __init__(self, config=None, directory=None):
        if config:
            self._config = config.load_config(config)
        self._directory = directory
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate

    def set_extension(directory, config=None):
        """Set the default values

        @param config string The absolute path to a config file for this extension
        @param directory string The absolute path to this extensions directory
        """
        self._directory = directory
        if config:
            self._config = config.load_config(config)
        else:
            default_config_path = os.path.join( self._directory, "config.json" )
            if fs_utils.is_file( default_config_path ):
                self._config = config.load_config(default_config_path)
            else:
                raise IOError(self.translate("logs", "Extension does not contain a config file and is therefore invalid."))
        
    def validate_all(self):
        """Run all validation functions on an uncompressed extension.
        
        @brief Will set self.errors if any errors are found.
        @return bool True if valid, False if invalid. 
        """
        self.errors = None
        if not directory:
            if not self.directory:
                raise NameError(self.translate("logs", "ClientConfig validator requires at least an extension directory to be specified"))
            else:
                directory = self.directory
        errors = []
        if not self.name():
            errors.append("name")
        if not self.tests():
            errors.append("tests")
        if not self.menu_level():
            errors.append("menu_level")
        if not self.menu_item():
            errors.append("menu_item")
        if not self.parent():
            errors.append("parent")        
        else:
            for gui_name in ['main', 'settings', 'toolbar']:
                if not self.gui( gui_name ):
                    errors.append( gui_name )
        if errors:
            self.errors = errors
            return False
        else:
            return True


    def gui( self, gui_name ):
        """Validate of one of the gui objects config values. (main, settings, or toolbar)

        @param gui_name string "main", "settings", or "toolbar"
        """
        try:
            val = str( self._config[ gui_name ] )
        except KeyError:
            if gui_name != "main":
                try:
                    val = str( self._config[ "main" ] )
                except KeyError:
                    val = str( 'main' )
            else:
                val = str( 'main' )
        file_name = val + ".py"
        if not self.check_path( file_name ):
            self.log.warn(self.translate( "logs", "The extensions {0} file name is invalid for this system.".format( gui_name ) ))
            return False
        if not self.check_exists( file_name ):
            self.log.warn(self.translate( "logs", "The extensions {0} file does not exist.".format( gui_name ) ))
            return False
        return True

    def name( self ):
        try:
            name_val = str( self._config['name'] )
        except KeyError:
            self.log.warn(self.translate( "logs", "There is no name value in the config file. This value is required." ))
            return False
        if not self.check_path_length( name_val ):
            self.log.warn(self.translate( "logs", "This value is too long for your system." ))
            return False
        if not self.check_file_chars( name_val ):
            self.log.warn(self.translate( "logs", "This value uses invalid characters for your system." ))
            return False
        return True

    def menu_item( self ):
        """Validate a  menu item value."""
        try:
            val = str( self._config[ "menu_item" ] )
        except KeyError:
            if self.name():
                val = str( self._config[ "name" ] )
            else:
                self.log.warn(self.translate( "logs", "The name value is the default for a menu_item if none is specified. You don't have a menu_item specified and the name value in this config is invalid." ))
                return False
        if not check_menu_text( val ):
            self.log.warn(self.translate("logs", "The menu_item value is invalid"))
            return False
        return True

    def parent( self ):
        """Validate a  parent value."""
        try:
            val = str( self._config[ "parent" ] )
        except KeyError:
            self.log.info(self.translate( "logs", "There is no 'parent' value set in the config. As such the default value of 'Extensions' will be used." ))
            return True
        if not self.check_menu_text( val ):
            self.log.warn(self.translate("logs", "The parent value is invalid"))
            return False
        return True

    def menu_level( self ):
        """Validate a Menu Level Config item."""
        try:
            val = int( self._config[ "menu_level" ] )
        except KeyError:
            self.log.info(self.translate( "logs", "There is no 'menu_level' value set in the config. As such the default value of 10 will be used." ))
            return True
        except ValueError:
            self.log.info(self.translate( "logs", "The 'menu_level' value set in the config is not a number and is therefore invalid." ))
            return False
        if not ( 0 < val > 100 ):
            self.log.warn(self.translate("logs", "The menu_level is invalid. Choose a number between 1 and 100"))
            return False
        return True

    def tests( self ):
        """Validate a tests config menu item."""
        try:
            val = str( self._config[ "tests" ] )
        except KeyError:
            val = str( 'tests' )
        file_name = val + ".py"
        if not self.check_path( file_name ):
            self.log.warn(self.translate( "logs", "The extensions 'tests' file name is invalid for this system."))
            return False
        if not self.check_exists( file_name ):
            self.log.warn(self.translate( "logs", "The extensions 'tests' file does not exist." ))
            return False
        return True
        
    def check_menu_text( self, menu_text ):
        """
        Checks that menu text fits within the accepted string length bounds.

        @param menu_text string The text that will appear in the menu.
        """
        if not ( 3 < len( str( menu_text )) > 40 ):
            self.log.warn(self.translate("logs", "Menu items must be between 3 and 40 chars long. Becuase it looks prettier that way."))
            return False
            
    def check_exists(self, file_name):
        """Checks if a specified file exists within a directory

        @param file_name string The file name from a config file
        """
        files = QtCore.QDir(self.directory).entryList()
        if not ( str( file_name )) in files:
            self.log.warn(self.translate("logs", "The specified file does not exist."))
            return False
        else:
            return True
            
    def check_path(self, file_name):
        """Runs all path checking functions on a string.

        @param file_name string  The string to check for validity.
        """
        if not check_path_length( file_name ):
            self.log.warn(self.translate( "logs", "This value is too long for your system." ))
            return False
        if not check_file_chars( file_name ):
            self.log.warn(self.translate( "logs", "This value uses invalid characters for your system." ))
            return False
        return True

    def check_path_chars(self, file_name):
        """Checks if a string is a valid file name on this system.

        @param file_name string The string to check for validity
        """
        # file length limit
        platform  = sys.platform
        reserved = { "cygwin" : "[\|\\\?\*<\":>\+\[\]/]",
                     "win32" : "[\|\\\?\*<\":>\+\[\]/]",
                     "darwin" : "[:]",
                     "linux" : "[/\x00]" }
        if platform and reserved[platform]:
            if re.search( file_name, reserved[platform] ):
                self.log.warn(self.translate("logs", "The extension's config file contains an invalid main value."))
                return False
            else:
                return True
        else:
            self.log.warn(self.translate("logs", "Your system, {0} is not recognized. This may cause instability if file uses chars that your system does not allow.").format(platform))
            return True
                
            
    def check_path_length(self, file_name=None):
        """Checks if a string will be of a valid length for a file name and full path on this system.

        @param file_name string The string to check for validity.
        """
        # file length limit
        platform  = sys.platform
        # OSX(name<=255),  linux(name<=255)
        name_limit = ['linux', 'darwin']
        # Win(name+path<=260),
        path_limit = ['win32', 'cygwin']
        if platform in path_limit:
            if self.name(): #check valid name before using it
                extension_path = os.path.join( QtCore.QDir.currentPath(), "extensions" )
                full_path = os.path.join( extension_path, file_name )
            else:
                self.log.warn(self.translate("logs", "The extension's config file 'main' value requires a valid 'name' value. Which this extension does not have."))
                return False
            if len( str( full_path )) > 255:
                self.log.warn(self.translate("logs", "The full extension path cannot be greater than 260 chars"))
                return False
        else if platform in name_limit:
            if len( str( file_name ) ) > 260:
                self.log.warn(self.translate("logs", "File names can not be greater than 260 chars on your system"))
                return False
        else:
            self.log.warn(self.translate("logs", "Your system, {0} is not recognized. This may cause instability if file or path names are longer than your system allows.").format(platform))
            return True
