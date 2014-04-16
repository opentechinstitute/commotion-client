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

    def reset_settings_group(self):
        """Resets the user_settings group to be at the top of the extensions group.

        Some functions modify the user_settings location to point at indiviudal extensions or other sub-groups. This function resets the settings to point at the top of the extensions group.

        NOTE: This should not be seen as a way to avoid doing clean up on functions you initiate. It is merely a way to ensure that on critical functions (deletions or modifications of existing settings) that errors do not cause data loss for users..
        """
        while self.user_settings.group():
            self.user_settings.endGroup()
        self.user_settings.beginGroup("extensions")
    
    def init_extension_libraries(self):
        """This function bootstraps the Commotion client when the settings are not populated on first boot or due to error. It iterates through all extensions in the core client and loads them."""
        
        #set default library paths
        self.set_library_defaults()
        #create directory structures if needed
        self.init_libraries()
        #load core and move to global if needed
        self.log.debug(self.libraries)
        self.load_core()
        #Load all extension configs found in libraries
        for name, path in self.libraries.items():
            self.log(path)
            self.log(QtCore.QDir(path).entryInfoList())
            if QtCore.QDir(path).entryInfoList() != []:
                self.init_extension_config(name)
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
        _app_path.cd("extensions")
        _app_path.cd("core")
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
                'global':os.path.join("extensions", "global"),
                'global_root' : QtCore.QDir(QtCore.QCoreApplication.applicationDirPath())}}
        for path_type in ['user', 'global']:
            ext_dir = platform_dirs[platform][path_type+'_root']
            ext_path = platform_dirs[platform][path_type]
            self.log.debug(self.translate("logs", "The root directory of {0} is {1}.".format(path_type, ext_dir.path())))
            #move the root directory to the correct sub-path.
            lib_path = ext_dir.filePath(ext_path)
            self.log.debug(self.translate("logs", "The extension directory has been set to {0}..".format(lib_path)))
            #Set the extension directory.
            self.libraries[path_type] = lib_path

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
                    self.log.debug(ext_dir.mkpath(ext_dir.absolutePath()))
                    self.log.debug(ext_dir.exists(ext_dir.absolutePath()))
                    raise IOError(self.translate("logs", "Could not create the extension library for {0}.".format(path_type)))
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
            try:
                self.log.debug(self.translate("logs", "Creating  {0} config manager".format(type_)))
                self.extensions[type_] = ConfigManager(self.libraries[type_])
            except ValueError:
                self.log.debug(self.translate("logs", "There were no extensions found for the {0} library.".format(type_)))
                continue
            except KeyError:
                self.log.debug(self.translate("logs", "There were no library path found for the {0} library.".format(type_)))
                continue
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
            try:
                ext_configs = self.extensions[type_].configs
            except KeyError: #Check if type has not been set yet
                self.log.info(self.translate("logs", "No extensions of type {0} are currently loaded.".format(type_)))
                continue
            if not ext_configs: #Check if the type has been created and then emptied
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
        
        long description
        
        Args:
          name (str): the name of an extension to remove from the extension settings.

        Returns:
          bool: True if extension is removed, false if it is not.
        
        Raises:
          ValueError: When an empty string is passed as an argument.
        """
        #make sure that a string of "" is not passed to this function because that would remove all keys.
        self.reset_settings_group()
        if len(str(name)) > 0:
            _settings = self.user_settings
            _settings.remove(str(name))
            return True
        else:
            self.log.debug(self.translate("logs", "A zero length string was passed as the name of an extension to be removed. This would delete all the extensions if it was allowed to succeed."))
            raise ValueError(self.translate("logs", "You must specify an extension name greater than 1 char."))
        return False

    def save_settings(self, extension_config, extension_type="global"):
        """Saves an extensions core properties into the applications extension settings.
        
        long description
        
        Args:
          extension_config (dict) An extension config in dictionary format.
          extension_type (string): Type of extension "user" or "global". Defaults to global.
        
        Returns:
          bool: True if successful, False on any failures
        """
        _settings = self.user_settings
        #get extension dir
        try:
            extension_dir = self.libraries[extension_type]
        except KeyError:
            self.log.warning(self.translate("logs", "Invalid extension type. Please check the extension type and try again."))
            return False
        #create validator
        try:
            config_validator = validate.ClientConfig(extension_config, extension_dir)
        except KeyError as _excp:
            self.log.warning(self.translate("logs", "The extension is missing a name value which is required."))
            self.log.debug(_excp)
            return False
        except FileNotFoundError as _excp:
            self.log.warning(self.translate("logs", "The extension was not found on the system and therefore cannot be saved."))
            self.log.debug(_excp)
            return False
        #Extension Name
        try:
            extension_name = extension_config['name']
            if config_validator.name():
                _settings.beginGroup(extension_name)
                _settings.setValue("name", extension_name)
            else:
                _error = self.translate("logs", "The extension's name is invalid and cannot be saved.")
                self.log.error(_error)
                return False
        except KeyError:
            _error = self.translate("logs", "The extension is missing a name value which is required.")
            self.log.error(_error)
            return False
        #Extension Main
        try:
            _main = extension_config['main']
            if not config_validator.gui(_main):
                _error = self.translate("logs", "The config's main value is invalid and cannot be saved.")
                self.log.error(_error)
                return False
        except KeyError:
            _main = "main" #Set this for later default values
            if not config_validator.gui(_main):
                _settings.setValue("main", _main)
        else:
            _settings.setValue("main", _main)
        #Extension Settings & Toolbar
        for val in ["settings", "toolbar"]:
            try:
                _config_value = extension_config[val]
                if not config_validator.gui(val):
                    _error = self.translate("logs", "The config's {0} value is invalid and cannot be saved.".format(val))
                    self.log.error(_error)
                    return False
            except KeyError:
                #Defaults to main, which was checked and set before
                _settings.setValue(val, _main)
            else:
                _settings.setValue(val, _config_value)
        #Extension Parent
        try:
            _parent = extension_config["parent"]
            if config_validator.parent():
                _settings.setValue("parent", _parent)
            else:
                _error = self.translate("logs", "The config's parent value is invalid and cannot be saved.")
                self.log.error(_error)
                return False
        except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "parent")))
            _settings.setValue("parent", "Extensions")
        #Extension Menu Item
        try:
            _menu_item = extension_config["menu_item"]
            if config_validator.menu_item():
                _settings.setValue("menu_item", _menu_item)
            else:
                _error = self.translate("logs", "The config's menu_item value is invalid and cannot be saved.")
                self.log.error(_error)
                return False
        except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_item")))
            _settings.setValue("menu_item", extension_name)
        #Extension Menu Level
        try:
            _menu_level = extension_config["menu_level"]
            if config_validator.menu_level():
                _settings.setValue("menu_level", _menu_level)
            else:
                _error = self.translate("logs", "The config's menu_level value is invalid and cannot be saved.")
                self.log.error(_error)
                return False
        except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "menu_level")))
            _settings.setValue("menu_level", 10)
        #Extension Tests
        try:
            _tests = extension_config['tests']
            if config_validator.tests():
                _settings.setValue("tests", _tests)
            else:
                _error = self.translate("logs", "Extension {0} does not contain the {1} file listed in the config for its tests. Please either remove the listing to allow for the default value, or add the appropriate file.".format(extension_name, _config_value))
                self.log.error(_error)
                return False
        except KeyError:
            self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(extension_name, "tests")))
            _settings.setValue("tests", "tests")
        #Write extension type
        _settings.setValue("type", extension_type)
        _settings.setValue("initialized", True)
        _settings.endGroup()
        return True

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
                self.log.debug(self.translate("logs", "No extensions found in the {0} directory. You must first populate the folder with extensions to init a ConfigManager in that folder. You can create a ConfigManager without a location specified, but you will have to add extensions before getting paths.".format(path)))
                raise ValueError(self.translate("logs", "The path {0} is empty. ConfigManager could not be created".format(path)))
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
            self.log.warning(self.translate("logs", "No configs have been loaded. Please load configs first.".format(name)))
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
          config_files (array): An array of paths to all extension objects with config files that were found.
        
        Raises:
          TypeError: If no extensions exist within the directory requested.
          AssertionError: If the directory path does not exist.
        
        """
        #Check the directory and raise value error if not there
        dir_obj = QtCore.QDir(str(directory))
        if not dir_obj.exists(dir_obj.absolutePath()):
            raise ValueError(self.translate("logs", "Folder at path {0} does not exist. No Config files loaded.".format(str(directory))))
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
            self.log.debug(self.translate("logs", "No paths found. Attempting to load all extension manager paths list."))
            paths = self.paths
            self.log.debug(self.translate("logs", "Found paths:{0}.".format(paths)))
        for path in paths:
            if fs_utils.is_file(path):
                config = self.load(path)
                if config:
                    yield config
            else:
                self.log.warning(self.translate("logs", "Config file {0} does not exist and therefore cannot be loaded.".format(path)))

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
                self.log.warning(self.translate("logs", "Failed to load {0} due to a non-json or otherwise invalid file type".format(path)))
                return False
        if data:
            self.log.debug(self.translate("logs", "Config file loaded.".format(path)))
            return data
        else:
            self.log.debug(self.translate("logs", "Failed to load config file.".format(path)))
            return False
