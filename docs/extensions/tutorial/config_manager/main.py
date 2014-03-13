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
#from extensions.core.config_manager.ui import Ui_config_manager.py
from docs.extensions.tutorial.config_manager.ui import Ui_config_manager.py

class ViewPort(Ui_main.ViewPort):
    """
    
    """

    start_report_collection = QtCore.pyqtSignal()
    data_report = QtCore.pyqtSignal(str, dict)
    error_report = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.start_report_collection.connect(self.send_signal)


    def send_signal(self):
        self.data_report.emit("myModule", {"value01":"value", "value02":"value", "value03":"value"})

    def send_error(self):
        self.error_report.emit("THIS IS AN ERROR MESSAGE!!!")

