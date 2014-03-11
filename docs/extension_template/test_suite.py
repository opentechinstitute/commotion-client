#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_suite

The test suite for the extension template.

"""

#Standard Library Imports
import sys
import unittest

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtTest import QtTest

#import python modules created by qtDesigner and converted using pyuic4
from extensions.extension_template import main
from extensions.extension_template import settings
from extensions.extension_template import task_bar

class MainTest(unittest.TestCase):
    """
    Test the main viewport object.
    """
    
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.task_bar = main.ViewPort()
        
class SettingsTest(unittest.TestCase):
    """
    Test the settings object.
    """
    
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.task_bar = settings.ViewPort()

class TaskBarTest(unittest.TestCase):
    """
    Test the task bar object
    """
    
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.task_bar = task_bar.TaskBar()

 if __name__ == "__main__":
     unittest.main()
