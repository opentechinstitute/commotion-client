#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MainWindow

The main window for the commotion_client pyqt GUI.
"""
#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#Commotion Client Imports
from assets import assets

class MainWindow(QtGui.QMainWindow):
    """
    The central widget for the commotion client. This widget initalizes all other sub-widgets and modules as well as defines the paramiters of the main GUI container.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.dirty = False #The variable to keep track of state for tracking if the gui needs any clean up.
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.
        

