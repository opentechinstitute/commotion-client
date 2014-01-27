#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commotion_client

The main python script for implementing the commotion_client GUI.

"""

import sys

from PyQt4 import QtCore
from PyQt4 import QtGui

from assets import assets
from utils import logger
from GUI.MainWindow import MainWindow

#==================================
# Startup Starts HERE
#==================================

#Enable Logging
logFile = "temp/logfile.temp" #TODO change the logfile to be grabbed from the commotion config reader

if "--debug" in sys.argv:
    del sys.argv[sys.argv.index("--debug")]
    logLevel = 5
else:
    logLevel = 2 #getConfig() #actually want to get this from commotion_config
log = logger.set_logging("commotion_client", logLevel, logFile)

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
app.setOrganizationName("The Open Technology Institute")
app.setOrganizationDomain("commotionwireless.net")
app.setApplicationName(app.translate("main", "Commotion Client")) #special translation case since we are outside of the main application
app.setWindowIcon(QtGui.QIcon(":commotion_logo.png"))
__version__ = "1.0"

#Start GUI
form = MainWindow()
form.show()
app.exec_()
log.debug(app.translate("logs", "Shutting down"))
