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
from GUI import welcome_page

class MainWindow(QtGui.QMainWindow):
    """
    The central widget for the commotion client. This widget initalizes all other sub-widgets and extensions as well as defines the paramiters of the main GUI container.
    """
    
    #Clean up signal atched by children to do any clean-up or saving needed
    clean_up = QtCore.pyqtSignal()
    app_message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        #Keep track of if the gui needs any clean up / saving.
        self._dirty = False
        self.log = logging.getLogger("commotion_client."+__name__)

        self.init_crash_reporter()
        self.setup_menu_bar()
        
        self.next_viewport = welcome_page.ViewPort(self)
        self.set_viewport()
        
        #Default Paramiters #TODO to be replaced with paramiters saved between instances later
        try:
            self.load_settings()
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Failed to load window settings."))
            self.log.exception(_excp)
            raise
        
        #set main menu to not close application on exit events
        self.exitOnClose = False
        self.remove_on_close = False

        #==================================        
        
    def toggle_menu_bar(self):
        #if menu shown... then
        #DockToHide = self.findChild(name="MenuBarDock")
        #QMainWindow.removeDockWidget (self, QDockWidget dockwidget)
        #else
        #bool QMainWindow.restoreDockWidget (self, QDockWidget dockwidget)
        pass

    def setup_menu_bar(self):
        """ Set up menu bar. """
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
        self.connect(self.menu_bar, QtCore.SIGNAL("viewportRequested()"), self.change_viewport)

    def init_crash_reporter(self):
        """ """
        try:
            self.crash_report = CrashReport()
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Failed to load crash reporter. Ironically, this means that the application must be halted."))
            self.log.exception(_excp)
            raise
        else:
            self.crash_report.crash.connect(self.crash)

    def set_viewport(self):
        """Set viewport to next viewport and load viewport """
        self.viewport = self.next_viewport
        self.load_viewport()

    def load_viewport(self):
        """Apply current viewport to the central widget and set up proper signal's for communication. """
        self.setCentralWidget(self.viewport)

        #connect viewport extension to crash reporter
        self.viewport.data_report.connect(self.crash_report.crash_info)
        self.crash_report.crash_override.connect(self.viewport.start_report_collection)
        
        #connect error reporter to crash reporter
        self.viewport.error_report.connect(self.crash_report.alert_user)

        #Attach clean up signal
        self.clean_up.connect(self.viewport.clean_up)

    def change_viewport(self, viewport):
        """Prepare next viewport for loading and start loading process when ready."""
        self.log.debug(QtCore.QCoreApplication.translate("logs", "Request to change viewport received."))
        self.next_viewport = viewport
        if self.viewport.is_dirty:
            self.viewport.on_stop.connect(self.set_viewport)
            self.clean_up.emit()
        else:
            self.set_viewport()

    def purge(self):
        """
        Closes the menu and sets its data up for immediate removal.
        """
        self.cleanup()
        self.main.remove_on_close = True
        self.close()


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
        self.cleanup()
        self.exitOnClose = True
        self.close()

    def cleanup(self):
        self.clean_up.emit() #send signal for others to clean up if they need to
        if self.is_dirty:
            self.save_settings()


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
            geometry = _settings.value("geometry", defaults['geometry']) 
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Could not load window geometry from settings file or defaults."))
            self.log.exception(_excp)
            raise
        _settings.endGroup()
        try:
            self.setGeometry(geometry)
        except Exception as _excp:
            self.log.critical(QtCore.QCoreApplication.translate("logs", "Cannot create GUI window."))
            self.log.exception(_excp)
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
            self.log.exception(_excp)
        _settings.endGroup()
        

    def crash(self, crash_type):
        """
        Emits a closing signal to allow other windows who need to clean up to clean up and then exits the application.
        """
        self.clean_up.emit() #send signal for others to clean up if they need to
        if crash_type == "restart":
            self.app_message.emit("restart")
        else:
            self.exitOnClose = True
            self.close()
            
    @property
    def is_dirty(self):
        """Get the current state of the main window"""
        return self._dirty

        
