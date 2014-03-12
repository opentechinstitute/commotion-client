#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main

An initial viewport template to make development easier.

@brief Populates the extensions initial view-port. This can be the same file as the settings and taskbar as long as that file contains seperate functions for each object type.

@note This template ONLY includes the objects for the "main" component of the extension template. The other components can be found in their respective locations.

"""

#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#import python modules created by qtDesigner and converted using pyuic4
from extensions.contrib.extension_template.ui import Ui_main

class ViewPort(Ui_main.ViewPort):
    """
    
    """
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)



