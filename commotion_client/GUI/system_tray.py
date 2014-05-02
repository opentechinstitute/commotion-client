#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#Commotion Client Imports
import commotion_assets_rc

class TrayIcon(QtGui.QWidget):
    """
    The Commotion tray icon. This icon object is the only object that can close the entire application.
    """
    show_main = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__()
        self.log = logging.getLogger("commotion_client."+__name__) #TODO stop hard_coding commotion_ client
        #Create actions for tray menu
        self.exit = QtGui.QAction(QtGui.QIcon(), "Exit", self)
        #set tray Icon and it's menu which allows closing from it.
        self.tray_icon = QtGui.QSystemTrayIcon(QtGui.QIcon(":logo32.png"), self)
        menu = QtGui.QMenu(self)
        menu.addAction(self.exit) #add exit action to tray icon
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_iconActivated)
        self.tray_icon.show()

    def tray_iconActivated(self, reason):
        """
        Defines the tray icon behavior on different types of interactions.
        """
        if reason == QtGui.QSystemTrayIcon.Context:
            self.tray_icon.contextMenu().show()
        elif reason == QtGui.QSystemTrayIcon.Trigger:
            self.show_main.emit()
