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

#PyQt imports
from PyQt4 import QtCore

#Commotion Client Imports
from utils import config
import extensions

class ExtensionManager():
    """   """
    def __init__(self, parent=None):
        self.log = logging.getLogger("commotion_client."+__name__)
        self.extensions = self.check_installed()


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

        
    def get(self, extension_name, subsection=None):
        """Return the full extension object or one of its primary sub-objects (settings or main)

        @subsection str Name of a objects sub-section. (settings or main)
        """
        config = config.find_configs("user", extension_name)
        if subsection:
            subsection = config[subsection]
        extension = self.import_extension(extension_name, subsection)
        if subsection:
            return extension.ViewPort()
        else:
            return extension

    def import_extension(self, extension_name, subsection=None):
        """load extensions by string name."""
        if subsection:
            extension = importlib.import_module("."+subsection, "extensions."+extension_name)
        else:
            extension = importlib.import_module("."+extension_name, "extensions")
        return extension

