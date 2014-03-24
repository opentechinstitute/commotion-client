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

#PyQt imports
from PyQt4 import QtCore

#Commotion Client Imports
from utils import config
from utils import fs_utils
from utils import validate
import extensions

class ExtensionManager(object):
    def __init__(self):
        self.log = logging.getLogger("commotion_client."+__name__)
        self.extensions = self.check_installed()
        self.translate = QtCore.QCoreApplication.translate
        self.config_values = ["name",
                              "main",
                              "menu_item",
                              "menu_level",
                              "parent",
                              "settings",
                              "toolbar"]

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
        else if not name and installed_extensions:
            return True
        else:
            return False

    def load_all(self):
        ERRORS_HERE()
        
    @staticmethod
    def get_installed():
        """Get all installed extensions seperated by type.

        Pulls the current installed extensions from the application settings and returns a dictionary with the lists of the two extension types.

        Returns:
          A dictionary with two keys ['core' and 'contrib'] that both have lists of all extensions of that type as their values.

          {'core':['coreExtensionOne', 'coreExtensionTwo'],
           'contrib':['contribExtension', 'anotherContrib']}

        """
        installed_extensions = {}
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        _settings.beginGroup("core")
        core = _settings.allKeys()
        _settings.endGroup()
        _settings.beginGroup("contrib")
        contrib = _settings.allKeys()
        _settings.endGroup()
        _settings.endGroup()
        for ext in core:
            installed_extensions[ext] = "core"
        for ext in contrib:
            installed_extensions[ext] = "contrib"
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
        matching_extensions = []
        if value not in self.config_values:
            _error = self.translate("logs", "That is not a valid extension config value.")
            self.log.error(_error)
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
        if value not in self.config_values:
            _error = self.translate("logs", "That is not a valid extension config value.")
            self.log.error(_error)
            raise KeyError(_error)
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        ext_type = self.get_type(name)
        _settings.beginGroup(ext_type)
        _settings.beginGroup(name)
        setting_value = _settings.value(key)
        if setting_value.isNull():
            _error = self.translate("logs", "The extension config does not contain that value.")
            self.log.error(_error)
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
        if subsection:
            extension = importlib.import_module("."+subsection, "extensions."+extension_name)
        else:
            extension = importlib.import_module("."+extension_name, "extensions")
        return extension

    def load_settings(self, extension_name):
        """Gets an extension's settings and returns them as a dict.

        @return dict A dictionary containing an extensions properties.
        """
        extension_config = {"name":extension_name}
        extension_type = self.extensions[extension_name]
        
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        _settings.beginGroup(extension_type)
        extension_config['main'] = _settings.value("main").toString()
        #get extension dir
        main_ext_dir = os.path.join(QtCore.QtDir.current(), "extensions")
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type)
        extension_dir = QtCore.QtDir.mkpath(os.path.join(main_ext_type_dir, config['name']))
        extension_files = extension_dir.entryList()
        if not extension_config['main']:
            if "main.py" in extension_files:
                extension_config['main'] = "main"
            else:
                _error = self.translate("logs", "Extension {0} does not contain a \"main\" extension file. Please re-load or remove this extension.".format(extension_name))
                self.log.error(_error)
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
        if len(str(name)) > 0:
            _settings = QtCore.QSettings()
            _settings.beginGroup("extensions")
            _settings.remove(str(name))
        else:
            _error = self.translate("logs", "You must specify an extension name greater than 1 char.")
            self.log.error(_error)
            raise ValueError(_error)

    def save_settings(self, extension_config, extension_type="contrib"):
        """Saves an extensions core properties into the applications extension settings

        @param extension_type string Type of extension "contrib" or "core". Defaults to contrib.
        @param extension_config dict Dictionary of key-pairs for json config.
        @return bool True if successful and False on failures
        """
        _settings = QtCore.QSettings()
        _settings.beginGroup("extensions")
        #get extension dir
        main_ext_dir = os.path.join(QtCore.QtDir.current(), "extensions")
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type)
        extension_dir = QtCore.QtDir.mkpath(os.path.join(main_ext_type_dir, config['name']))
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
        _settings.endGroup()
        _settings.endGroup()
        return True

    def save_extension(self, extension, extension_type="contrib"):
        """Unpacks a extension and attempts to add it to the Commotion system.

        @param extension
        @param extension_type string Type of extension "contrib" or "core". Defaults to contrib.
        @return bool True if an extension was saved, False if it could not save.
        """
        #There can be only two... and I don't trust you.
        if extension_type != "contrib":
            extension_type = "core"
        try:
            unpacked = self.unpack_extension(self, extension, extension_type)
        except IOError:
            self.log.error(self.translate("logs", "Failed to unpack extension."))
            return False
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
                    config_name = _file
                    config_path = os.path.join(unpacked.absolutePath(), file_)
            _config = config.load_config(config_path)
            existing_extensions = config.find_configs("extension")
            try:
                assert _config['name'] not in existing_extensions
            except AssertionError:
                self.log.error(self.translate("logs", "The name given to this extension is already in use. Each extension must have a unique name."))
                self.log.info(self.translate("logs", "Cleaning extension's temp directory."))
                fs_utils.clean_dir(unpacked)
                return False
        else:
            self.log.error(self.translate("logs", "The extension name is invalid and cannot be saved."))
            self.log.info(self.translate("logs", "Cleaning extension's temp directory."))
            fs_utils.clean_dir(unpacked)
            return False
        #Check all values
        if not config_validator.validate_all():
            self.log.error(self.translate("logs", "The extension's config contains the following invalid value/s: [{0}]".format(",".join(config_validator.errors))))
            self.log.info(self.translate("logs", "Cleaning extension's temp directory."))
            fs_utils.clean_dir(unpacked)
            return False
        #make new directory in extensions
        main_ext_dir = os.path.join(QtCore.QtDir.current(), "extensions")
        main_ext_type_dir = os.path.join(main_ext_dir, extension_type)
        extension_dir = QtCore.QtDir.mkpath(os.path.join(main_ext_type_dir, _config['name']))
        try:
            fs_utils.copy_contents(unpacked, extension_dir)
        except IOError:
            self.log.error(self.translate("logs", "Could not move extension into main extensions directory from temporary storage. Please try again."))
            self.log.info(self.translate("logs", "Cleaning extension's temp and main directory."))
            fs_utils.clean_dir(extension_dir)
            fs_utils.clean_dir(unpacked)
            return False
        else:
            fs_utils.clean_dir(unpacked)
        try:
            self.save_settings(_config, extension_type)
        except KeyError:
            self.log.error(self.translate("logs", "Could not save the extension because it was missing manditory values. Please check the config and try again."))
            self.log.info(self.translate("logs", "Cleaning extension directory and settings."))
            fs_utils.clean_dir(extension_dir)
            self.remove_extension_settings(_config['name'])
            return False
        try:
            self.add_config(unpacked.absolutePath(), config_name)
        except IOError:
            self.log.error(self.translate("logs", "Could not add the config to the core config directory."))
            self.log.info(self.translate("logs", "Cleaning extension directory and settings."))
            fs_utils.clean_dir(extension_dir)
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
        data_dir = os.path.join(QtCore.QDir.current(), "data")
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
                log.info(_error)
                raise IOError(_error)
        return True

            
            
        

    def unpack_extension(self, compressed_extension):
        """Unpacks an extension into a temporary directory and returns the location.

        @param compressed_extension string Path to the compressed_extension
        @return QDir A QDir object containing the path to the temporary directory
        """
        temp_dir = fs_utils.make_temp_dir(new=True)
        temp_abs_path = temp_dir.absolutePath()
        try:
            shutil.unpack_archive(compressed_extension, temp_abs_path, "gztar")
        except ReadError:
            _error = QtCore.QCoreApplication.translate("logs", "Could not load Commotion extension because it was corrupted or mis-packaged.")
            self.log.error(_error)
            raise IOError(_error)
        except FileNotFoundError:
            _error = QtCore.QCoreApplication.translate("logs", "Could not load Commotion extension because it was not found.")
            self.log.error(_error)
            raise IOError(_error)
        return temp_dir

    def save_unpacked_extension(self, temp_dir, extension_name, extension_type):
        """Moves an extension from the temporary directory to the extension directory."""
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
            self.log.error(_error)
            raise ValueError(_error)

class InvalidSignature(Exception):
    """A verification procedure has failed.

    This exception should only be handled by halting the current task.
    """
    pass
