#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main_window

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
from GUI.menu_bar import MenuBar
#from GUI.crash_report import CrashReport

class MainWindow(QtGui.QMainWindow):
    """
    The central widget for the commotion client. This widget initalizes all other sub-widgets and extensions as well as defines the paramiters of the main GUI container.
    """
    
    #Closing Signal used by children to do any clean-up or saving needed
    closing = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.dirty = False #The variable to keep track of state for tracking if the gui needs any clean up.
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.

        try:
            #self.crash_report() = CrashReport()
            pass
        except Exception as e:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Failed to load crash reporter. Ironically, this means that the application must be halted."))
            self.log.debug(e, exc_info=1)
            raise
        
        #Default Paramiters #TODO to be replaced with paramiters saved between instances later
        try:
            self.loadSettings()
        except Exception as e:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Failed to load window settings."))
            self.log.debug(e, exc_info=1)
            raise

        #set main menu to not close application on exit events
        self.exitOnClose = False


        #Set up Main Viewport
        #self.viewport = Viewport(self)


        #REMOVE THIS TEST CENTRAL WIDGET SECTION
        #==================================
        from tests.extensions.test_ext001 import myMain
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setMinimumSize(600,600)
        self.setCentralWidget(myMain.viewport(self))
        
        #==================================
        
        #Set up menu bar.
        self.menuBar = MenuBar(self)        
        
        #Create dock for menu-bar TEST
        self.menuDock = QtGui.QDockWidget(self)
        #turn off title bar
        #TODO create a vertical title bar that is the "dock handle"
        self.menuDock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        #Set Name of dock so we can hide and show it.
        self.menuDock.setObjectName("MenuBarDock")
        #force bar to the left side
        self.menuDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        #apply menu bar to dock and dock to the main window
        self.menuDock.setWidget(self.menuBar)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.menuDock)

        #Create slot to monitor when menu-bar wants the main window to change the main-viewport
        self.connect(self.menuBar, QtCore.SIGNAL("viewportRequested()"), self.changeViewport)
        
        #Create tray
        self.tray = trayIcon(self)
        #connect to tray events for closing application and showing main window.
        self.connect(self.tray.exit, QtCore.SIGNAL("triggered()"), self.exitEvent)
        self.connect(self.tray, QtCore.SIGNAL("showMainWindow"), self.bringFront)
        #crash("YOU NEED TO IMPLEMENT THE CRASHING FUNCTIONALITY HERE")

    def toggleMenuBar(self):
        #if menu shown... then
        #DockToHide = self.findChild(name="MenuBarDock")
        #QMainWindow.removeDockWidget (self, QDockWidget dockwidget)
        #else
        #bool QMainWindow.restoreDockWidget (self, QDockWidget dockwidget)
        pass

        
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
        self.closing.emit() #send signal for others to clean up if they need to
        if self.dirty:
            self.saveSettings()
        self.exitOnClose = True
        self.close()

    def bringFront(self):
        """
        Brings the main window to the front of the screen.
        """
        self.show()
        self.raise_()

    def loadSettings(self):
        """
        Loads window geometry from saved settings and sets window to those settings.
        """
        defaults = {
            #QRect(posX, posY, width, height)
            "geometry":QtCore.QRect(300, 300, 640, 480), #TODO set sane defaults and catalogue in HIG
        }

        _settings = QtCore.QSettings()
        _settings.beginGroup("MainWindow")

        #Load settings from saved, or use defaults
        try:
            geometry = _settings.value("geometry") or defaults['geometry']
        except Exception as e:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Could not load window geometry from settings file or defaults."))
            self.log.debug(e, exc_info=1)
            raise
        _settings.endGroup()
        try:
            self.setGeometry(geometry)
        except Exception as e:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Cannot create GUI window."))
            self.log.debug(e, exc_info=1)
            raise


    def saveSettings(self):
        """
        Saves current window geometry
        """

        _settings = QtCore.QSettings()
        _settings.beginGroup("MainWindow")
        #Save settings
        try:
            _settings.setValue("geometry", self.geometry())
        except Exception as e:
            self.log.warn(QtCore.QCoreApplication.translate("logs", "Could not save window geometry. Will continue without saving window geometry."))
            self.log.debug(e, exc_info=1)
        _settings.endGroup()
        

    def crash(self, msg):
        self.closing.emit() #send signal for others to clean up if they need to
        self.crash_report(msg)
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
            self.emit(QtCore.SIGNAL("showMainWindow"))
