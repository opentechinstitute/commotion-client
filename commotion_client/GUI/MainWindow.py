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
from GUI.MenuBar import MenuBar

class MainWindow(QtGui.QMainWindow):
    """
    The central widget for the commotion client. This widget initalizes all other sub-widgets and extensions as well as defines the paramiters of the main GUI container.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.dirty = False #The variable to keep track of state for tracking if the gui needs any clean up.
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.

        #Default Paramiters #TODO to be replaced with paramiters saved between instances later

        #set main menu to not close application on exit events
        self.exitOnClose = False
                
        #Set up menu bar.
        self.menuBar = MenuBar(self)

        #Create dock for menu-bar TEST
        self.menuDock = QtGui.QDockWidget(self)
        self.menuDock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.menuDock.setObjectName("MenuBarDock")
        self.menuDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.menuDock.setWidget(self.menuBar)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.menuDock)


        #set up viewport
        #self.viewport = Viewport(self)
        
        #Create slot to monitor when menu-bar wants the main window to change the main-viewport
        self.connect(self.menuBar, QtCore.SIGNAL("viewportRequested()"), self.changeViewport)
        
        #Create tray
        self.tray = trayIcon(self)
        #connect to tray events for closing application and showing main window.
        self.connect(self.tray.exit, QtCore.SIGNAL("triggered()"), self.exitEvent)
        self.connect(self.tray, QtCore.SIGNAL("showMainWindow"), self.bringFront)

    def changeViewport(self, viewport):
        self.log.debug(QtCore.QCoreApplication.translate("logs", "Request to change viewport received."))
        self.viewport.setViewport(viewport)

    def closeEvent(self, event):
        """
        Captures the close event for the main window. When called from exitEvent removes a trayIcon and accepts its demise. When called otherwise will simply hide the main window and ignore the event. 
        """
        if self.exitOnClose:
            self.log.debug(QtCore.QCoreApplication.translate("logs", "Application has received a EXIT close event and will shutdown completely."))
            self.tray.trayIcon.hide()
            del self.tray.trayIcon
            event.accept()
        else:
            self.log.debug(QtCore.QCoreApplication.translate("logs", "Application has received a non-exit close event and will hide its main window."))
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

    def bringFront(self):
        """
        Brings the main window to the front of the screen. 
        """
        self.show()
        self.raise_()


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
            self.emit(QtCore.SIGNAL("showMainWindow"))
