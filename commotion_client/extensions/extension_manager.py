#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
extension_manager

The extension management object.

Key componenets handled within:
 * finding, loading, and unloading extensions
 * installing extensions

"""
#Standard Library Imports
import logging
import importlib
import shutil

#PyQt imports
from PyQt4 import QtCore

#Commotion Client Imports
from utils import config
from utils import fs_utils
from utils import validate
import extensions

class ExtensionManager():
    """   """
    def __init__(self, parent=None):
        self.log = logging.getLogger("commotion_client."+__name__)
        self.extensions = self.check_installed()
        self.translate = QtCore.QCoreApplication.translate


    def check_installed(self):
        """Creates dictionary keyed with the name of installed extensions with each extensions type.

        @returns dict Dictionary keyed with the name of installed extensions with each extensions type.
        """
        extensions = {}
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        _settings.beginGroup("core")
        core = settings.allKeys();
        _settings.endGroup()
        _settings.beginGroup("contrib")
        contrib = settings.allKeys();
        _settings.endGroup()
        _settings.endGroup()
        for ext in core:
            extensions[ext] = "core"
        for ext in contrib:
            extensions[ext] = "contrib"
        return extensions

    def load_user_interface(self, extension_name, subsection=None):
        """Return the full extension object or one of its primary sub-objects (settings, main, toolbar)

        @subsection str Name of a objects sub-section. (settings, main, or toolbar)
        """
        user_interface_types = {'main': "ViewPort", "setttings":"SettingsMenu", "toolbar":"ToolBar"}
        settings = self.load_settings(extension_name)
        if subsection:
            extension_name = extension_name+"."settings[subsection]
            subsection = user_interface_types[subsection]
        extension = self.import_extension(extension_name, subsection)
        return extension

    def import_extension(self, extension_name, subsection=None):
        """load extensions by string name."""
        if subsection:
            extension = importlib.import_module("."+subsection, "extensions."+extension_name)
        else:
            extension = importlib.import_module("."+extension_name, "extensions")
        return extension

    def load_settings(self, extension_name):
        """Gets an extension's settings and returns them as a dict.

        @return dict A dictionary containing an extensions properties.
        """
        extension_config = { "name":extension_name }
        extension_type = self.extensions[extension_name]
        
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        _settings.beginGroup(extension_type)
        extension_config['main'] = _settings.value("main", None)
        if not extension_config['main']:
            if fs_utils.is_file("extensions/"+extension_type+"/"+extension_name+"/main.py"):
                extension_config['main'] = "main"
            else:
                _error = self.translate("logs", "Extension {0} does not contain a \"main\" extension file. Please re-load or remove this extension.".format(extension_name))
                self.log.error(_error)
                raise IOError(_error)
        extension_config['settings'] = _settings.value( "settings", extension_config['main'] )
        extension_config['toolbar'] = _settings.value( "toolbar", extension_config['main'] )
        extension_config['parent'] = _settings.value( "parent", "Add-On's" )
        extension_config['menu_item'] = _settings.value( "menu_item", extension_config['name'] )
        extension_config['menu_level'] = _settings.value( "menu_level", 10 )
        extension_config['tests'] = _settings.value( "tests",  None )
        if not extension_config['tests']:
            if fs_utils.is_file("extensions/"+extension_type+"/"+extension_name+"/tests.py"):
                extension_config['tests'] = "tests"
        _settings.endGroup()
        _settings.endGroup()
        return extension_config
        
    def save_settings(self, extension_config, extension_type="contrib"):
        """Saves an extensions core properties into the applications extension settings

        @param extension_type string Type of extension "contrib" or "core". Defaults to contrib.
        @param extension_config dict Dictionary of key-pairs for json config.
        @return bool True if successful. It should raise various exceptions if it fails
        """
        
        _settings = QtCore.QSettings()
        _settings.beginGroup( "extensions" )
        #Extension Name
        try:
            extension_name = extension_config['name']
        except KeyError as _expt:
            self.log.error(self.translate("logs", "Could not load unknown extension because it's config file was missing a name value."))
            self.log.exception(_excp)
            raise
        else:
            extension_path = "extensions/"+extension_type+"/"+extension_name+"/"
            if fs_utils.is_file( extension_path ):
                _settings.beginGroup( extension_name )
            else:
                _error = self.translate("logs", "Extension {0} does not exist. Please re-load or remove this extension using the extension menu.".format(extension_config['name']))
                self.log.error(_error)
                raise IOError(_error)
        #Extension Main
        try:
            _main = extension_config['main']
        except KeyError:
            if fs_utils.is_file(extension_path+"main.py"):
                _main = "main" #Set this for later default values
                _settings.value( "main", "main" )
        else:
            if fs_utils.is_file(extension_path+_main+".py"):
                _settings.value( "main", _main )
            else:
                _error = self.translate("logs", "Extension {0} does not contain a \"main\" extension file. Please re-load or remove this extension.".format(extension_config['name']))
                self.log.error(_error)
                raise IOError(_error)
        #Extension Settings & Toolbar
        for val in ["settings", "toolbar"]:
            try:
                _config_value = extension_config[val]
            except KeyError:
                #Defaults to main, which was checked and set before
                _settings.value( val, _main )
            else:
                if fs_utils.is_file(extension_path+_config_value+".py"):
                    _settings.value( val,  _config_value)
                else:
                    _error = self.translate("logs", "Extension {0} does not contain the {1} file listed in the config. Please either remove the config listing to allow for the default value, or add the appropriate file.".format(extension_config['name'], _config_value))
                self.log.error(_error)
                raise IOError(_error)
        #Extension Parent
        try:
            _settings.value( "parent", extension_config["parent"] )
        except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "parent")))
            _settings.value( "parent", "Extensions" )
        #Extension Menu Item
        try:
            _settings.value( "menu_item", extension_config["menu_item"] )
        except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_item")))
            _settings.value( "menu_item", extension_name )
        #Extension Menu Level
        try:
            _settings.value( "menu_level", extension_config["menu_level"] )
        except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_level")))
            _settings.value( "menu_level", 10 )
        #Extension Tests
        try:
            _tests = extension_config['tests']
        except KeyError:
            if fs_utils.is_file(extension_path+"tests.py"):
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "tests")))
                _settings.value( "tests", "tests" )
            else:
                self.log.debug(self.translate("logs", "{0} does not contain any tests. Shame on you.... SHAME!".format(extension_name)))
        else:
            if fs_utils.is_file(extension_path+_tests+".py"):
                _settings.value( "main", _test )
            else:
                _error = self.translate("logs", "Extension {0} does not contain the {1} file listed in the config. Please either remove the listing to allow for the default value, or add the appropriate file.".format(extension_config['name'], _config_value))
                self.log.error(_error)
                raise IOError(_error)
        _settings.endGroup()
        _settings.endGroup()
        return True

    def save_extension(self, extension, extension_type="contrib", md5sum=None):
        """Unpacks a extension and attempts to add it to the Commotion system.

        @param extension
        @param extension_type string Type of extension "contrib" or "core". Defaults to contrib.
        @param md5sum
        @return bool True if an extension was saved, False if it could not save.
        """
        #There can be only two... and I don't trust you. 
        if extension_type != "contrib":
            extension_type = "core"

        if md5sum:
            try:
                self.verify_extension(md5sum)
            except InvalidSignature:
                self.log.error(self.translate("logs", "Could not verify extension. Please check that you used the correct key and extension file."))
                return False
        try:
            unpacked = self.unpack_extension(self, extension, extension_type)
        except IOError as _excpt:
            self.log.error(self.translate("logs", "Failed to unpack extension."))
            return False
        if not self.ensure_minimally_complete(unpacked):
            self.log.error(self.translate("logs", "Extension is not complete."))
            return False
            
                    #TODO THIS!!!

        #check if extension with that name already exists
        #make sure it has everythign it needs
        #move it into the proer folder
        #save it into settings


    def ensure_minimally_complete(self, extension):
        """Check that a package has the minimum required functional components"""
        files = extension.entryList()
        if "config.json" in files:
            config = config.load_config( os.path.join( extension.path(), "config.json" ))
        else:
            self.log.error(self.translate("logs", "Extension does not contain a config file."))
            return
        if not config["name"]:
            self.log.error(self.translate("logs", "The extension's config file does not contain a name value."))
            return False
        if config["main"]:
            if not ( str( config["name"] ) + ".py" ) in files:
                self.log.error(self.translate("logs", "The extension's config file specifys a 'main' python file that is missing."))
                return False
        else:
            if not ( "main.py" ) in files:
                self.log.error(self.translate("logs", "The extension is missing a 'main' python file."))
                return False
        if config["tests"]:
            if not ( str( config["tests"] ) + ".py" ) in files:
                self.log.error(self.translate("logs", "The extension's config file specifys a 'tests' python file that is missing."))
                return False
        for val in ["settings", "toolbar"]:
            if config[val]:
                if not ( str( config[val] ) + ".py" ) in files:
                    self.log.error(self.translate("logs", "The extension's config file specifys a '{0}' python file that is missing.".format(val)))
                return False
        
        
            

                
        
        for key, val in config.items():


            

    def verify_extension(self, md5sum):
        """Verify's a compressed extension against its MD5 sum

        @param md5sum path to file containing the md5 sum of a valid version of this extension
        """
        #TODO THIS!!!
        #Check valid sum
        #Check extension matches sum
        else:
            _error = QtCore.QCoreApplication.translate("logs", "Bad or modified extension! The current extension does not match the provided signature.")
            self.log.critical(_error)
            raise InvalidSignature(_error)

    def unpack_extension(self, compressed_extension, extension_type):
        """Unpacks an extension into a temporary directory and returns the location.

        @param compressed_extension string Path to the compressed_extension
        @param extension_type string Type of extension "contrib" or "core". Defaults to contrib.
        @return QDir A QDir object containing the path to the temporary directory
        """
        temp_dir = utils.fs_utils.make_temp_dir(new=True)
        temp_abs_path = temp_dir.absolutePath()
        try:
            shutil.unpack_archive(compressed_extension, temp_abs_path, "gztar")
        except ReadError as _excpt:
            _error = QtCore.QCoreApplication.translate("logs", "Could not load Commotion extension because it was corrupted or mis-packaged.")
            self.log.error(_error)
            raise IOError(_error)
        except FileNotFoundError as _excpt:
            _error = QtCore.QCoreApplication.translate("logs", "Could not load Commotion extension because it was not found.")
            self.log.error(_error)
            raise IOError(_error)
        return temp_dir

    def save_unpacked_extension(self, temp_dir, extension_name, extension_type):
        """Moves an extension from the temporary directory to the extension directory."""
        extension_path = "extensions/"+extension_type+"/"+extension_name
        full_path = os.path.join(QtCore.QDir.currentPath(), extension_path)
        if not s_utils.is_file(full_path):
            try:
                QtCore.QDir.mkpath(full_path)
                try:
                    fs_utils.copy_contents(temp_dir, full_path)
                except IOError as _excpt:
                    raise IOError( _excpt )
                else:
                    temp_dir.rmpath( temp_dir.path() )
                    return True
            except IOError:
                log.error(QtCore.QCoreApplication.translate( "logs", "Could not save unpacked extension into extensions directory.")
                return False
        else:
            _error = QtCore.QCoreApplication.translate( "logs", "An extension with that name already exists. Please delete the existing extension and try again." )
            log.error( _error )
            raise ValueError( _error )
        return True

class InvalidSignature(Exception):
    """A verification procedure has failed.

    This exception should only be handled by halting the current task.
    """
    pass
