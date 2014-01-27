#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commotion_client

The main python script for implementing the commotion_client GUI.

"""

import sys

from PyQt4 import QtCore
from PyQt4 import QtGui


class MainWindow(QtGui.QMainWindow):
    """
    The central widget for the commotion client. This widget initalizes all other sub-widgets and modules as well as defines the paramiters of the main GUI container.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.dirty = False #The variable to keep track of state for tracking if the gui needs any clean up.
        
        



#==================================
# Main Applicaiton Creator
#==================================

app = QtGui.QApplication(sys.argv)

#Enable Translations
locale = QtCore.QLocale.system().name()
qtTranslator = QtCore.QTranslator()
if qtTranslator.load("qt_"+locale, ":/"):
    app.installTranslator(qtTranslator)
    appTranslator = QtCore.QTranslator()
    if appTranslator.load("imagechanger_"+locale, ":/"):
        app.installTranslator(appTranslator)

#Set Application and Organization Information
app.setOrganizationName("Open Technology Institute")
app.setOrganizationDomain("commotionwireless.net")
app.setApplicationName(app.translate("main", "Commotion Client")) #special translation case since we are outside of the main application
app.setWindowIcon(QtGui.QIcon(":/assets/images/commotion_logo.png"))
__version__ = "1.0"

#Start GUI 
form = MainWindow()
form.show()
app.exec_()
