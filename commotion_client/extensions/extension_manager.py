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
        #get extension dir
        main_ext_dir = os.path.join(QtCore.QtDir.current(), "extensions" )
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type )
        extension_dir = QtCore.QtDir.mkpath( os.path.join(main_ext_type_dir, config['name'] ))
        extension_files = extension_dir.entryList()
        if not extension_config['main']:
            if "main.py" in extension_files:
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
            if "tests.py" in extension_files:
                extension_config['tests'] = "tests"
        _settings.endGroup()
        _settings.endGroup()
        return extension_config
        
    def remove_extension_settings(self, name):
        """Removes an extension and its core properties from the applications extension settings.

        @param name str the name of an extension to remove from the extension settings.
        """
        if len( str( name )) > 0:
            _settings = QtCore.QSettings()
            _settings.beginGroup( "extensions" )
            _settings.remove( str( name ) )
        else:
            _error = self.translate("logs", "You must specify an extension name greater than 1 char.")
            self.log.error( _error )
            raise ValueError( _error )

    def save_settings(self, extension_config, extension_type="contrib"):
        """Saves an extensions core properties into the applications extension settings

        @param extension_type string Type of extension "contrib" or "core". Defaults to contrib.
        @param extension_config dict Dictionary of key-pairs for json config.
        @return bool True if successful and False on failures
        """
        _settings = QtCore.QSettings()
        _settings.beginGroup( "extensions" )
        #get extension dir
        main_ext_dir = os.path.join(QtCore.QtDir.current(), "extensions" )
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type )
        extension_dir = QtCore.QtDir.mkpath( os.path.join(main_ext_type_dir, config['name'] ))
        #create validator
        config_validator = validate.ClientConfig(extension_config, extension_dir)
        #Extension Name
        if config_validator.name():
            try:
                extension_name = extension_config['name']
                _settings.beginGroup( extension_name )
            except KeyError:
            _error = self.translate("logs", "The extension is missing a  name value which is required.")
            self.log.error( _error )
            return False
        else:
            _error = self.translate("logs", "The extension's name is invalid and cannot be saved.")
            self.log.error( _error )
            return False
        #Extension Main
        if config_validator.gui("main"):
            try:
                _main = extension_config['main']
            except KeyError:
                if config_validator.main():
                    _main = "main" #Set this for later default values
                    _settings.value( "main", "main" )
                else:
                    _settings.value( "main", _main )
        else:
            _error = self.translate("logs", "The config's main value is invalid and cannot be saved.")
            self.log.error( _error )
            return False
        #Extension Settings & Toolbar
        for val in ["settings", "toolbar"]:
            if config_validator.gui(val):
                try:
                    _config_value = extension_config[val]
                except KeyError:
                    #Defaults to main, which was checked and set before
                    _settings.value( val, _main )
                else:
                    _settings.value( val,  _config_value)
            else:
                _error = self.translate("logs", "The config's {0} value is invalid and cannot be saved.").format(val))
                self.log.error(_error)
                return False
        #Extension Parent
        if config_validator.parent():
            try:
                _settings.value( "parent", extension_config["parent"] )
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "parent")))
                _settings.value( "parent", "Extensions" )
        else:
            _error = self.translate("logs", "The config's parent value is invalid and cannot be saved.")
            self.log.error( _error )
            return False

        #Extension Menu Item
        if config_validator.menu_item():
            try:
                _settings.value( "menu_item", extension_config["menu_item"] )
            except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_item")))
                _settings.value( "menu_item", extension_name )
        else:
            _error = self.translate("logs", "The config's menu_item value is invalid and cannot be saved.")
            self.log.error( _error )
            return False
        #Extension Menu Level
        if config_validator.menu_level():
            try:
                _settings.value( "menu_level", extension_config["menu_level"] )
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_level")))
                _settings.value( "menu_level", 10 )
        else:
            _error = self.translate("logs", "The config's menu_level value is invalid and cannot be saved.")
            self.log.error( _error )
            return False
        #Extension Tests
        if config_validator.tests():
            try:
                _settings.value( "main", extension_config['tests'] )
            except KeyError:
                    self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "tests")))
                    _settings.value( "tests", "tests" )
        else:
            _error = self.translate("logs", "Extension {0} does not contain the {1} file listed in the config for its tests. Please either remove the listing to allow for the default value, or add the appropriate file.".format(extension_config['name'], _config_value))
            self.log.error(_error)
            return False
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
        config_validator = validate.ClientConfig()
        try:
            config_validator.set_extension( unpacked.absolutePath() )
        except IOError:
            self.log.error(self.translate("logs", "Extension is invalid and cannot be saved."))
            self.log.info(self.translate("logs", "Cleaning extension's temp directory." )))
            fs_utils.clean_dir(unpacked)
            return False
        #Name
        if config_validator.name():
            config_path = os.path.join( unpacked.absolutePath(), "config.json" )
            config = config.load_config( config_path )
            existing_extensions = config.find_configs("extension")
            try:
                assert config['name'] not in existing_extensions
            except AssertionError:
                self.log.error(self.translate("logs", "The name given to this extension is already in use. Each extension must have a unique name."))
                self.log.info(self.translate("logs", "Cleaning extension's temp directory." )))
                fs_utils.clean_dir(unpacked)
                return False
        else:
            self.log.error(self.translate("logs", "The extension name is invalid and cannot be saved."))
            self.log.info(self.translate("logs", "Cleaning extension's temp directory." )))
            fs_utils.clean_dir(unpacked)
            return False
        #Check all values
        if not config_validator.validate_all():
            self.log.error(self.translate("logs", "The extension's config contains the following invalid value/s: [{0}]".format( ",".join(config_validator.errors) )))
            self.log.info(self.translate("logs", "Cleaning extension's temp directory." )))
            fs_utils.clean_dir(unpacked)
            return False
        #make new directory in extensions
        main_ext_dir = os.path.join(QtCore.QtDir.current(), "extensions" )
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type )
        extension_dir = QtCore.QtDir.mkpath( os.path.join(main_ext_type_dir, config['name'] ))
        try:
            fs_utils.copy_contents( unpacked, extension_dir )
        except:
            self.log.error(self.translate("logs", "Could not move extension into main extensions directory from temporary storage. Please try again." )))
            self.log.info(self.translate("logs", "Cleaning extension's temp and main directory." )))
            fs_utils.clean_dir(extension_dir)
            fs_utils.clean_dir(unpacked)
            return False
        else:
            fs_utils.clean_dir(unpacked)
        try:
            self.save_settings( config, extension_type)
        except KeyError:
            self.log.error(self.translate("logs", "Could not save the extension because it was missing manditory values. Please check the config and try again." )))
            self.log.info(self.translate("logs", "Cleaning extension directory and settings." )))
            fs_utils.clean_dir(extension_dir)
            self.remove_extension_settings(config['name'])
            return False
        return True

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
