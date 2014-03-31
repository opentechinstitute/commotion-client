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
import os
import re
import sys
import pkgutil
import json

#PyQt imports
from PyQt4 import QtCore

#Commotion Client Imports
from commotion_client.utils import fs_utils
from commotion_client.utils import validate
from commotion_client import extensions

class ExtensionManager(object):
    def __init__(self):
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        self.extension_dirs = {}
        self.set_extension_dir_defaults()
        self.config_values = ["name",
                              "main",
                              "menu_item",
                              "menu_level",
                              "parent",
                              "settings",
                              "toolbar"]
        self.extensions = self.check_installed()
        _core = os.path.join(QtCore.QDir.currentPath(), "core_extensions")
        self.core = ConfigManager(_core)

    def set_extension_dir_defaults(self):
        """Sets self.extension_dirs dictionary for user and global extension directories to system defaults.
        
        Creates an extension folder, if it does not exit, in the operating systems default application data directories for the current user and for the global application. Then sets the extension managers extension_dirs dictionary to point to those directories.

        OS Defaults:
        
          OSX:
            user: $HOME/Library/Commotion/extension_data/
            global: /Library/Application Support /Commotion/extension_data/
        
          Windows:
            user: %APPDATA%\\Local\\Commotion\\extension_data\\.
            global: %COMMON_APPDATA%\\Local\\Commotion\extension_data\\.
            The %APPDATA% path is usually C:\\Documents and Settings\\User Name\\Application Data; the %COMMON_APPDATA% path is usually C:\\Documents and Settings\\All Users\\Application Data.
        
          Linux:
            user: $HOME/.Commotion/extension_data/
            global: /usr/share/Commotion/extension_data/
        
        Raises:
          IOError: If the application does not have permission to create ANY of the extension directories.
        """
        
        self.log.debug(self.translate("logs", "Setting the default extension directory defaults.")) 
        platform = sys.platform
        #Default global and user extension directories per platform.
        #win23, darwin, and linux supported.
        platform_dirs = {
            'darwin': {
                'user' : os.path.join("Library", "Commotion", "extension_data"),
                'user_root': QtCore.QDir.home(),
                'global' : os.path.join("Library", "Application Support", "Commotion", "extension_data"),
                'global_root' : QtCore.QDir.root()},
            'win32' : {
                'user':os.path.join("Local", "Commotion", "extension_data"),
                'user_root': QtCore.QDir(os.getenv('APPDATA')),
                'global':os.path.join("Local", "Commotion", "extension_data"),
                'global_root' : QtCore.QDir(os.getenv('COMMON_APPDATA'))},
            'linux': {
                'user':os.path.join(".Commotion", "extension_data"),
                'user_root': QtCore.QDir.home(),
                'global':os.path.join("usr", "share", "Commotion", "extension_data"),
                'global_root' : QtCore.QDir.root()}}
        
        #User Path Settings
        for path_type in ['user', 'global']:
            ext_dir = platform_dirs[platform][path_type+'_root']
            ext_path = platform_dirs[platform][path_type]
            if not ext_dir.exists():
                if ext_dir.mkpath(ext_path.absolutePath()):
                    ext_dir.setPath(ext_path)
                    self.log.debug(self.translate("logs", "Created the {0} extension directory at {1}".format(path_type, str(ext_dir.absolutePath()))))
                    self.extension_dirs[path_type] = ext_dir.absolutePath()
                    self.log.debug(self.translate("logs", "Set the {0} extension directory to {1}".format(path_type, str(ext_dir.absolutePath()))))
                else:
                    raise IOError(self.translate("logs", "Could not create the user extension directory."))
            else:
                self.extension_dirs[path_type] = ext_dir.absolutePath()
                self.log.debug(self.translate("logs", "Set the {0} extension directory to {1}".format(path_type, str(ext_dir.absolutePath()))))
    
    def check_installed(self, name=None):
        """Checks if and extension is installed.
            
        Args:
          name (type): Name of a extension to check. If not specified will check if there are any extensions installed.
            
        Returns:
          bool: True if named extension is installed, false, if not.
        """
        installed_extensions = self.get_installed().keys()
        if name and name in installed_extensions:
            return True
        elif not name and installed_extensions:
            return True
        else:
            return False

    def load_core(self):
        """Loads all core extensions.
        
        This function bootstraps the Commotion client when the settings are not populated on first boot or due to error. It iterates through all extensions in the core client and loads them.

        NOTE: Relies on save_settings to validate all fields.

        Returns:
          List of names (strings) of extensions loaded  on success. Returns False (bool) on failure.
        
        """
        installed = self.get_installed()
        exist = self.core.configs
        if not exist:
            self.log.info(self.translate("logs", "No extensions found."))
            return False
        for config_path in exist:
            _config = self.config.load_config(config_path)
            if _config['name'] in installed.keys():
                _type = installed[_config['name']]
                if _type == "global":
                    _ext_dir = os.path.join(self.extension_dir['global'], _config['name'])
                elif _type == "user":
                    _ext_dir = os.path.join(self.extension_dir['user'], _config['name'])
                else:
                    self.log.warn(self.translate("logs", "Extension {0} is of an unknown type. It will not be loaded".format(_config['name'])))
                    continue
            else:
                if QtCore.QDir(self.extension_dir['user']).exists(_config['name']):
                    _ext_dir = os.path.join(self.extension_dir['user'], _config['name'])
                elif QtCore.QDir(self.extension_dir['global']).exists(_config['name']):
                    _ext_dir = os.path.join(self.extension_dir['global'], _config['name'])
                else:
                    self.log.warn(self.translate("logs", "There is no corresponding data to accompany the config for extension {0}. It will not be loaded".format(_config['name'])))
                    continue
            if not self.save_settings(_config, _type):
                self.log.warn(self.translate("logs", "Extension {0} could not be saved.".format(_config['name'])))
            else:
                saved.append(_config['name'])
        return saved or False
                

    @staticmethod
    def get_installed():
        """Get all installed extensions seperated by type.

        Pulls the current installed extensions from the application settings and returns a dictionary with the lists of the two extension types.

        Returns:
          A dictionary keyed by the names of all extensions with the values being if they are a user extension or a global extension.

          {'coreExtensionOne':"user", 'coreExtensionTwo':"global",
           'contribExtension':"global", 'anotherContrib':"global"}

        """
