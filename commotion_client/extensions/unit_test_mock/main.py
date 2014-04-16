#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main

A unit test extension. Not for production.

"""

#Standard Library Imports
import logging
import sys
#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#import python modules created by qtDesigner and converted using pyuic4
from ui import Ui_test

class ViewPort(Ui_test.ViewPort):
    """
    This is a mock extension and should not be used for ANYTHING user facing!
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
        """HI"""
        self.error_report.emit("THIS IS AN ERROR MESSAGE!!!")
        pass

    def is_loaded(self):
        return True


class SettingsMenu(Ui_test.ViewPort):
    """
    This is a mock extension and should not be used for ANYTHING user facing!
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
        """HI"""
        self.error_report.emit("THIS IS AN ERROR MESSAGE!!!")
        pass

    def is_loaded(self):
        return True
