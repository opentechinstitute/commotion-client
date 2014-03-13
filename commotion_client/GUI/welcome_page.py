#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

welcome_page

The welcome page for the main window.

Key components handled within.
 * being pretty and welcoming to new users

"""

#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

from GUI.ui import Ui_welcome_page

class ViewPort(Ui_welcome_page.ViewPort):
    """
    """
    start_report_collection = QtCore.pyqtSignal()
    data_report = QtCore.pyqtSignal(str, dict)
    error_report = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__()
        self.log = logging.getLogger("commotion_client."+__name__)
        self.setupUi(self) #run setup function from Ui_main_window