#        WRITE_TESTS_FOR_ME()
        installed_extensions = {}
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        extensions = _settings.allKeys()
        for ext in extensions:
            installed_extensions[ext] = _settings.value(ext+"/type").toString()
        _settings.endGroup()
        return installed_extensions

    def get_extension_from_property(self, key, val):
        """Takes a property and returns all extensions who have the passed value set under the passed property.

        Checks all installed extensions and returns the name of all extensions whose config contains the key:val pair passed to this function.

        Args:
          key (string): The name of the property to be checked.
          val (string): The value that the property must have to be selected

        Returns:
          A list of extension names that have the key:val property in their config if they exist.
            ['ext01', 'ext02', 'ext03']

        Raises:
          KeyError: If the value requested is non-standard.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        matching_extensions = []
        if value not in self.config_values:
            _error = self.translate("logs", "That is not a valid extension config value.")
            raise KeyError(_error)
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        ext_sections = ['core', 'contrib']
        for ext_type in ext_sections:
            #enter extension type group
            _settings.beginGroup(ext_type)
            all_exts = _settings.allKeys()
            #QtCore.QStringList from allKeys() is missing the .toList() method from to its QtCore.QVariant.QStringList version. So, we do this horrible while loop instead. 
            while all_exts.isEmpty() != True:
                current_extension = all_exts.takeFirst()
                #enter extension settings
                _settings.beginGroup(current_extension)
                if _settings.value(key).toString() == str(val):
                    matching_extensions.append(current_extension)
                #exit extension
                _settings.endGroup()
            #exit extension type group
            _settings.endGroup()
        if matching_extensions:
            return matching_extensions
        else:
            self.log.debug(self.translate("logs", "No extensions had the requested value."))

    def get_property(self, name, key):
        """
        Get a property of an installed extension.
        
        Args:
          name (string): The extension's name.
          key (string): The key of the value you are requesting from the extension.

        Returns:
          A STRING containing the value associated the extensions key in the applications saved extension settings.
        
        Raises:
          KeyError: If the value requested is non-standard.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        if value not in self.config_values:
            _error = self.translate("logs", "That is not a valid extension config value.")
            raise KeyError(_error)
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        ext_type = self.get_type(name)
        _settings.beginGroup(ext_type)
        _settings.beginGroup(name)
        setting_value = _settings.value(key)
        if setting_value.isNull():
            _error = self.translate("logs", "The extension config does not contain that value.")
            raise KeyError(_error)
        else:
            return setting_value.toStr()

    def get_type(self, name):
        """Returns the extension type of an installed extension.
        
        Args:
          name (string): the name of the extension
        
        Returns:
          A string with the type of extension. "Core" or "Contrib"
        
        Raises:
          KeyError: If an extension does not exist.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        core_ext = _settings.value("core/"+str(name))
        contrib_ext = _settings.value("contrib/"+str(name))
        if not core_ext.isNull() and contrib_ext.isNull():
            return "core"
        elif not contrib_ext.isNull() and core_ext.isNull():
            return "contrib"
        else:
            _error = self.translate("logs", "This extension does not exist.")
            raise KeyError(_error)

    def load_user_interface(self, extension_name, subsection=None):
        """Return the full extension object or one of its primary sub-objects (settings, main, toolbar)
        
        @param extension_name string The extension to load
        @subsection string Name of a objects sub-section. (settings, main, or toolbar)
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        user_interface_types = {'main': "ViewPort", "setttings":"SettingsMenu", "toolbar":"ToolBar"}
        settings = self.load_settings(extension_name)
        if subsection:
            extension_name = extension_name+"."+settings[subsection]
            subsection = user_interface_types[subsection]
        extension = self.import_extension(extension_name, subsection)
        return extension

    @staticmethod
    def import_extension(extension_name, subsection=None):
        """
        Load extensions by string name.

        @param extension_name string The extension to load
        @param subsection string The module to load from an extension
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        if subsection:
            extension = importlib.import_module("."+subsection, "extensions."+extension_name)
        else:
            extension = importlib.import_module("."+extension_name, "extensions")
        return extension

    def load_settings(self, extension_name):
        """Gets an extension's settings and returns them as a dict.

        @return dict A dictionary containing an extensions properties.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        extension_config = {"name":extension_name}
        extension_type = self.extensions[extension_name]
        
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        _settings.beginGroup(extension_type)
        extension_config['main'] = _settings.value("main").toString()
        #get extension dir
        main_ext_dir = os.path.join(QtCore.QDir.currentPath(), "extensions")
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type)
        extension_dir = QtCore.QDir.mkpath(os.path.join(main_ext_type_dir, extension_config['name']))
        extension_files = extension_dir.entryList()
        if not extension_config['main']:
            if "main.py" in extension_files:
                extension_config['main'] = "main"
            else:
                _error = self.translate("logs", "Extension {0} does not contain a \"main\" extension file. Please re-load or remove this extension.".format(extension_name))
                raise IOError(_error)
        extension_config['settings'] = _settings.value("settings", extension_config['main']).toString()
        extension_config['toolbar'] = _settings.value("toolbar", extension_config['main']).toString()
        extension_config['parent'] = _settings.value("parent", "Add-On's").toString()
        extension_config['menu_item'] = _settings.value("menu_item", extension_config['name']).toString()
        extension_config['menu_level'] = _settings.value("menu_level", 10).toInt()
        extension_config['tests'] = _settings.value("tests").toString()
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
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        if len(str(name)) > 0:
            _settings = QtCore.QSettings()
            _settings.beginGroup("extensions")
            _settings.remove(str(name))
        else:
            _error = self.translate("logs", "You must specify an extension name greater than 1 char.")
            raise ValueError(_error)

    def save_settings(self, extension_config, extension_type="global"):
        """Saves an extensions core properties into the applications extension settings.
        
        long description
        
        Args:
          extension_config (dict) An extension config in dictionary format.
          extension_type (string): Type of extension "user" or "global". Defaults to global.
        
        Returns:
          bool: True if successful, False on failures
        
        Raises:
        exception: Description.
        
        """
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        #get extension dir
        try:
            extension_dir = self.extension_dirs[extension_type]
        except KeyError:
            self.log.warn(self.translate("logs", "Invalid extension type. Please check the extension type and try again."))
            return False
        #create validator
        config_validator = validate.ClientConfig(extension_config, extension_dir)
        #Extension Name
        if config_validator.name():
            try:
                extension_name = extension_config['name']
                _settings.beginGroup(extension_name)
            except KeyError:
                _error = self.translate("logs", "The extension is missing a  name value which is required.")
                self.log.error(_error)
                return False
        else:
            _error = self.translate("logs", "The extension's name is invalid and cannot be saved.")
            self.log.error(_error)
            return False
        #Extension Main
        if config_validator.gui("main"):
            try:
                _main = extension_config['main']
            except KeyError:
                if config_validator.main():
                    _main = "main" #Set this for later default values
                    _settings.value("main", "main").toString()
                else:
                    _settings.value("main", _main).toString()
        else:
            _error = self.translate("logs", "The config's main value is invalid and cannot be saved.")
            self.log.error(_error)
            return False
        #Extension Settings & Toolbar
        for val in ["settings", "toolbar"]:
            if config_validator.gui(val):
                try:
                    _config_value = extension_config[val]
                except KeyError:
                    #Defaults to main, which was checked and set before
                    _settings.value(val, _main).toString()
                else:
                    _settings.value(val, _config_value).toString()
            else:
                _error = self.translate("logs", "The config's {0} value is invalid and cannot be saved.".format(val))
                self.log.error(_error)
                return False
        #Extension Parent
        if config_validator.parent():
            try:
                _settings.value("parent", extension_config["parent"]).toString()
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "parent")))
                _settings.value("parent", "Extensions").toString()
        else:
            _error = self.translate("logs", "The config's parent value is invalid and cannot be saved.")
            self.log.error(_error)
            return False

        #Extension Menu Item
        if config_validator.menu_item():
            try:
                _settings.value("menu_item", extension_config["menu_item"]).toString()
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_item")))
                _settings.value("menu_item", extension_name).toString()
        else:
            _error = self.translate("logs", "The config's menu_item value is invalid and cannot be saved.")
            self.log.error(_error)
            return False
        #Extension Menu Level
        if config_validator.menu_level():
            try:
                _settings.value("menu_level", extension_config["menu_level"]).toInt()
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_level")))
                _settings.value("menu_level", 10).toInt()
        else:
            _error = self.translate("logs", "The config's menu_level value is invalid and cannot be saved.")
            self.log.error(_error)
            return False
        #Extension Tests
        if config_validator.tests():
            try:
                _settings.value("main", extension_config['tests']).toString()
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "tests")))
                _settings.value("tests", "tests").toString()
        else:
            _error = self.translate("logs", "Extension {0} does not contain the {1} file listed in the config for its tests. Please either remove the listing to allow for the default value, or add the appropriate file.".format(extension_config['name'], _config_value))
            self.log.error(_error)
            return False
        #Write extension type
        _settings.value("type", extension_type)
        _settings.endGroup()
        return True

    def save_extension(self, extension, extension_type="contrib", unpack=None):
        """Attempts to add an extension to the Commotion system.

        Args:
          extension (string): The name of the extension
          extension_type (string): Type of extension "contrib" or "core". Defaults to contrib.
          unpack (string or QDir): Path to compressed extension
        
        Returns:
          bool True if an extension was saved, False if it could not save.
        
        Raises:
        exception: Description.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        #There can be only two... and I don't trust you.
        if extension_type != "contrib":
            extension_type = "core"
        if unpack:
            try:
                unpacked = QtCore.QDir(self.unpack_extension(unpack))
            except IOError:
                self.log.error(self.translate("logs", "Failed to unpack extension."))
                return False
        else:
            self.log.info(self.translate("logs", "Saving non-compressed extension."))
            main_ext_dir = os.path.join(QtCore.QDir.currentPath(), "extensions")
            main_ext_type_dir = os.path.join(main_ext_dir, extension_type)
            unpacked = QtCore.QDir(os.path.join(main_ext_type_dir, extension))
            unpacked.mkpath(unpacked.absolutePath())
        config_validator = validate.ClientConfig()
        try:
            config_validator.set_extension(unpacked.absolutePath())
        except IOError:
            self.log.error(self.translate("logs", "Extension is invalid and cannot be saved."))
            self.log.info(self.translate("logs", "Cleaning extension's temp directory."))
            fs_utils.clean_dir(unpacked)
            return False
        #Name
        if config_validator.name():
            files = unpacked.entryList()
            for file_ in files:
                if re.match("^.*\.conf$", file_):
                    config_name = file_
                    config_path = os.path.join(unpacked.absolutePath(), file_)
            _config = self.config.load_config(config_path)
            existing_extensions = self.config.find_configs("extension")
            try:
                assert _config['name'] not in existing_extensions
            except AssertionError:
                self.log.error(self.translate("logs", "The name given to this extension is already in use. Each extension must have a unique name."))
                if unpack:
                    self.log.info(self.translate("logs", "Cleaning extension's temp directory."))
                    fs_utils.clean_dir(unpacked)
                return False
        else:
            self.log.error(self.translate("logs", "The extension name is invalid and cannot be saved."))
            if unpack:
                self.log.info(self.translate("logs", "Cleaning extension's temp directory."))
                fs_utils.clean_dir(unpacked)
            return False
        #Check all values
        if not config_validator.validate_all():
            self.log.error(self.translate("logs", "The extension's config contains the following invalid value/s: [{0}]".format(",".join(config_validator.errors))))
            if unpack:
                self.log.info(self.translate("logs", "Cleaning extension's temp directory."))
                fs_utils.clean_dir(unpacked)
            return False
        #make new directory in extensions
        main_ext_dir = os.path.join(QtCore.QDir.currentPath(), "extensions")
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type)
        extension_dir = QtCore.QDir(os.path.join(main_ext_type_dir, _config['name']))
        extension_dir.mkdir(extension_dir.path())
        if unpack:
            try:
                fs_utils.copy_contents(unpacked, extension_dir)
            except IOError:
                self.log.error(self.translate("logs", "Could not move extension into main extensions directory from temporary storage. Please try again."))
                if unpack:
                    self.log.info(self.translate("logs", "Cleaning extension's temp and main directory."))
                    fs_utils.clean_dir(extension_dir)
                    fs_utils.clean_dir(unpacked)
                return False
            else:
                if unpack:
                    fs_utils.clean_dir(unpacked)
        try:
            self.save_settings(_config, extension_type)
        except KeyError:
            self.log.error(self.translate("logs", "Could not save the extension because it was missing manditory values. Please check the config and try again."))
            if unpack:
                self.log.info(self.translate("logs", "Cleaning extension directory."))
                fs_utils.clean_dir(extension_dir)
            self.log.info(self.translate("logs", "Cleaning settings."))
            self.remove_extension_settings(_config['name'])
            return False
        try:
            self.add_config(unpacked.absolutePath(), config_name)
        except IOError:
            self.log.error(self.translate("logs", "Could not add the config to the core config directory."))
            if unpack:
                self.log.info(self.translate("logs", "Cleaning extension directory and settings."))
                fs_utils.clean_dir(extension_dir)
                self.log.info(self.translate("logs", "Cleaning settings."))
            self.remove_extension_settings(_config['name'])
            return False
        return True

    def add_config(self, extension_dir, name):
        """Copies a config file to the "loaded" core extension config data folder.
                       
        Args:
          extension_dir (string): The absolute path to the extension directory
          name (string): The name of the config file
        
        Returns:
          bool: True if successful
        
        Raises:
          IOError: If a config file of the same name already exists or the extension can not be saved.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        data_dir = os.path.join(QtCore.QDir.currentPath(), "data")
        config_dir = os.path.join(data_dir, "extensions")
        #If the data/extensions folder does not exist, make it.
        if not QtCore.Qdir(config_dir).exists():
            QtCore.Qdir(data_dir).mkdir("extensions")
        source = QtCore.Qdir(extension_dir)
        s_file = os.path.join(source.path(), name)
        dest_file = os.path.join(config_dir, name)
        if source.exists(name):
            if not QtCore.QFile(s_file).copy(dest_file):
                _error = QtCore.QCoreApplication.translate("logs", "Error saving extension config. File already exists.")
                raise IOError(_error)
        return True

    def remove_config(self, name):
        """Removes a config file from the "loaded" core extension config data folder.
                       
        Args:
          name (string): The name of the config file
        
        Returns:
          bool: True if successful
        
        Raises:
          IOError: If a config file does not exist in the extension data folder.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        data_dir = os.path.join(QtCore.QDir.currentPath(), "data")
        config_dir = os.path.join(data_dir, "extensions")
        config = os.path.join(config_dir, name)
        if QtCore.QFile(config).exists():
            if not QtCore.QFile(config).remove():
                _error = QtCore.QCoreApplication.translate("logs", "Error deleting file.")
                raise IOError(_error)
        return True
            
            
        

    def unpack_extension(self, compressed_extension):
        """Unpacks an extension into a temporary directory and returns the location.

        @param compressed_extension string Path to the compressed_extension
        @return A string object containing the absolute path to the temporary directory
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        temp_dir = fs_utils.make_temp_dir(new=True)
        temp_abs_path = temp_dir.absolutePath()
        try:
            shutil.unpack_archive(compressed_extension, temp_abs_path, "gztar")
        except FileNotFoundError:
            _error = QtCore.QCoreApplication.translate("logs", "Could not load Commotion extension because it was corrupted or mis-packaged.")
            raise IOError(_error)
        except FileNotFoundError:
            _error = QtCore.QCoreApplication.translate("logs", "Could not load Commotion extension because it was not found.")
            raise IOError(_error)
        return temp_dir.absolutePath()

    def save_unpacked_extension(self, temp_dir, extension_name, extension_type):
        """Moves an extension from a temporary directory to the extension directory.
        
        Args:
          temp_dir (string): Absolute path to the temporary directory
          extension_name (string): The name of the extension
          extension_type (string): The type of the extension (core or contrib)
        
        Returns:
          bool True if successful, false if unsuccessful.
        
        Raises:
          ValueError: If an extension with that name already exists. 
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        extension_path = "extensions/"+extension_type+"/"+extension_name
        full_path = os.path.join(QtCore.QDir.currentPath(), extension_path)
        if not fs_utils.is_file(full_path):
            try:
                QtCore.QDir.mkpath(full_path)
                try:
                    fs_utils.copy_contents(temp_dir, full_path)
                except IOError as _excpt:
                    raise IOError(_excpt)
                else:
                    temp_dir.rmpath(temp_dir.path())
                    return True
            except IOError:
                self.log.error(QtCore.QCoreApplication.translate("logs", "Could not save unpacked extension into extensions directory."))
                return False
        else:
            _error = QtCore.QCoreApplication.translate("logs", "An extension with that name already exists. Please delete the existing extension and try again.")
            raise ValueError(_error)

class InvalidSignature(Exception):
    """A verification procedure has failed.

    This exception should only be handled by halting the current task.
    """
    pass


class ConfigManager(object):

    def __init__(self, path=None):
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        if path:
            self.paths = self.get_paths(path)
            self.configs = []
            self.configs = self.get()
            
    def find(self, name=None):
        """
        Function used to obtain a config file from the ConfigManager.

        @param name optional The name of the configuration file if known
        @param path string The absolute path to the folder to check for extension configs.

        @return list of tuples containing a config name and its config.
        """
        if not self.configs:
            self.log.warn(self.translate("logs", "No configs have been loaded. Please load configs first.".format(name)))
            return False
        if not name:
            return self.configs
        elif name != None:
            for conf in self.configs:
                if conf["name"] and conf["name"] == name:
                    return conf
            self.log.error(self.translate("logs", "No config of the chosed type named {0} found".format(name)))
            return False

    def get_paths(self, directory):
        """Returns the paths to all config files within a directory.
        
        Args:
          directory (string): The path to the folder that extension's are within. Extensions can be up to one level below the directory given.
        
        Returns:
          config_files (array): An array of paths to all config files found in the directory given.
        
        Raises:
          TypeError: If no extensions exist within the directory requested.
          AssertionError: If the directory path does not exist.
        
        """
        #Check the directory and 
        dir_obj = QtCore.QDir(str(directory))
        if not dir_obj.exists(dir_obj.path()):
            self.log.warn(self.translate("logs", "Folder at path {0} does not exist. No Config files loaded.".format(str(directory))))
            return False
        else:
            path = dir_obj.absolutePath()

        config_files = []
        try:
            for root, dirs, files in fs_utils.walklevel(path):
                for file_name in files:
                    if file_name.endswith(".conf"):
                        config_files.append(os.path.join(root, file_name))
        except AssertionError:
            self.log.warn(self.translate("logs", "Config file folder at path {0} does not exist. No Config files loaded.".format(path)))
            raise
        except TypeError:
            self.log.warn(self.translate("logs", "No config files found at path {0}. No Config files loaded.".format(path)))
            raise
        if config_files:
            return config_files
        else:
            raise TypeError(self.translate("logs", "No config files found at path {0}. No Config files loaded.".format(path)))

    def get(self, paths):
        """
        Generator to retreive config files for the paths passed to it

        @param a list of paths of the configuration file to retreive
        @return config file as a dictionary
        """
        #load config file
        if not paths:
            paths = self.paths
        for path in paths:
            if fs_utils.is_file(path):
                config = self.load(path)
                if config:
                    yield config
            else:
                self.log.warn(self.translate("logs", "Config file {0} does not exist and therefore cannot be loaded.".format(path)))

    def load(self, path):
        """This function loads the formatted config file and returns it.
        
        long description
        
        Args:
        path (string): The path to a config file
        
        Returns:
          (dictionary) On success returns a dictionary containing the config file values.
          (bool): On failure returns False
        
        """
        myfile = QtCore.QFile(str(path))
        if not myfile.exists(myfile.absolutePath()):
            return False
        try:
            config = fs_utils.json_load(path)
        except ValueError, TypeError as _excpt:
            self.log.warn(self.translate("logs", "Could not load the config file {0}".format(str(path))))
            self.log.debug(_excpt)
            return False
        else:
            return config
