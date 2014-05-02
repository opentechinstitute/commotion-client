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
import sys
#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui


from commotion_client.GUI import extension_toolbar

#import python modules created by qtDesigner and converted using pyuic4
#from extensions.core.config_manager.ui import Ui_config_manager.py
from ui import Ui_config_manager

class ViewPort(Ui_config_manager.ViewPort):
    """
    pineapple
    """

    start_report_collection = QtCore.pyqtSignal()
    data_report = QtCore.pyqtSignal(str, dict)
    error_report = QtCore.pyqtSignal(str)
    clean_up = QtCore.pyqtSignal()
    on_stop = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        self.setupUi(self)
        self.start_report_collection.connect(self.send_signal)
        self._dirty = False
        
    @property
    def is_dirty(self):
        """The current state of the viewport object """
        return self._dirty
        
    def clean_up(self):
        self.on_stop.emit()

    def send_signal(self):
        self.data_report.emit("myModule", {"value01":"value", "value02":"value", "value03":"value"})

    def send_error(self):
        """HI"""
        self.error_report.emit("THIS IS AN ERROR MESSAGE!!!")
        pass



class ToolBar(extension_toolbar.ExtensionToolBar):
    pass
