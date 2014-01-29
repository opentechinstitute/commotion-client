#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MainWindow

The main window and system tray for the commotion_client pyqt GUI.

Key componenets handled within:
 * exiting/hiding the application
 * Creating the main window and systemTray icon.

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
        
        #set main menu to not close application on exit events (once set to true we will close on exit events.)
        self.exitOnClose = False
        self.tray = trayIcon()
        
        #connect to tray's exit event to allow application to close. 
        self.connect(self.tray.exit, QtCore.SIGNAL("triggered()"), self.exitEvent)

    def closeEvent(self, event):
        """
        Captures the close event for the main window. When called from exitEvent removes a trayIcon and accepts its demise. When called otherwise will simply hide the main window and ignore the event. 
        """
        if self.exitOnClose:
            self.log.debug(self.translate("logs", "Application has received a EXIT close event and will shutdown completely."))
            self.tray.trayIcon.hide()
            del self.tray.trayIcon
            event.accept()
        else:
            self.log.debug(self.translate("logs", "Application has received a non-exit close event and will hide its main window."))
            self.hide()
            event.setAccepted(True)
            event.ignore()

    def exitEvent(self):
        """
        Closes and exits the entire commotion program.
        """
        print("exit event triggered")
        self.exitOnClose = True
        self.close()

class trayIcon(QtGui.QWidget):
    """
    The Commotion tray icon. This icon object is the only object that can close the entire application. 
    """

    def __init__(self, parent=None):
        super().__init__()
        
        #Create actions for tray menu
        self.exit = QtGui.QAction(QtGui.QIcon(), "Exit", self)

        #set tray Icon and it's menu which allows closing from it.
        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon(":commotion_logo.png"), self)
        menu = QtGui.QMenu(self)
        menu.addAction(self.exit) #add exit action to tray icon
        self.trayIcon.setContextMenu(menu)
        self.trayIcon.activated.connect(self.trayIconActivated)
        self.trayIcon.show()

    def trayIconActivated(self, reason):
        """
        Defines the tray icon behavior on different types of interactions.
        """
        if reason == QtGui.QSystemTrayIcon.Context:
            self.trayIcon.contextMenu().show()
        elif reason == QtGui.QSystemTrayIcon.Trigger:
            self.show()
            self.raise_()
