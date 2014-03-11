#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
settings

The settings page for the extension template.

@brief The settings page for the extension. This page controls how the  extension level settings should look and behave in the settings menu. If this is not included in the config file and a "settings" class is not found in the file listed under the "main" option the extension will not list a settings button in the extension settings page.

@note This template ONLY includes the objects for the "settings" component of the extension template. The other components can be found in their respective locations.

"""

#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#import python modules created by qtDesigner and converted using pyuic4
from extensions.extension_template.ui import Ui_settings

class Settings(Ui_settings.ViewPort):
    """
    """

