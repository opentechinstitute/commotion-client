#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
extension_manager

The extension management object.

Key componenets handled within:
 * finding, loading, and unloading extensions
 * installing extensions

-----------
Definitions:
-----------

Library: The [core, user, & global] folders that hold the extension zip archives.

Loaded: An extension (Library) that has been found by the ExtensionManager and has had its config loaded into one of the ConfigManagers [core, global, user].

Installed: An extension that has been saved into the [user or global] applications settings. On initial installation the extension will be set to initialized and show up in the main extension settings menu.

Initialized: An installed extension that has had its "initialized" flag set to true. Initalized applications show up in the menu and have a personal settings page if enabled.

Disabled: An installed extension that has had its "initialized" flag set to false. Disabled applications will not show up in the menu or have their personal settings page enabled, but will still show up in the main extension settings menu.

Uninstalled: An extension that has been removed from the application settings and also had its library deleted from all extension directories [user global]

Core Extensions: Core extensions are extensions that are loaded along with the application. On restart these extensions are checked against the global extensions, and if missing copied into the global extension directory and re-installed.

Global Extensions: Global extensions are extensions that are available for all logged in users.

User Extensions: User extensions are extensions that are only installed for the current user.

"""
#Standard Library Imports
import logging
import importlib
import shutil
import os
import re
import sys
import zipfile
import json
import zipimport

#PyQt imports
from PyQt4 import QtCore

#Commotion Client Imports
from commotion_client.utils import fs_utils
from commotion_client.utils import validate
from commotion_client.utils import settings
from commotion_client import extensions

class ExtensionManager(object):
    
    def __init__(self):
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        self.extensions = {}
        self.libraries = {}
        self.user_settings = self.get_user_settings()
        self.config_keys = ["name",
                            "main",
                            "menu_item",
                            "menu_level",
                            "parent",
                            "settings",
                            "toolbar",
                            "tests",
                            "initialized",
                            "type",]

    def get_user_settings(self):
        """Get the currently logged in user settings object."""
        settings_manager = settings.UserSettingsManager()
        _settings = settings_manager.get()
        if _settings.Scope() == 0:
            _settings.beginGroup("extensions")
            return _settings
        else:
            raise TypeError(self.translate("logs", "User settings has a global scope and will not be loaded. Because, security."))

    
    def init_extension_libraries(self):
        """This function bootstraps the Commotion client when the settings are not populated on first boot or due to error. It iterates through all extensions in the core client and loads them."""
        
        #set default library paths
        self.set_library_defaults()
        #create directory structures if needed
        self.init_libraries()
        #load core and move to global if needed
        self.load_core()
        #Load all extension configs found in libraries
        self.init_extension_config()
        #install all loaded config's with the existing settings
        self.install_loaded()

    def set_library_defaults(self):
        """Sets the default directories for core, user, and global extensions.
        
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
        #==== Core ====#
        _app_path = QtCore.QDir(QtCore.QCoreApplication.applicationDirPath())
        _app_path.setPath("extensions")
        #set the core extension directory
        self.libraries['core'] = _app_path.absolutePath()
        self.log.debug(self.translate("logs", "Core extension directory succesfully set."))

        #==== SYSTEM DEFAULTS =====#
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
        for path_type in ['user', 'global']:
            ext_dir = platform_dirs[platform][path_type+'_root']
            ext_path = platform_dirs[platform][path_type]
            #move the root directory to the correct sub-path.
            ext_dir.setPath(ext_path)
            #Set the extension directory.
            self.libraries[path_type] = ext_dir.absolutePath()

    def init_libraries(self):
        """Creates a library folder, if it does not exit, in the directories specified for the current user and for the global application. """
        #==== USER & GLOBAL =====#
        for path_type in ['user', 'global']:
            try:
                ext_dir = QtCore.QDir(self.libraries[path_type])
            except KeyError:
                self.log.warning(self.translate("logs", "No directory is specified for the {0} library. Try running set_library_defaults to initalize the default libraries.".format(path_type)))
                #If the directories are not yet created. We are not going to have this fail.
                continue
            if not ext_dir.exists():
                if ext_dir.mkpath(ext_dir.absolutePath()):
                    self.log.debug(self.translate("logs", "Created the {0} extension library at {1}".format(path_type, str(ext_dir.absolutePath()))))
                else:
                    raise IOError(self.translate("logs", "Could not create the user extension library for {0}.".format(path_type)))
            else:
                self.log.debug(self.translate("logs", "The extension library at {0} already existed for {1}".format(str(ext_dir.absolutePath()), path_type)))

    def init_extension_config(self, ext_type=None):
        """ Initializes config objects for the path of extensions.

        Args:
          ext_type (string): A specific extension type to load/reload a config object from. [global, user, or core]. If not provided, defaults to all.

        Raises:
          ValueError: If the extension type passed is not either [core, global, or user]
        """
        self.log.debug(self.translate("logs", "Initializing {0} extension configs..".format(ext_type)))
        extension_types = ['user', 'global', 'core']
        if ext_type:
            if str(ext_type) in extension_types:
                extension_types = [ext_type]
            else:
                raise ValueError(self.translate("logs", "{0} is not an acceptable extension type.".format(ext_type)))
        for type_ in extension_types:
            self.extensions[type_] = ConfigManager(self.libraries[type_])
            self.log.debug(self.translate("logs", "Configs for {0} extension library loaded..".format(type_)))

    def check_installed(self, name=None):
        """Checks if and extension is installed.
            
        Args:
          name (type): Name of a extension to check. If not specified will check if there are any extensions installed.
            
        Returns:
          bool: True if named extension is installed, false, if not.
        """
        installed_extensions = list(self.get_installed().keys())
        if name and name in installed_extensions:
            self.log.debug(self.translate("logs", "Extension {0} found in installed extensions.".format(name)))
            return True
        elif not name and installed_extensions:
            self.log.debug(self.translate("logs", "Installed extensions found."))
            return True
        else:
            self.log.debug(self.translate("logs", "Extension/s NOT found."))
            return False

    def get_installed(self):
        """Get all installed extensions seperated by type.

        Pulls the current installed extensions from the application settings and returns a dictionary with the lists of the two extension types.

        Returns:
          A dictionary keyed by the names of all extensions with the values being if they are a user extension or a global extension.

          {'coreExtensionOne':"user", 'coreExtensionTwo':"global",
           'contribExtension':"global", 'anotherContrib':"global"}

        """
        self.log.debug(self.translate("logs", "Getting installed extensions."))
        installed_extensions = {}
        _settings = self.user_settings
        extensions = _settings.childGroups()
        for ext in extensions:
            installed_extensions[ext] = _settings.value(ext+"/type")
        self.log.debug(self.translate("logs", "The following extensions are installed: [{0}].".format(extensions)))
        return installed_extensions
            
    def load_core(self):
        """Loads all core extensions into the globals library and re-initialized the global config.
        
        This function bootstraps global library from the core library. It iterates through all extensions in the core library and populates the global config with any extensions it does not already contain and then loads them into the global config.

        """
        #Core extensions are loaded from the global directory.
        #If a core extension has been deleted from the global directory it will be replaced from the core directory.
        self.init_extension_config('core')
        _core_dir = QtCore.QDir(self.libraries['core'])
        _global_dir = QtCore.QDir(self.libraries['global'])
        _reload_globals = False
        for ext in self.extensions['core'].configs:
            try:
                #Check if the extension is in the globals
                global_extensions = list(self.extensions['global'].configs.keys())
                if ext['name'] in global_extensions:
                    continue
            except KeyError:
                #If extension not loaded in globals it will raise a KeyError
                _core_ext_path = _core_dir.absoluteFilePath(ext['name'])
                _global_ext_path = _global_dir.absoluteFilePath(ext['name'])
                self.log.info(self.translate("logs", "Core extension {0} was missing from the global extension directory. Copying it into the global extension directory from the core now.".format(ext['name'])))
                #Copy extension into global directory
                if QtCore.QFile(_core_ext_path).copy(_global_ext_path):
                    self.log.debug(self.translate("logs", "Extension config successfully copied."))
                else:
                    self.log.debug(self.translate("logs", "Extension config was not copied."))
                _reload_globals = True
        if _reload_globals == True:
            self.init_extension_config("global")

    def install_loaded(self, ext_type=None):
        """Installs loaded libraries by saving their settings into the application settings.

        This function will install all loaded libraries into the users settings. It will add any missing configs and values that are not found. If a value exists install loaded will not change it.
        
        Args:
          ext_type (string): A specific extension type [global or user] to load extensions from. If not provided, defaults to both.

        Returns:
          List of names (strings) of extensions loaded  on success. Returns and empty list [] on failure.
        
        Note on validation: Relies on save_settings to validate all fields.
        Note on core: Core extensions are never "installed" they are used to populate the global library and then installed under global settings.
        
        """
        _settings = self.user_settings
        _keys = _settings.childKeys()
        extension_types = ['user', 'global']
        if ext_type and str(ext_type) in extension_types:
            extension_types = [ext_type]
        saved = []
        for type_ in extension_types:
            ext_configs = self.extensions[type_].configs
            if not ext_configs:
                self.log.info(self.translate("logs", "No extensions of type {0} are currently loaded.".format(type_)))
                continue
            for _config in ext_configs:
                #Only install if not already installed in this section.
                if _config['name'] not in _keys:
                    #Attempt to save the extension.
                    if not self.save_settings(_config, type_):
                        self.log.warning(self.translate("logs", "Extension {0} could not be saved.".format(_config['name'])))
                    else:
                        saved.append(_config['name'])
        return saved

    def get_extension_from_property(self, key, val):
        """Takes a property and returns all INSTALLED extensions who have the passed value set under the passed property.

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
        matching_extensions = []
        if key not in self.config_keys:
            _error = self.translate("logs", "{0} is not a valid extension config value.".format(key))
            raise KeyError(_error)
        _settings = self.user_settings
        all_exts = _settings.childGroups()
        for current_extension in all_exts:
            #enter extension settings
            _settings.beginGroup(current_extension)
            if _settings.value(key) == val:
                matching_extensions.append(current_extension)
            #exit extension
            _settings.endGroup()
        if matching_extensions:
            return matching_extensions
        else:
            self.log.info(self.translate("logs", "No extensions had the requested value."))
            return []

    def get_property(self, name, key):
        """
        Get a property of an installed extension from the user settings.

        
        Args:
          name (string): The extension's name.
          key (string): The key of the value you are requesting from the extension.

        Returns:
          A the (string) value associated the extensions key in the applications saved extension settings.
        
        Raises:
          KeyError: If the value requested is non-standard.
        """
        if key not in self.config_keys:
            _error = self.translate("logs", "That is not a valid extension config value.")
            raise KeyError(_error)
        _settings = self.user_settings
        _settings.beginGroup(name)
        setting_value = _settings.value(key)
        if not setting_value:
            _error = self.translate("logs", "The extension config does not contain that value.")
            _settings.endGroup()
            raise KeyError(_error)
        else:
            _settings.endGroup()
            return setting_value

    def load_user_interface(self, extension_name, gui):
        """Return the graphical user interface (settings, main, toolbar) from an initialized extension.

        Args:
          extension_name (string): The extension to load
          gui (string): Name of a objects sub-section. (settings, main, or toolbar)

        Returns:
          The ( <UI Type> class) contained within the <extension_name> module.
        Raise:
          AttributeError: If an invalid gui type is requested or an uninitialized extension gui is requested.
        """
        if str(gui) not in ["settings", "main", "toolbar"]:
            self.log.debug(self.translate("logs", "{0} is not a supported user interface type.".format(str(gui))))
            raise AttributeError(self.translate("logs", "Attempted to get a user interface of an invalid type."))
        _config = self.get_config(extension_name)
        try:
            if _config['initialized'] != True:
                self.log.debug(self.translate("logs", "Extension manager attempted to load a user interface from uninitalized extension {0}. Uninitialized extensions cannot be loaded. Try installing/initalizing the extension first.".format(extension_name)))
                raise AttributeError(self.translate("logs", "Attempted to load a user interface from an uninitialized extension."))
        except KeyError:
            self.log.debug(self.translate("logs", "Extension manager attempted to load a user interface from uninitalized extension {0}. Uninitialized extensions cannot be loaded. Try installing/initalizing the extension first.".format(extension_name)))
            raise AttributeError(self.translate("logs", "Attempted to load a user interface from an uninitialized extension."))
        #Get ui file name and location of the extension from the settings.
        ui_file = _config[gui]
        _type = self.get_property(extension_name, "type")
        extension_path = os.path.join(self.libraries[_type], extension_name)
        #Get the extension 
        extension = zipimport.zipimporter(extension_path)
        #add extension to sys path so imported modules can access other modules in the extension.
        sys.path.append(extension_path)
        user_interface = extension.load_module(ui_file)
        if gui == "toolbar":
            return user_interface.ToolBar()
        elif gui == "main":
            return user_interface.ViewPort()
        elif gui == "settings":
            return user_interface.SettingsMenu()

    def get_config(self, name):
        """Returns a config from an installed extension.
                
        Args:
          name (string): An extension name.
        
        Returns:
          A config (dictionary) for an extension.
        
        Raises:
          KeyError: If an installed extension of the specified name does not exist.
        """
        config  = {}
        _settings = self.user_settings
        extensions  = _settings.childGroups()
        if name not in extensions:
            raise KeyError(self.translate("logs", "No installed extension with the name {0} exists.".format(name)))
        _settings.beginGroup(name)
        extension_config = _settings.childKeys()
        for key in extension_config:
            config[key] = _settings.value(key)
        _settings.endGroup()
        return config

    def remove_extension_settings(self, name):
        """Removes an extension and its core properties from the applications extension settings.

        @param name str the name of an extension to remove from the extension settings.
        """
#        WRITE_TESTS_FOR_ME()
#        FIX_ME_FOR_NEW_EXTENSION_TYPES()
        if len(str(name)) > 0:
            _settings = self.user_settings
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
        _settings = self.user_settings
        #get extension dir
        try:
            extension_dir = self.libraries[extension_type]
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
                _error = self.translate("logs", "The extension is missing a name value which is required.")
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
                if not config_validator.main():
                    _main = "main" #Set this for later default values
                    _settings.setValue("main", _main)
            else:
                _settings.setValue("main", _main)
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
                    _settings.setValue(val, _main)
                else:
                    _settings.setValue(val, _config_value)
            else:
                _error = self.translate("logs", "The config's {0} value is invalid and cannot be saved.".format(val))
                self.log.error(_error)
                return False
        #Extension Parent
        if config_validator.parent():
            try:
                _settings.setValue("parent", extension_config["parent"])
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "parent")))
                _settings.setValue("parent", "Extensions")
        else:
            _error = self.translate("logs", "The config's parent value is invalid and cannot be saved.")
            self.log.error(_error)
            return False

        #Extension Menu Item
        if config_validator.menu_item():
            try:
                _settings.setValue("menu_item", extension_config["menu_item"])
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_item")))
                _settings.setValue("menu_item", extension_name)
        else:
            _error = self.translate("logs", "The config's menu_item value is invalid and cannot be saved.")
            self.log.error(_error)
            return False
        #Extension Menu Level
        if config_validator.menu_level():
            try:
                _settings.setValue("menu_level", extension_config["menu_level"])
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_level")))
                _settings.setValue("menu_level", 10)
        else:
            _error = self.translate("logs", "The config's menu_level value is invalid and cannot be saved.")
            self.log.error(_error)
            return False
        #Extension Tests
        if config_validator.tests():
            try:
                _settings.setValue("tests", extension_config['tests'])
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "tests")))
                _settings.setValue("tests", "tests")
        else:
            _error = self.translate("logs", "Extension {0} does not contain the {1} file listed in the config for its tests. Please either remove the listing to allow for the default value, or add the appropriate file.".format(extension_config['name'], _config_value))
            self.log.error(_error)
            return False
        #Write extension type
        _settings.setValue("type", extension_type)
        _settings.setValue("initialized", True)
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
            files = unpacked.entryInfoList()
            for file_ in files:
                if file_.suffix() == ".conf":
                    config_name = file_.fileName()
                    config_path = file_.absolutePath()
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
    """A object for loading config data from a library.

    This object should only be used to load configs and saving/checking those values against the users settings. Any value checking should take place in the users settings.
    """

    def __init__(self, path=None):
        """
        Args:
          path (string): The path to an extension library.
        """
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        self.log.debug(self.translate("logs", "Initalizing ConfigManager"))
        self.configs = []
        self.directory = None
        self.paths = []
        if path:
            self.directory = path
            try:
                self.paths = self.get_paths(path)
            except TypeError:
                self.log.info(self.translate("logs", "No extensions found in the {0} directory".format(path)))
            else:
                self.log.info(self.translate("logs", "Extensions found in the {0} directory. Attempting to load extension configs.".format(path)))
                self.configs = list(self.get())

    def has_configs(self):
        """Provides the status of a ConfigManagers config files.
        
        Returns:
          bool: True, if there are configs. False, if there are no configs currently.
        """
        if self.configs:
            return True
        else:
            return False
            
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
        """Returns the paths to all extensions with config files within a directory.
        
        Args:
          directory (string): The path to the folder that extension's are within. Extensions can be up to one level below the directory given.
        
        Returns:
          config_files (array): An array of paths to all extension objects withj config files that were found.
        
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
                    if zipfile.is_zipfile(os.path.join(root, file_name)):
                        ext_zip = zipfile.ZipFile(os.path.join(root, file_name), 'r')
                        ext_names = ext_zip.namelist()
                        for member_name in ext_names:
                            if member_name.endswith(".conf"):
                                config_files.append(os.path.join(root, file_name))
        except AssertionError:
            self.log.warn(self.translate("logs", "Extension library at path {0} does not exist. No Config files identified.".format(path)))
            raise
        except TypeError:
            self.log.warn(self.translate("logs", "No extensions found at path {0}. No Config files identified.".format(path)))
            raise
        if config_files:
            return config_files
        else:
            raise TypeError(self.translate("logs", "No config files found at path {0}. No Config files loaded.".format(path)))

    def get(self, paths=None):
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
        config = None
        data = None
        myfile = QtCore.QFile(str(path))
        if not myfile.exists():
            return False
        if not zipfile.is_zipfile(str(path)):
            return False
        with zipfile.ZipFile(path, 'r') as zip_ext:
            for file_name in zip_ext.namelist():
                if file_name.endswith(".conf"):
                    config = zip_ext.read(file_name)
                    self.log.debug(self.translate("logs", "Config found in extension {0}.".format(path)))
        if config:
            try:
                data = json.loads(config.decode('utf-8'))
                self.log.info(self.translate("logs", "Successfully loaded {0}'s config file.".format(path)))
            except ValueError:
                self.log.warn(self.translate("logs", "Failed to load {0} due to a non-json or otherwise invalid file type".format(path)))
                return False
        if data:
            self.log.debug(self.translate("logs", "Config file loaded.".format(path)))
            return data
        else:
            self.log.debug(self.translate("logs", "Failed to load config file.".format(path)))
            return False
