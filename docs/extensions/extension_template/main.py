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
    #Signals for data collection, reporting, and alerting on errors
    start_report_collection = QtCore.pyqtSignal()
    data_report = QtCore.pyqtSignal(str, dict)
    error_report = QtCore.pyqtSignal(str)
    on_stop = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self._dirty = False
        self.setupUi(self)
        self.start_report_collection.connect(self.send_signal)

    def send_signal(self):
        self.data_report.emit("myModule", {"value01":"value", "value02":"value", "value03":"value"})

    def send_error(self):
        self.error_report.emit("THIS IS AN ERROR MESSAGE!!!")

    @property
    def is_dirty(self):
        """The current state of the viewport object """
        return self.dirty
        
    def clean_up(self):
        self.on_stop.emit()
