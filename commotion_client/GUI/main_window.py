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
from assets import commotion_assets_rc
from GUI.menu_bar import MenuBar
from GUI.crash_report import CrashReport


class MainWindow(QtGui.QMainWindow):
    """
    The central widget for the commotion client. This widget initalizes all other sub-widgets and extensions as well as defines the paramiters of the main GUI container.
    """
    
    #Closing Signal used by children to do any clean-up or saving needed
    closing = QtCore.pyqtSignal()
    app_message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.dirty = False #The variable to keep track of state for tracking if the gui needs any clean up.
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.

        try:
            self.crash_report = CrashReport()
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Failed to load crash reporter. Ironically, this means that the application must be halted."))
            self.log.debug(_excp, exc_info=1)
            raise
        else:
            self.crash_report.crash.connect(self.crash)
        
        #Default Paramiters #TODO to be replaced with paramiters saved between instances later
        try:
            self.load_settings()
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Failed to load window settings."))
            self.log.debug(_excp, exc_info=1)
            raise

        #set main menu to not close application on exit events
        self.exitOnClose = False
        self.remove_on_close = False



        #Set up Main Viewport
        #self.viewport = Viewport(self)


        #REMOVE THIS TEST CENTRAL WIDGET SECTION
        #==================================        
        from tests.extensions.test_ext001 import myMain
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setMinimumSize(600, 600)
        self.central_app = myMain.viewport(self)
        self.setCentralWidget(self.central_app)

        #connect central app to crash reporter
        self.central_app.data_report.connect(self.crash_report.crash_info)
        self.crash_report.crash_override.connect(self.central_app.start_report_collection)
        #connect error reporter to crash reporter
        self.central_app.error_report.connect(self.crash_report.alert_user)

        #==================================
        
        #Set up menu bar.
        self.menu_bar = MenuBar(self)
        
        #Create dock for menu-bar TEST
        self.menu_dock = QtGui.QDockWidget(self)
        #turn off title bar
        #TODO create a vertical title bar that is the "dock handle"
        self.menu_dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        #Set Name of dock so we can hide and show it.
        self.menu_dock.setObjectName("MenuBarDock")
        #force bar to the left side
        self.menu_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        #apply menu bar to dock and dock to the main window
        self.menu_dock.setWidget(self.menu_bar)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.menu_dock)

        #Create slot to monitor when menu-bar wants the main window to change the main-viewport
        self.connect(self.menu_bar, QtCore.SIGNAL("viewportRequested()"), self.changeViewport)
        
    def toggle_menu_bar(self):
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
            event.accept()
        elif self.remove_on_close:
            self.log.debug(QtCore.QCoreApplication.translate("logs", "Application has received a GUI closing close event and will close its main window."))
            self.deleteLater()
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
            self.save_settings()
        self.exitOnClose = True
        self.close()

    def bring_front(self):
        """
        Brings the main window to the front of the screen.
        """
        self.show()
        self.raise_()

    def load_settings(self):
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
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Could not load window geometry from settings file or defaults."))
            self.log.debug(_excp, exc_info=1)
            raise
        _settings.endGroup()
        try:
            self.setGeometry(geometry)
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Cannot create GUI window."))
            self.log.debug(_excp, exc_info=1)
            raise

    def save_settings(self):
        """
        Saves current window geometry
        """

        _settings = QtCore.QSettings()
        _settings.beginGroup("MainWindow")
        #Save settings
        try:
            _settings.setValue("geometry", self.geometry())
        except Exception as _excp:
            self.log.warn(QtCore.QCoreApplication.translate("logs", "Could not save window geometry. Will continue without saving window geometry."))
            self.log.debug(_excp, exc_info=1)
        _settings.endGroup()
        

    def crash(self, crash_type):
        """
        Emits a closing signal to allow other windows who need to clean up to clean up and then exits the application.
        """
        self.closing.emit() #send signal for others to clean up if they need to
        if crash_type == "restart":
            self.app_message.emit("restart")
        else:
            self.exitOnClose = True
            self.close()
        
